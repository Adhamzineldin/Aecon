from logging import exception
import requests
import json
import datetime
from .models import *
from .automatedemails import sendMail
import pytz
from dateutil import parser
from . import tracsis_api_helpers
import pandas as pd

def vivacity_test():
    timezone = pytz.timezone("Europe/London")   
    numdays = 1
    # t = datetime.datetime.utcnow().replace(second=0, microsecond=0) - datetime.timedelta(days=3)
    # t = datetime.datetime().replace(second=0, microsecond=0) 
    t1 = datetime.datetime(2022,3,1).replace(hour=0,minute=0) 
    t2 = datetime.datetime.utcnow().replace(second=0, microsecond=0)
    # t2 = t + datetime.timedelta(minutes=60)

    f_error =  open('data/error_log.txt','w')
    
    lst = ['pedestrian','cyclist','motorbike','car','taxi','van','minibus','bus','rigid','truck','emergency car','emergency van','fire engine']
    
    api = VivacityAPI.objects.using(DB_NAME).get(id=6)
    sensor_lst = Location.objects.using(DB_NAME).filter(observationType_id = 1)
    sensor_lst = [loc.api_identifier for loc in sensor_lst]
    print(sensor_lst)
    # apis = VivacityAPI.objects.using(DB_NAME).filter(record=True)
  
    token = tracsis_api_helpers.get_vivacity_auth_token(api.username,api.password)
    # result = tracsis_api_helpers.get_vivacity_countlines(token,[])
   
    for i in sensor_lst:
        while t1 < t2:
            try:
                print("for sensor ",i)
                result = tracsis_api_helpers.get_vivacity_data(token,t1,t2,i)
                t1 = t1 + datetime.timedelta(minutes=60)
                file = 'data/date_'+str(t.date())+"_"+str(i)+'.json'
                f = open(file,'w')
                print(json.dumps(result, indent = 3),file=f)
                print(file, api.name)
                print("printed in file form time - ",t1,", to - ",t2)
                f.close()
            except Exception as e:
                print('error -',e)
                print ("for -",i," ,api-",api.name," ,",e,"form time - ",t1,", to - ",t2,file=f_error)
                
    
   
    
    # print(token)
    
        # for x in result['23440']:
            
    

def london_breath_data():
    # timezone = pytz.timezone("Europe/London")
    # d = d.astimezone(timezone)
    obsClass_lst = ["NO2","PM25"]
    filename = "new.xlsx" 
    data = pd.read_excel(filename,sheet_name="Sites Added to Dashboard",header = [0])
    data = data.fillna("")
    data  = data['Air Quality Sensor SiteCode'].tolist()
    data = [x for x in data if x != ""]
    data = set(data) #remove the dublicate item
    data = list(data)
    # obsClass_lst = ["PM25"]
 
    sensors = {str(s.vivacity_sensor_id): s for s in Location.objects.using(DB_NAME).filter(observationType=5) if str(s.vivacity_sensor_id) in data}
    # sensors = {str(s.vivacity_sensor_id): s for s in Location.objects.using(DB_NAME).filter(observationType=5) }
    
    timezone.activate("UTC")
    start_date = datetime.datetime(2021,8,1,0)
    # end_date = datetime.datetime(2021,11,25,0)
    end_date = datetime.datetime.utcnow().replace(second=0, microsecond=0)
    not_updated_records = []
    f = open('data/london_breath_data.json','w')
    
    for key in sensors:
        # key = 'CLDP0193'
        sensor = sensors[key]
        try:
            direction = sensor.locationdirection_set.all()[0]
        except:
            direction = None
        # start_date = sensor.lastDataReceived
        # start_date = str(start_date).split('+')[0]
        for index in range(len(obsClass_lst)):
            data_flg =  False
            url = 'https://api.breathelondon.org/api/getClarityData/'+str(key)+'/I'+obsClass_lst[index]+'/'+str(start_date)+'/'+str(end_date)+'/Hourly?key=e2635276-e87a-11eb-9a03-0242ac130003'
            data = requests.get(url)
            data = data.json()
            if len(data) > 0:
                data_flg =  True
                for i in range(len(data)):
                    obs_class =  obsClass_lst[index].replace("25",'2.5') if obsClass_lst[index] == "PM25" else obsClass_lst[index] 
                    for cl in sensor.locationobservationclass_set.all():
                        if cl.obsClass.name == obs_class:
                            d = parser.parse(data[i]['DateTime'])
                            timezone1 = pytz.timezone("Europe/London")
                            d = d.astimezone(timezone1)
                            # print(d)
                            print("for -",cl.obsClass.name,key,sensor.id,data[i]['ScaledValue'],d)
                            
                            # print(cl.obsClass.id,cl.obsClass.name,key)
                            val = data[i]['ScaledValue']
                          
                            c = Observation(date=d, location=sensor,direction=direction, value=val, obsClass=cl)
                            try:
                                c.save()
                            except Exception as e:
                                print(Observation.objects.using(DB_NAME).filter(date=d, location=sensor,direction=direction, value=val, obsClass=cl))
                                print("couldnt save item", str(e))
                            
            else:
                print("no data",data," - ",key,'-',obsClass_lst[index])

                not_updated_records.append({'sensor':key,'obsClass':obsClass_lst[index],'location_name':sensor.name,'start_date':start_date,'end_date':end_date})
        if  data_flg == True:
            if (sensor.lastDataReceived is None or sensor.lastDataReceived < d):
                print("Last reccived date - ",d,key,sensor.lastDataReceived)
                sensor.lastDataReceived = d
                # sensor.save()
            else :
                print("last date is equal to apidate -",d , sensor.lastDataReceived)
    
    if len(not_updated_records)>0:
        msg = "Data is Not available for the following sensors:<br> "
        for item in not_updated_records:
            for key in item:
                msg += str(key) + ": " + str(item[key])+" , "
            msg += "<br>"
        sendMail("rohel@divyaltech.com","School Street London Breathe API Report",msg, sender="automated_email@tracsis-tads.com")
        
        
def import_excel():
    Direction_lst = {'N0':1,'S1':2,'E0': 9,'W1':10 }
    filename = "D:\python\webapps\webapps_EastLothian\East-Lothian\excel_file\Raw_date_for_DB_4615-ELC.csv" 
    data = pd.read_csv(filename)
    data = data.fillna("")
    for index,row in data.iterrows():
        Datetime = parser.parse(str(row['Date']) + " " + str(row['Time']))
        timezone1 = pytz.timezone("Europe/London")
        Datetime = Datetime.astimezone(timezone1)
        loc = int(row['Site_No'])+10
        loc = Location.objects.using(DB_NAME).get(id=loc)
        dir = loc.directions.get(direction = Direction_lst[str(row['Direction'])])
        obsclass = loc.classes.get(order = int(row['Class'])-1)
        print(row['Project_No'])
        project_id  = Project.objects.using(DB_NAME).get(project_no = row['Project_No'].strip())
        print(project_id)
        
        
        # AssociatedObservation.objects.using(DB_NAME).update_or_create(location = loc ,date = Datetime , value = row['Speed'], obsClass = obsclass, direction = dir,project_id = 1)
        break

    # data  = data.groupby(data.Site_No)
    # for i in range(1,10):
    #     df = data.get_group(i)
    #     df2 = df.groupby(df.Direction)
    #     odr = 0
    #     for item in  df2.groups.keys():
    #         dir = Direction.objects.using(DB_NAME).get(id=Direction_lst[item])
    #         loc = i+10
    #         loc = Location.objects.using(DB_NAME).get(id=loc)
    #         print(loc.directions.all())
    #         continue
    #         try:
    #             obj = LocationDirection.objects.using(DB_NAME).update_or_create(location = loc, direction = dir, order = odr)
    #             print("saved",obj,loc,dir,odr)
    #         except Exception as e :
    #             print('error - ',e)
    #         odr +=1
            
        
        
   
    
       
       
            
        
            