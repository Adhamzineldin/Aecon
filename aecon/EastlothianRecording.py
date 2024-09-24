from django.conf import settings
import os
import django
import sys
path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if path not in sys.path:
    sys.path.append(path)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "webapps.settings")
django.setup()
import random
from django.db import connections
import datetime
import geojson
import pandas as pd
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
import threading


DB_NAME = settings.DB_NAME
SEND_MAIL_TO = settings.SEND_MAIL_TO


if __name__ == "__main__":
        locs = Location.objects.using(DB_NAME).filter(observationType_id = 1, startRecievingDate__isnull=False, startRecievingDate__lte = datetime.datetime.utcnow())
        timezone.activate("UTC")
        t2 = datetime.datetime.utcnow().replace(second=0, microsecond=0) - datetime.timedelta(minutes=120)
        end = abs(t2.minute-(t2.minute%5))+5 if t2.minute%5 != 0  else t2.minute
        t2 = t2.replace(minute=0) + datetime.timedelta(minutes = end )
        thread_lst = []
        try:
            apis = VivacityAPI.objects.using(DB_NAME).filter(id=6)
            for api in apis:
                try:
                    # locs_thread = {}
                    for x in locs :
                        if x.lastNonZeroDataReceived :
                            t1 = datetime.datetime(x.lastNonZeroDataReceived.year,x.lastNonZeroDataReceived.month,x.lastNonZeroDataReceived.day,x.lastNonZeroDataReceived.hour,x.lastNonZeroDataReceived.minute,0)
                        else :
                            t1 = datetime.datetime(x.startRecievingDate.year,x.startRecievingDate.month,x.startRecievingDate.day).replace(hour=0,second=0, microsecond=0)
                        t1 = t1.replace(minute=abs(t1.minute-(t1.minute%5)))

                        if t1 < t2 :
                            print("***************************************")
                            print("for loc - {} ,start date - {}, endDate - {}".format(x.id,t1,t2))
                            api.backfill(t1,t2,[x.id])
                            # thread  = threading.Thread(target = api.backfill,args=(t1,t2,[x.id]))
                            # thread.start()
                            # thread_lst.append(thread)
                    # for thrd in thread_lst :
                        # thrd.join()
                    api.locations.all().update_status()
                    
                except Exception as e:
                    print(e)
                    sendMail(SEND_MAIL_TO, "aecon v2 recording " + api.name,
                            "recording failed, " + str(e),
                            sender = None)
           
        except django.db.utils.Error as e:
            sendMail(SEND_MAIL_TO, "aecon recording Server Error",
                    " django error " + str(e))
        except pymysql.Error as e:
            sendMail(SEND_MAIL_TO, "aecon recording Server Error",
                    " Sql server error " + str(e))
        except tracsis_api_helpers.APIError as e:
            sendMail(SEND_MAIL_TO, "aecon v2 recording API Failure",
                    "recording failed, API retrieval error " + repr(e),
                    sender = None)
        


