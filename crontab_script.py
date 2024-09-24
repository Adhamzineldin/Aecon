
import os
import subprocess
import sys
from threading import Thread
import datetime
import schedule
import time

def run_cmd(cmd):
    print("command runned -",cmd)
    print("iteeration - ",datetime.datetime.now())
    Thread(target = lambda x: subprocess.run(x,stdout = subprocess.PIPE,stderr=subprocess.STDOUT,shell=True) ,args = ([cmd])).start()
cmd = 'cd /var/www/webapps/east_lothian && python manage.py updateRecord > cronjobOutput_test.txt 2>&1'
schedule.every(15).minutes.do(run_cmd,cmd = cmd)


cmd = 'cd /var/www/webapps/east_lothian/aecon && python check_api_db.py > checker_output.txt 2>&1'
schedule.every().day.at("00:01:00").do(run_cmd,cmd = cmd)

while True:
    schedule.run_pending()
    time.sleep(1)


    
 
    
    



