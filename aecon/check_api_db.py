from http import client
import os
import django
import sys
path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if path not in sys.path:
    sys.path.append(path)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "webapps.settings")
django.setup()
import datetime
import pandas as pd
from aecon.views import *
import tracsis_api_helpers
import pytz
from pathlib import Path
from dateutil.parser import parse

# mail_lst = ['manoj@divyaltech.com','rohel@divyaltech.com','Sam.Aziz@tracsis.com']
mail_lst = ['rohel@divyaltech.com']
def sum_api_value(data,loc):
    total = 0
    classes = [cl.obsClass.name for cl in loc.classes.all()]
    
    for key,value in data[str(loc.api_identifier)].items():
        for item in value['counts']:
            if item['class'] in classes:
                total =  total + item['countOut'] + item['countIn']
    return total

def check_weekly_data(api,locs,date,clnt):
    print("for Weekly Data")
    start_date = date - datetime.timedelta(days=7)
    end_date = date.replace(hour=23,minute=59)
    unmatched_list = []
    for loc in locs:
        print("------------------------------------")
        print("for loc - ",loc)
        try:
            print("filter -",loc,start_date,end_date)
            db_total = Observation.objects.using(DB_NAME).filter(location=loc,date__range=[start_date,end_date]).aggregate(sum=Sum('value'))
            print("db_total -",db_total)
            db_total = int(db_total['sum']) if db_total['sum'] is not None else 0
            print("db_total: %d" % db_total)
        except Exception as e:
            print("error", e)
            db_total = 0
        
        try:
            api_total = 0
            st  = start_date
            while st < end_date:
                print(st)
                token = tracsis_api_helpers.get_vivacity_auth_token(api.username, api.password)
                response = tracsis_api_helpers.get_vivacity_data(token, st.replace(tzinfo = None), (st + datetime.timedelta(days=1)).replace(tzinfo = None), loc.api_identifier)
                if api_total == 0 and len(response[loc.api_identifier])>0:
                    api_total = response
                elif len(response[loc.api_identifier])>0:
                    api_total[loc.api_identifier].update(response[loc.api_identifier])
                st = st + datetime.timedelta(days=1)
            api_total = sum_api_value(api_total,loc)
        except Exception as e :
            print(e)
            api_total = 0
        if (int(db_total) != int(api_total)):
            unmatched_list.append([loc.area.name,loc.name,loc.api_identifier,start_date.strftime("%Y-%m-%d %H:%M:%S"),(end_date).strftime("%Y-%m-%d %H:%M:%S"),api_total,db_total])
            
    if (unmatched_list):
        html = pd.DataFrame(unmatched_list, columns=['Area','Sensor_Name','Countiline_ID','Start DateTime','End DateTime','Api_total','DB_total']).to_html(index=False)
        html =  html.replace('text-align: right','text-align: center')
        sub = "Weekly Reports Unmatched Values  in DB for Client -  "+clnt.name
        sendMail(mail_lst,sub,html)
    else:
        print("No Unmatched Values found")

        
       
            
            
def check_daily_data(api,locs,start_date,clnt):
    print("for Daily Data")
    
    unmatched_list = []
    for loc in locs:
        print("------------------------------------")
        print("for loc - ",loc)
        try:
            db_total = Observation.objects.using(DB_NAME).filter(location=loc,date__range=[start_date,  start_date + datetime.timedelta(hours=23,minutes=59)]).aggregate(sum=Sum('value'))
            db_total = int(db_total['sum']) if db_total['sum'] is not None else 0
        except Exception as e:
            print("error", e)
            db_total = 0
        try:
            print("checking", loc.name, loc.id ,loc.api_identifier)
            token = tracsis_api_helpers.get_vivacity_auth_token(api.username, api.password)
            response = tracsis_api_helpers.get_vivacity_data(token, start_date.replace(tzinfo = None), (start_date + datetime.timedelta(days=1)).replace(tzinfo = None), loc.api_identifier)
            api_total = sum_api_value(response,loc)
        except Exception as e :
            print(e)
            api_total = 0
        if (int(db_total) != int(api_total)):
            unmatched_list.append([loc.area.name,loc.name,loc.api_identifier,start_date.strftime("%Y-%m-%d %H:%M:%S"),(start_date + datetime.timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S"),api_total,db_total])
    if (unmatched_list):
        html = pd.DataFrame(unmatched_list, columns=['Area','Sensor_Name','Countiline_ID','Start DateTime','End DateTime','Api_total','DB_total']).to_html(index=False)
        html =  html.replace('text-align: right','text-align: center')
        sub = "Daily Reports Unmatched Values in DB for  Client -  "+clnt.name
        sendMail(mail_lst,sub,html)
    else:
        print("No Unmatched Values found")
    
            
  
if __name__ == "__main__":
    clients  = Client.objects.using(DB_NAME).filter(id=18)
    current_date = datetime.datetime.now(pytz.utc) - datetime.timedelta(days=1) 
    api = VivacityAPI.objects.using(DB_NAME).get(id=6)
    start_date = current_date.replace(hour=0, minute=0, second=0, microsecond=0)
    
    for clnt in clients:
        print("********************************")
        print("for client -",clnt)
        locs  = api.locations.filter(id__in=clnt.locations.all().values("id"))
        check_daily_data(api,locs,start_date,clnt)
        if current_date.strftime("%A") == "Saturday":
            check_weekly_data(api,locs,start_date,clnt)
            
# 0 1 * * * /var/www/webapps/east_lothian/east_lothian_env/bin/python /var/www/webapps/east_lothian/aecon/check_api_db.py >> /var/www/webapps/east_lothian/checking_output.log 2>&1


            
 
        
    

    
    
