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
from django.db.models import Sum
from threading import Thread


def check_or_create_dir(loc=None):
    parent_dir = Path(__file__).resolve().parent
    path = os.path.join(parent_dir,r'aecon_update_reports')
    if not os.path.exists(path):
        os.mkdir(path)
    if loc is not None:
        path = os.path.join(path,str(loc.area.name)+"__("+str(loc.name)+"__"+str(loc.id)+")")
        if not os.path.exists(path):
            os.mkdir(path)
    return path

def sum_api_value(data,loc):
    total = 0
    classes = [cl.obsClass.name for cl in loc.classes.all()]
    
    for key,value in data[str(loc.api_identifier)].items():
        for item in value['counts']:
            if item['class'] in classes:
                total =  total + item['countOut'] + item['countIn']
    return total

def check_specfic_loc(api,loc,startDt,endDt):
    output = []
    print("-------------------------------------------------")
    while startDt < endDt:
        print("***************************************************")
        print("for loc_id: {} strat-Date: {} ,endDate : {}".format(loc.id,startDt,endDt))
        try:
            db_total = Observation.objects.using(DB_NAME).filter(location=loc,date__range=[startDt,  startDt + datetime.timedelta(hours=23,minutes=59)]).aggregate(sum=Sum('value'))
            db_total = int(db_total['sum']) if db_total['sum'] is not None else 0
        except Exception as e:
            print("error", e)
            db_total = 0
        print("db_total -",db_total)
        try:
            token = tracsis_api_helpers.get_vivacity_auth_token(api.username, api.password)
            response = tracsis_api_helpers.get_vivacity_data(token, startDt.replace(tzinfo = None), (startDt + datetime.timedelta(days=1)).replace(tzinfo = None), loc.api_identifier)
            api_total = sum_api_value(response,loc)
        except Exception as e :
            print(e)
            api_total = 0
        print("api_total -",api_total)
        try :
            if (int(db_total) != int(api_total)):
                # obs = Observation.objects.using(DB_NAME).filter(location=loc,date__range=[startDt,  startDt + datetime.timedelta(hours=23,minutes=59)])
                # obs.delete()            
                result = api.get_data_from_api_and_save(startDt.replace(tzinfo=None), (startDt.replace(tzinfo=None))+ datetime.timedelta(days=1),selectedSites=[loc], save=True,update=True)
                output.append([startDt.strftime("%Y-%m-%d %H:%M:%S"),(startDt + datetime.timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S"),api_total,db_total])
        except Exception as e:
            print("error -",e)
            exit()
            
        startDt += datetime.timedelta(days=1)
        # break
    print(output)
    # path = check_or_create_dir(loc)
    # if len(output)>0:
    #     pd.DataFrame(output, columns=["Start Date","END DATE", "API_value","DB_value"]).to_csv(os.path.join(path,r"report.csv"))
           
if __name__ == "__main__":
    # api = VivacityAPI.objects.using(DB_NAME).get(id=6)
    # data = pd.read_excel(r'D:\python\webapps\webapps_EastLothian\East-Lothian\reports\aecon.xlsx')
    # data.fillna("")
    # # data = data.drop_duplicates(subset=['Countiline_ID'], keep='first')
  
    # data = data.drop_duplicates(subset=['Countiline_ID'], keep='first')
  
    # for index,row in data.iterrows():
    #     print("-------------------")
    #     print("for index -", index)
    #     for loc in api.locations.filter(api_identifier = row['Countiline_ID']) :
    #         check_specfic_loc(api,loc,row['Start DateTime'].replace(tzinfo = pytz.utc),row['End DateTime'].replace(tzinfo = pytz.utc))
    # exit()
    api = VivacityAPI.objects.using(DB_NAME).get(id=6)
    current_date = datetime.datetime.now(pytz.utc) - datetime.timedelta(days=1) 
    startDate = current_date.replace(hour=0,minute=0,second=0,microsecond=0)
    endDate = datetime.datetime.now(pytz.UTC).replace(hour=0,minute=0,second=0,microsecond=0)
    for loc in api.locations.all() :
        try :
            # Thread(target=check_specfic_loc,args=(api,loc,startDate,endDate)).start()
            check_specfic_loc(api,loc,startDate,endDate)
        except Exception as e:
            print("error -",e)


        

# 30 2 * * * /var/www/webapps/east_lothian/east_lothian_env/bin/python /var/www/webapps/east_lothian/aecon/checker.py >> /var/www/webapps/east_lothian/Checker.log 2>&1

           
  

            