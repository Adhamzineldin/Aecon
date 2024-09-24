import requests
import json
import datetime
from zeep import Client,helpers
from django.contrib.sessions.backends.db import SessionStore 
from django.contrib.sessions.models import Session
import dateutil


class APIError(Exception):
    pass


class APIAuthorisationError(APIError):
    pass


class APIDataRetrievalError(APIError):
    pass


#######################################################################################################
#
#
# NEW Vivacity API
#
#
#######################################################################################################
def check_create_session_auth_token(flg="check",token=None):
    if flg == "check":
        print("token checking")
        session = Session.objects.all()
        chk_flg = 0
        
        if len(session):
            for s in session:
                ssn = SessionStore(session_key=s.pk)
                if  ssn.get('auth_token') is not None:
                    chk_flg = 1
                    time_diff =  datetime.datetime.now() - dateutil.parser.parse(ssn['auth_token']['time'])  
                    time_diff = time_diff.total_seconds()
                    time_diff = round(time_diff/60)

                    if time_diff > 14:
                        print("token Expired -",ssn['auth_token']['time'])
                        s.delete()
                        return None
                    else: 
                        print("token returned - ",ssn['auth_token']['time'])
                        return ssn['auth_token']['token']
            if chk_flg == 0 :
                return None
        else:
            return None
    elif flg == "create" and token is not None:
        s  = SessionStore()
        s['auth_token'] = {'token':token,"time":str(datetime.datetime.now())}
        s.save()
        print("token created")
        

def get_vivacity_auth_token(username,password):
    try:
        token = check_create_session_auth_token(flg="check")
        if token is None:
            response = requests.post("https://api.vivacitylabs.com/get-token",
                                    data={"username": username, "password": password})
            if response.status_code == 401:
                raise APIAuthorisationError("Invalid Auth details")
            if response.status_code == 429:
                raise APIAuthorisationError("Too many failed attempts")
            if response.status_code == 500:
                raise APIAuthorisationError("Internal Server Error")
            try:
                result = json.loads(response.text)
                # print(result)
            except Exception as e:
                raise APIDataRetrievalError("Json decode error" + str(e))
            check_create_session_auth_token(flg="create",token=result["access_token"])
            token = result["access_token"]
        return token
    except KeyError as e:
        raise APIAuthorisationError("No token returned")
    except requests.exceptions.ConnectionError as e:
        raise APIDataRetrievalError("No response from Vivacity API " + str(e))


def get_vivacity_data(token,startDate,endDate,countlines):
    params = {"timeFrom": startDate.strftime("%Y-%m-%dT%H:%M:%S.000Z"),"countline":countlines,
              "timeTo": endDate.strftime("%Y-%m-%dT%H:%M:%S.000Z"),"includeZeroCounts":True}
    headers = {"Authorization":"Bearer " + str(token)}
    try:
        response = requests.get("https://api.vivacitylabs.com/counts", params=params, headers=headers)

    except requests.exceptions.ConnectionError as e:
        raise APIDataRetrievalError("No response from Vivacity API " + str(e))
    print("request was", response.request.url)
    if response.status_code == 401:
        raise APIAuthorisationError("Invalid Auth details")
    if response.status_code == 400:
        raise APIDataRetrievalError("Bad Request")
    if response.status_code == 500:
        raise APIDataRetrievalError("Internal Server Error")
    if response.status_code == 403:
        raise APIDataRetrievalError("Forbidden")
    if response.status_code == 404:
        raise APIDataRetrievalError("Not Found")
    try:
        result = json.loads(response.text)
        # print(result)
    except Exception as e:
        raise APIDataRetrievalError("Json decode error" + str(e))
    #for item in result:
    #    print(item)
    return result


def get_vivacity_sensors(token):
    headers = {"Authorization": "Bearer " + str(token)}
    response = requests.get("https://api.vivacitylabs.com/sensor", headers=headers)
    if response.status_code == 401:
        raise APIAuthorisationError("Invalid Auth details")
    if response.status_code == 400:
        raise APIDataRetrievalError("Bad Request")
    if response.status_code == 500:
        raise APIDataRetrievalError("Internal Server Error")
    if response.status_code == 403:
        raise APIDataRetrievalError("Forbidden")
    if response.status_code == 404:
        raise APIDataRetrievalError("Not Found")
    try:
        result = json.loads(response.text)
    except Exception as e:
        raise APIDataRetrievalError("Json decode error" + str(e))
    return result


def get_vivacity_countlines(countlines,token):
    headers = {"Authorization": "Bearer " + str(token)}
    params={"countLineid":countlines}
    response = requests.get("https://api.vivacitylabs.com/countline", headers=headers,params=params)
    if response.status_code == 401:
        raise APIAuthorisationError("Invalid Auth details")
    if response.status_code == 400:
        raise APIDataRetrievalError("Bad Request")
    if response.status_code == 500:
        raise APIDataRetrievalError("Internal Server Error")
    if response.status_code == 403:
        raise APIDataRetrievalError("Forbidden")
    if response.status_code == 404:
        raise APIDataRetrievalError("Not Found")
    try:
        result = json.loads(response.text)
    except Exception as e:
        raise APIDataRetrievalError("Json decode error" + str(e))
    return result


#######################################################################################################
#
#
# Turning Counts Vivacity API
#
#
#######################################################################################################
def get_turning_counts_data(api_key:str, start_zone:int, end_zone:int, start_date:datetime, end_date:datetime):
    params = {"start_zone_ids": start_zone, 
              "end_zone_ids": end_zone, 
              "from": start_date.strftime("%Y-%m-%dT%H:%M:%S.000Z"), 
              "to": end_date.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
              "time_bucket" : "5m"
              }
    response = requests.get("https://api.vivacitylabs.com/zone/turning_movements", params=params,
                            headers={"x-vivacity-api-key": api_key})
    
    if response.status_code == 401:
        raise APIAuthorisationError("Invalid Auth details")
    if response.status_code == 400:
        raise APIDataRetrievalError("Bad Request")
    if response.status_code == 500:
        raise APIDataRetrievalError("Internal Server Error")
    if response.status_code == 403:
        raise APIDataRetrievalError("Forbidden")
    if response.status_code == 404:
        raise APIDataRetrievalError("Not Found")
    try:
        result = json.loads(response.text)
    except Exception as e:
        raise APIDataRetrievalError("Json decode error" + str(e))
    return result

#######################################################################################################
#
#
# Clearview Intelligence API
#
#
#######################################################################################################



def get_token(username,password):
    response = requests.get("https://www.gateway.insighthub.io/customer-api/v1/auth",params={"username":username,"password":password})
    if response.status_code == 401:
        raise APIAuthorisationError("Invalid Auth details")
    if response.status_code == 429:
        raise APIAuthorisationError("Too many failed attempts")
    result = json.loads(response.text)

    try:
        token = result["token"]
        return token
    except KeyError as e:
        raise APIAuthorisationError("No token returned")


def get_vehicle_data(deviceId,startDate,endDate,token):
    params = {"timeFrom":startDate.strftime("%Y-%m-%dT%H:%M:%S+00:00Z"),"timeTo":endDate.strftime("%Y-%m-%dT%H:%M:%S+00:00Z")}

    headers = {"CVT-Insight-Authentication":token}
    response = requests.get("https://www.gateway.insighthub.io/customer-api/v1/devices/" + str(deviceId) + "/vehicle-data",
                            headers=headers,params=params)
    print(response.status_code)
    print(response.text)



def get_devices(token):

    headers = {"CVT-Insight-Authentication":token}
    response = requests.get("https://www.gateway.insighthub.io/customer-api/v1/devices",
                            headers=headers)
    print(response.status_code)
    print(response.text)




#######################################################################################################
#
#
# Vivacity API
#
#
#######################################################################################################


def get_historic_vivacity_data(url,key,startDate,endDate):
    url = url + "from=" + str(int(startDate.timestamp())) + "&to=" + str(int(endDate.timestamp())) + "&apikey=" + key
    print("url is",url)
    response = requests.get(url)
    if response.status_code == 401:
        raise APIAuthorisationError("Invalid Auth details")
    if response.status_code == 400:
        raise APIDataRetrievalError("Bad Request")
    if response.status_code == 500:
        raise APIDataRetrievalError("Internal Server Error")
    if response.status_code == 403:
        raise APIDataRetrievalError("Forbidden")
    if response.status_code == 404:
        raise APIDataRetrievalError("Not Found")
    try:
        result = json.loads(response.text)
    except Exception as e:
        raise APIDataRetrievalError("Json decode error" + str(e))
    return result


#######################################################################################################
#
#
# London Breath API
#
#
#######################################################################################################

def get_london_breath_data():
    url = "https://api.breathelondon.org/api/ListSensors?key=e2635276-e87a-11eb-9a03-0242ac130003"
    data = requests.get(url)
    return (json.loads(data.text))[0]

def get_london_breath_data_sitecode(key,obsClass,start_date,end_date):
    url = 'https://api.breathelondon.org/api/getClarityData/'+str(key)+'/I'+obsClass+'/'+str(start_date)+'/'+str(end_date)+'/Hourly?key=e2635276-e87a-11eb-9a03-0242ac130003'
    data = requests.get(url)
    return data.json()
    

#######################################################################################################
#
#
# Envirowatch API
#
#
#######################################################################################################


#envirowatchClient = Client('http://api-tracsis.envirowatch.ltd.uk/moteservice.asmx?WSDL')
def get_client():
    envirowatchClient = Client('http://api-tracsis.envirowatch.ltd.uk/moteservice.asmx?WSDL')
    return envirowatchClient


def get_envirowatch_token():
    envirowatchClient = get_client()
    loginResult = envirowatchClient.service.Login(emailAddress="Neil.Watson@Tracsis.com",password="bastardo1")
    if "LoginResult" in loginResult:
        if "ResponseType" in loginResult["LoginResult"]:
            if loginResult["LoginResult"]["ResponseType"] == "AuthFail":
                return None
            else:
                return loginResult["token"]
    return None


def get_envirowatch_motes(token):
    envirowatchClient = get_client()
    result = envirowatchClient.service.GetMotes(token)
    if "GetMotesResult" in result:
        if "ResponseType" in result["GetMotesResult"]:
            if result["GetMotesResult"]["ResponseType"] == "Success":
                return result["motes"]["Mote"]
    return []


def get_envirowatch_data(token):
    envirowatchClient = get_client()
    result = envirowatchClient.service.GetLatest(token)
    if "GetLatestResult" in result:
        if "ResponseType" in result["GetLatestResult"] and result["GetLatestResult"]["ResponseType"] == "Success":
            return result["moteDataSets"]["MoteDataSet"]


#######################################################################################################
#
#
# TFWM API
#
#
#######################################################################################################

def get_TFWM_token(username,password):
    url = "https://net.ca-traffic.com/Token"
    data = requests.post(url,data={"username": username, "password": password,"grant_type": "password"})
    result = json.loads(data.text)
    return result["access_token"]


def get_TFWM_sites(token):
    headers = {"Authorization": "Bearer " + str(token)}
    try:
        response = requests.get("https://net.ca-traffic.com/api/SiteList/VDAPro-TransportForWestMids/All/NULL/1970-1-1/1970-1-1",  headers=headers)
        print("request was", response.request.url)
        print("response",response)
        if response.status_code == 401:
            raise APIAuthorisationError("Invalid Auth details")
        if response.status_code == 400:
            raise APIDataRetrievalError("Bad Request")
        if response.status_code == 500:
            raise APIDataRetrievalError("Internal Server Error")
        if response.status_code == 403:
            raise APIDataRetrievalError("Forbidden")
        if response.status_code == 404:
            raise APIDataRetrievalError("Not Found")
    except requests.exceptions.ConnectionError as e:
        raise APIDataRetrievalError("No response from TFWM API " + str(e))
    try:
        result = json.loads(response.text)
    except Exception as e:
        raise APIDataRetrievalError("Json decode error" + str(e))
    return result


def get_TFWM_data(token, site, startDate, endDate):
    headers = {"Authorization": "Bearer " + str(token)}
    try:
        url = "https://net.ca-traffic.com/api/FlowData/VDAPro-TransportForWestMids/" + site
        url += "/" + startDate.strftime("%Y-%m-%d") + "/" + endDate.strftime("%Y-%m-%d") + "/15"
        print(url)
        response = requests.get(url,  headers=headers)
        print("request was", response.request.url)
        print("response",response)
        if response.status_code == 401:
            raise APIAuthorisationError("Invalid Auth details")
        if response.status_code == 400:
            raise APIDataRetrievalError("Bad Request")
        if response.status_code == 500:
            raise APIDataRetrievalError("Internal Server Error")
        if response.status_code == 403:
            raise APIDataRetrievalError("Forbidden")
        if response.status_code == 404:
            raise APIDataRetrievalError("Not Found")
    except requests.exceptions.ConnectionError as e:
        raise APIDataRetrievalError("No response from TFWM API " + str(e))
    try:
        result = json.loads(response.text)
    except Exception as e:
        raise APIDataRetrievalError("Json decode error" + str(e))
    return result


#######################################################################################################
#
#
# Openweathermap API
#
#
#######################################################################################################


def get_weather_data(lat,lon,d,apiKey):
    url = "http://api.openweathermap.org/data/2.5/onecall/timemachine?lat=" + str(lat) + "&lon=" + str(lon)
    url += "&appid="+ str(apiKey) + "&units=metric&dt=" + str(int(d.timestamp()))
    try:
        response = requests.get(url)
        print("request was", response.request.url)
        print("response",response)
        if response.status_code == 401:
            raise APIAuthorisationError("Invalid Auth details")
        if response.status_code == 400:
            raise APIDataRetrievalError("Bad Request")
        if response.status_code == 500:
            raise APIDataRetrievalError("Internal Server Error")
        if response.status_code == 403:
            raise APIDataRetrievalError("Forbidden")
        if response.status_code == 404:
            raise APIDataRetrievalError("Not Found")
    except requests.exceptions.ConnectionError as e:
        raise APIDataRetrievalError("No response from Weather API " + str(e))
    try:
        result = json.loads(response.text)
    except Exception as e:
        raise APIDataRetrievalError("Json decode error" + str(e))
    return result


def process_weather_data(result):
    import pandas as pd
    tz = result["timezone"]
    df = pd.DataFrame.from_records(result["hourly"])
    df["dt"] = df["dt"].apply(lambda x: datetime.datetime.fromtimestamp(x))
    df.to_csv("weather output.csv")


#######################################################################################################
#
#
# Q-Free API for cheshire cycle counters
#
#
#######################################################################################################

def get_QFREE_data(token, siteId, classification, direction,  startDate, endDate):
    url = "https://api-infoqus.q-freehub.com/api/v1/Reporting/CrossingCount?siteIds=" + str(siteId) + "&interval=hour&fromDate="
    url += startDate.strftime("%Y-%m-%d") + "&toDate=" + endDate.strftime("%Y-%m-%d")
    url += "&directions=" + direction + "&classes=" + classification
    print("url is", url)
    #url = "https://api-infoqus.q-freehub.com/api/v1/Reporting/CrossingCount?fromDate=2020-10-01&toDate=2020-10-01&interval=hour&classes=Bicycle&directions=NorthBound&siteIds=257"
    #print("url is", url)
    headers = {"Authorization": "Bearer " + token}
    try:
        response = requests.get(url, headers=headers)
        print("status code", response.status_code)
        if response.status_code == 401:
            raise APIAuthorisationError("Invalid Auth details")
        if response.status_code == 400:
            raise APIDataRetrievalError("Bad Request")
        if response.status_code == 500:
            raise APIDataRetrievalError("Internal Server Error")
        if response.status_code == 403:
            raise APIDataRetrievalError("Forbidden")
        if response.status_code == 404:
            raise APIDataRetrievalError("Not Found")
        return response.json()
    except requests.exceptions.ConnectionError as e:
        raise APIDataRetrievalError("No response from Q-Free API " + str(e))


def get_QFREE_sites(token,id=None):
    url = "https://api-infoqus.q-freehub.com/api/v1/sites"
    if id:
        url += "/" + str(id)
    headers = {"Authorization": "Bearer " + token}
    try:
        response = requests.get(url, headers=headers)
        print(response.status_code)
        if response.status_code == 401:
            raise APIAuthorisationError("Invalid Auth details")
        if response.status_code == 400:
            raise APIDataRetrievalError("Bad Request")
        if response.status_code == 500:
            raise APIDataRetrievalError("Internal Server Error")
        if response.status_code == 403:
            raise APIDataRetrievalError("Forbidden")
        if response.status_code == 404:
            raise APIDataRetrievalError("Not Found")
        return response.json()
    except requests.exceptions.ConnectionError as e:
        raise APIDataRetrievalError("No response from Q-Free API " + str(e))


def get_QFREE_token(apiId, apiSecret):
    data = {"client_id": apiId, "client_secret": apiSecret, "audience": "urn:q-freehub-api", "grant_type": "client_credentials"}
    url = "https://api-identity.q-freehub.com/oauth/token"
    try:
        response = requests.post(url,json=data)
        print(response.status_code)
        if response.status_code == 401:
            raise APIAuthorisationError("Invalid Auth details")
        if response.status_code == 400:
            raise APIDataRetrievalError("Bad Request")
        if response.status_code == 500:
            raise APIDataRetrievalError("Internal Server Error")
        if response.status_code == 403:
            raise APIDataRetrievalError("Forbidden")
        if response.status_code == 404:
            raise APIDataRetrievalError("Not Found")
        token = response.json()["access_token"]
        return token
    except KeyError as e:
        raise APIAuthorisationError("No token returned")
    except requests.exceptions.ConnectionError as e:
        raise APIDataRetrievalError("No response from Vivacity API " + str(e))


syncAPI = ["tracsis-syncronicity-api-user","hrfG;97V"]
tracsisAPI = ["tcp-api-user","\9Gf-2D>"]
TFWMAPI = ["neil.watson@tracsis.com","Tracsis12345"]
SLPAPI = ["tracsis-slp-AQ-user", "5<AaD*>k"]

siteList = ["CY49","CY48","CY73","CY91","CY81","CY46","CY82","CY90","CY12","CY47","CY102","CY100","CY85","CY101","CY84","CY86"]


if __name__ == "__main__":
    s = datetime.datetime(2020, 11, 7, 15)

    #token = get_envirowatch_token()
    #data = get_envirowatch_data(token)
    #print(data)
    #exit()




    if True:
        s = datetime.datetime(2021, 7, 11, 5, 0)
        e = datetime.datetime(2021,7, 11, 6, 0)
        token = get_vivacity_auth_token(*tracsisAPI)
        result = get_vivacity_sensors(token)
        for item in result:
            print(item)
        #exit()
        result = get_vivacity_countlines([],token)
        for item in result:
            print(item)
        #exit()
        result = get_vivacity_data(token,s,e,[16189])
        print(result)
        for _,val in result.items():
            for _,data in val.items():
                for item in data["counts"]:
                    print(item)
        exit()

    #token = get_TFWM_token(*TFWMAPI)
    #print("token is", token)
    startDate = datetime.datetime(2021,2,16,10)
    endDate = datetime.datetime(2021,2,16,11)

    #data = get_TFWM_data(token,"f34a7f23-a2cc-402c-89c9-90d188ba0230",startDate,endDate)
    #print(data)
    #exit()
    #data = get_TFWM_sites(token)

    #for site in data["properties"]:
    #    if site["SiteReference"] in siteList:
    #        print(site)

    #exit()



    t = datetime.datetime(2021, 4, 16, 8, 0)
    t1 = t.replace(microsecond=0) - datetime.timedelta(hours=1)
    t2 = t.replace(microsecond=0)
    #exit()
    if False:
        try:
            token = get_vivacity_auth_token(*tracsisAPI)
            data = get_vivacity_data(token, t1, t2, ["13541", "929"])
            with open("example api data.json", "w") as f:
                json.dump(data, f)
            print(data)
            print("found data for", t.date)
            exit()
        except APIDataRetrievalError as e:
            print("no data for",t.date())
            print(e)
            t = t + datetime.timedelta(days=1)
            t1 = t.replace(microsecond=0) - datetime.timedelta(hours=1)
            t2 = t.replace(microsecond=0)
    #sensors = get_vivacity_sensors(token)
    #print(sensors)
    #exit()
    #area = StudyArea.objects.using("crt").get(id=37)
    token = get_vivacity_auth_token(*tracsisAPI)
    sensors = get_vivacity_sensors(token)
    for item in sensors:
        print(item)



    cls = get_vivacity_countlines([],token)
    for cl in cls:
        print(cl)
        loc = cl["location"]#["start"]
        id = cl["id"]
        print(id, loc)
        #try:
        #    countline = CountLine.objects.using("crt").get(id=id)
        #except CountLine.DoesNotExist as e:
        #    print("creating countline",id)
            #CountLine.objects.using("crt").create(id=id,lat=loc["lat"],lon=loc["long"],area=area,company="Vivacity",name="a")
