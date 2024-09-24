from django.conf import settings
from django.core.management.base import BaseCommand
import os
import django
import sys
path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if path not in sys.path:
    sys.path.append(path)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "slp_server.settings")
django.setup()
import random
from django.db import connections
import datetime
import geojson
import pandas as pd
django.setup()
import pickle
from aecon.views import *
from aecon.automatedemails import sendMail
import pymysql
from aecon import tracsis_api_helpers
import time
import requests
import pytz
import shutil
from django.conf import settings
from dateutil import parser
import time
timePeriod = 15

DB_NAME = settings.DB_NAME
SEND_MAIL_TO = settings.SEND_MAIL_TO
def get_envirowatch_data():
    result = {}
    try:
        result = tracsis_api_helpers.get_london_breath_data()
    except requests.exceptions.RequestException as e:
        print("Requests exception", e)
        sendMail(SEND_MAIL_TO, "crt_recording API", "Envirowatch data request failed," + repr(e),
                 sender = None)
    except ValueError as e:
        print("JSON decode error", e)
        sendMail(SEND_MAIL_TO, "crt_recording API", "Envirowatch data decode failed," + repr(e),
                 sender = None)
    return result


def process_envirowatch_data(data): 
    dataList = []
    if data is None:
        
        sendMail(SEND_MAIL_TO, "crt_recording API - Envirowatch API",
                     "Envirowatch API returned no data or failed to respond on " + datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                     sender = None)
        return
    try:
        sensors = {str(s.vivacity_sensor_id): s for s in Location.objects.using(DB_NAME).filter(observationType=5)}
    except django.db.utils.Error as e:
        print("couldnt access crt database")
        sendMail(SEND_MAIL_TO, "crt_recording API - Database failure", "CRT database unaccessible from django",
                 sender = None)
        sensors = {}
    for item in data:
        if item["SiteCode"] in sensors:
            sensor = sensors[item["SiteCode"]]
            try:
                direction = sensor.locationdirection_set.all()[0]
            except:
                direction = None
            d = parser.parse(item["HourlyBulletinEnd"])
            print("test d is-", d)
            # d = datetime.datetime.strptime('Jun 1 2005  1:33PM', '%b %d %Y %I:%M%p')
            # d = pytz.timezone("Europe/London").localize(d.replace(minute=d.minute - (d.minute%15),second=0,microsecond=0))
            timezone = pytz.timezone("Europe/London")
            d = d.astimezone(timezone)
            start_date = parser.parse(item['StartDate'])
            start_date = start_date.astimezone(timezone)

            if sensor.lastDataReceived is None or sensor.lastDataReceived < d:
                sensor.lastDataReceived = d
                sensor.save()
            diff = pytz.utc.localize(datetime.datetime.utcnow()) - sensor.lastDataReceived
            if diff.total_seconds() > 86400 and (sensor.status == "good" or sensor.status is None): ### 12 hours
                sensor.status = "offline"
                sensor.save()
                
                sendMail(SEND_MAIL_TO, "crt_recording API - Envirowatch Sensor offline", "Sensor " + str(sensor.vivacity_sensor_id) +
                         " has been marked offline at " + datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S") +
                         " as it is more than 24 hours since the last data was received",
                         sender = None)
            weekday = (d.isoweekday() % 7) + 1
            if weekday == 1:
                weekday = 3
            elif weekday == 7:
                weekday = 2
            else:
                weekday = 1
            for cl in sensor.locationobservationclass_set.all():
                print(cl.obsClass.name)
                if cl.obsClass.name == "PM10":
                    val = item["LatestIPM10Value"]
                if cl.obsClass.name == "PM10 NUM":
                    val = item["LatestIPM10NUMValue"]
                if cl.obsClass.name == "NO2":
                    val = item["LatestINO2Value"]
                if cl.obsClass.name == "PM1":
                    val = item["LatestIPM1Value"]
                if cl.obsClass.name == "PM1 NUM":
                    val = item["LatestIPM1NUMValue"]
                if cl.obsClass.name == "PM2.5":
                    val = item["LatestIPM25Value"]
                if cl.obsClass.name == "PM25 NUM":
                    val = item["LatestIPM25NUMValue"]
                if not bool(sensor.imgURL):
                    sensor.imgURL = item['SitePhotoURL']
                if not bool(sensor.installDate):
                    sensor.installDate = start_date
                sensor.save()
                c = Observation(date=d, location=sensor,
                                direction=direction, value=val, obsClass=cl)
                try:
                    c.save()
                except Exception as e:
                    print("couldnt save item", str(e))



def process_envirowatch_status(result):
    try:
        sensors = {str(s.vivacity_sensor_id): s for s in Location.objects.using(DB_NAME).filter(observationType=5)}
        for item in result:
            if item["SiteCode"] in sensors:
                sensor = sensors[item["SiteCode"]]
                #print(sensor.sensorId,sensor.status,item["Health"].lower())
                if sensor.status != "offline" and sensor.status != item["SensorsHealthStatus"].lower():
                    sensor.status = item["SensorsHealthStatus"].lower()
                    sensor.save()
                    
                    sendMail(SEND_MAIL_TO, "crt_recording API - Envirowatch Sensor status change",
                                 "Sensor " + str(sensor.id) + " has been marked with status " + str(item["SensorsHealthStatus"]) +
                                 " at " + datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S") +
                                 " from the envirowatch API",sender = None)

    except requests.exceptions.RequestException as e:
        print("Requests exception", e)
    except ValueError as e:
        print("JSON decode error", e)
    except django.db.utils.Error as e:
        print("Database error",e)

def london_breath_data(air_sensor = "All"):

    obsClass_lst = ["NO2","PM25"]
    if air_sensor == "All":
        sensors = Location.objects.using(DB_NAME).filter(observationType=5)
    else:
        sensors = Location.objects.using(DB_NAME).filter(observationType=5, vivacity_sensor_id__in = air_sensor )
    timezone.activate("UTC")
    start_date = datetime.datetime(2021,8,1,0) #from aug 2021
    end_date = datetime.datetime.utcnow().replace(second=0, microsecond=0)
    not_updated_records = []
    

    for sensor in sensors:
        key = sensor.vivacity_sensor_id
        try:
            direction = sensor.locationdirection_set.all()[0]
        except:
            direction = None
        # start_date = sensor.lastDataReceived
        #start_date =  datetime.datetime(2021,8,1,0)
        # start_date = str(start_date).split('+')[0]
        data_flg =  False
        for index in range(len(obsClass_lst)):
            try:
                data = tracsis_api_helpers.get_london_breath_data_sitecode(key,obsClass_lst[index],start_date,end_date)
            except Exception as e:
                data = []
                print(" error", e)
                # sendMail(SEND_MAIL_TO, "crt_recording API", "Envirowatch data decode failed," + repr(e)
                #         )
            if len(data) > 0:
                data_flg =  True
                for i in range(len(data)):
                    obs_class =  obsClass_lst[index].replace("25",'2.5') if obsClass_lst[index] == "PM25" else obsClass_lst[index] 
                    d = parser.parse(data[i]['DateTime'])
                    timezone_d = pytz.timezone("Europe/London")
                    d = d.astimezone(timezone_d)
                    
                    for cl in sensor.locationobservationclass_set.all():
                        if cl.obsClass.name == obs_class:
                            print("for -",cl.obsClass.name,key,sensor.id,d)
                            val = data[i]['ScaledValue']
                            c = Observation(date=d, location=sensor,direction=direction, value=val, obsClass=cl)
                            try:
                                c.save()
                            except Exception as e:
                                print("couldnt save item", str(e))
                            
            else:
                print("no data",data," - ",key,'-',obsClass_lst[index])
                not_updated_records.append({'sensor':key,'obsClass':obsClass_lst[index],'location_name':sensor.name,'start_date':start_date,'end_date':end_date})
                # sendMail(SEND_MAIL_TO, "crt_recording API", "data is not avaliable for sitecode - " + key +" ,class -"+ obsClass_lst[index])
                
        if  data_flg == True:
            if (sensor.lastDataReceived is None or sensor.lastDataReceived < d):
                print("Last reccived date - ",d,key,sensor.lastDataReceived)
                sensor.lastDataReceived = d
                sensor.save()
            else :
                print("last date is equal to apidate -",d , sensor.lastDataReceived)
    
    if len(not_updated_records)>0:
        msg = "Data is Not available for the following sensors:<br> "
        for item in not_updated_records:
            for key in item:
                msg += str(key) + ": " + str(item[key])+" , "
            msg += "<br>"
        sendMail("manoj@divyaltech.com","School Street London Breathe API Report",msg, sender="automated_email@tracsis-tads.com")
    
  

def import_camden_speed_file(file, locs):
    #
    # locs is a dictionary mapping countline_name, to countline, since we dont store the countline name in
    # the database
    #
    timezone.activate("UTC")

    inDir = Direction.objects.using(DB_NAME).get(id=3)
    outDir = Direction.objects.using(DB_NAME).get(id=4)
    classes = [43087, 43088, 43089, 43090, 43091, 43092, 43076, 43093]
    df = pd.read_csv(file, usecols=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11,12, 13])
    #print("df is", df)
    df.columns = ["date", "start_time", "end_time", "countline_name", "countline_id", "direction", "car", "taxi", "LGV", "bus", "OGV", "motorbike", "cyclist", "pedestrian"]
    df.replace(inplace=True, to_replace="n/a", value=None)
    #print(df.info())
    df = df.where(pd.notnull(df), None)
    data = []
    for _, row in df.iterrows():
        #print(row)
        d = timezone.make_aware(datetime.datetime.strptime(row["date"] + " " + row["start_time"], "%Y-%m-%d %H:%M:%S"))
        #print("d is", d)
        loc = locs[str(row["countline_id"])]
        selectedDir = inDir if row["direction"] == "in" else outDir
        for index, cls in enumerate(["car", "taxi", "LGV", "bus", "OGV", "motorbike", "cyclist", "pedestrian"]):
            if row[cls]:
                data.append(AssociatedObservation(location=loc, obsClass_id=classes[index], value=row[cls], date=d, direction=selectedDir))
    AssociatedObservation.objects.using(DB_NAME).bulk_create(data, ignore_conflicts=True)
    print("num data points to import ", len(data))

if False:
    client = Client.objects.using(DB_NAME).get(id=3)
    locs = client.locations.filter(temp=True).exclude(id="1310-WTR_S115")
    print([l.id for l in locs])
    exit()
    timezone.activate("UTC")
    for loc in locs:
        dirs = loc.ordered_location_direction_queryset()
        classes = loc.ordered_class_queryset()
        startDate = loc.observation_set.filter(status=0).latest("date").date
        print("start date is",startDate)
        endDate = timezone.make_aware(datetime.datetime.now())
        print("starting",datetime.datetime.now())
        while startDate < endDate:
            data = []
            for cl in classes:
                for d in dirs:
                    o = Observation(location=loc,direction=d,obsClass=cl,date=startDate,status=1,value=0)
                    data.append(o)
            #print("data is",data)
            startDate += datetime.timedelta(minutes=15)
            Observation.objects.using(DB_NAME).bulk_create(data, ignore_conflicts=True)
    exit()        #exit()



class Command(BaseCommand):
    help = "Update list of observation."
    
    def handle(self, *args, **kwargs):
        
        # filename = "new.xlsx" 
        # data = pd.read_excel(filename,sheet_name="Sites Added to Dashboard",header = [0])
        # data = data.fillna("")
        # loc  = data['Vivacity Countlineid'].tolist()
        # air_sensor = data['Air Quality Sensor SiteCode'].tolist()
        
        loc = Location.objects.using(DB_NAME).filter(observationType_id = 1, startRecievingDate__isnull=False, startRecievingDate__lte = datetime.datetime.utcnow() )
        timezone.activate("UTC")
        t2 = datetime.datetime.utcnow().replace(second=0, microsecond=0) 
        
        # t2 = t.replace(microsecond=0) + datetime.timedelta(minutes=60)
        try:
            apis = VivacityAPI.objects.using(DB_NAME).filter(id=6)
            for api in apis:
                try:
                    for x in loc :
                        if x.lastNonZeroDataReceived :
                            t1 = datetime.datetime(x.lastNonZeroDataReceived.year,x.lastNonZeroDataReceived.month,x.lastNonZeroDataReceived.day,x.lastNonZeroDataReceived.hour,x.lastNonZeroDataReceived.minute,0)
                        else :
                            t1 = datetime.datetime(x.startRecievingDate.year,x.startRecievingDate.month,x.startRecievingDate.day).replace(hour=0,second=0, microsecond=0)
                        startDate_resp = api.backfill(t1,t2,[x.id])
                        api.locations.all().update_status()
                    #api.locations.all().fill_daily_classed_totals(datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0))
                except Exception as e:
                    print(e)
                    sendMail(SEND_MAIL_TO, "aecon v2 recording " + api.name,
                            "recording failed, " + str(e),
                            sender = None)

            ###
            ### camden speed data
            ### temp way to import "live" data
            ### from files in a google bucket
            ###
            # startDate = t1
            # endDate = t2
            # startDate = startDate.replace(minute=startDate.minute - (startDate.minute % 5))
            # locs = {loc.id: loc for loc in Location.objects.using(DB_NAME).all()}
            # while startDate < endDate:
            #     try:
            #         f = io.BytesIO()
            #         with requests.get("https://storage.googleapis.com/tracsis_camden_speed_data/5_minute_speed/" + str(
            #                 int(startDate.timestamp())) + ".csv", stream=True) as r:
            #             print("status code", r.status_code)
            #             shutil.copyfileobj(r.raw, f)
            #             if r.status_code == 200:
            #                 f.seek(0)
            #                 import_camden_speed_file(f, locs)
            #             else:
            #                 print("issue retrieving file for", startDate, r.status_code)
            #     except Exception as e:
            #         print("error importing camden speed data", e)
            #     finally:
            #         startDate += datetime.timedelta(minutes=5)

            ###
            ### QFREE cheshire cycle counts
            ### update at midnight every night.
            ### API may not always be up to date so get the whole previous week
            ###
            
            
            # if t1.hour == 0 and t1.minute < 15:
            #     try:
            #         api = VivacityAPI.objects.using(DB_NAME).get(id=4)
            #         api.backfill(t - datetime.timedelta(days=7), t)
            #         api.locations.all().update_status()
            #         sendMail(SEND_MAIL_TO, "aecon v2 recording Cheshire API",
            #                 "Midnight recording successful",
            #                 sender = None)
            #     except Exception as e:
            #         sendMail(SEND_MAIL_TO, "aecon v2 recording " + api.name,
            #                 "recording failed, " + str(e),
            #                 sender = None)
            
            
            
            ###
            ### Envirowatch
            ###
            try:
                pass
                # london_breath_data()
            except Exception as e:
                sendMail(SEND_MAIL_TO, "aecon v2 recording " ,api.name,
                    "Envirowatch recording failed, " + str(e),
                    sender = None)
           
        except django.db.utils.Error as e:
            sendMail(SEND_MAIL_TO, "school streets recording Server Error",
                    " django error " + str(e))
        except pymysql.Error as e:
            sendMail(SEND_MAIL_TO, "school streets recording Server Error",
                    " mysql error " + str(e))
        except tracsis_api_helpers.APIError as e:
            sendMail(SEND_MAIL_TO, "aecon v2 recording API Failure",
                    "recording failed, API retrieval error " + repr(e),
                    sender = None)
        
