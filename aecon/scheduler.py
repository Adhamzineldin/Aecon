from aecon.tracsis_api_helpers import get_turning_counts_data
from .models import Project, Location, Arms, Jtc_Data, VivacityAPI
from .automatedemails import sendMail
from apscheduler.schedulers.background import BackgroundScheduler
from django.conf import settings
import os
import datetime
import json
import time
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model



apscheduler = BackgroundScheduler()
EXCEL_ROOT = settings.MEDIA_ROOT


def start_scheduler():
    apscheduler.add_job(check_for_upload_timeout, 'interval', minutes=10, id='upload_timeout_job')
    apscheduler.add_job(clean_temp_file, trigger='cron', hour='00', minute='30')
    apscheduler.add_job(pull_turning_count_data, trigger='cron', minute=0)
    apscheduler.start()

def clean_temp_file():
    for file in os.listdir(EXCEL_ROOT):
        path = os.path.join(EXCEL_ROOT, file)
        if not os.path.isdir(path):
            current_date = datetime.datetime.now()
            created_date = datetime.datetime.fromtimestamp(os.path.getctime(path))
            diff = current_date - created_date
            if diff.days > 15:
                os.unlink(path)


def send_error_email(location, start_zone, end_zone, start_time, end_time, error):
    email = 'rohel@divyaltech.com'
    
    content = "<p>Error in Turning Count Api</p>"
    content += f"<p>Location {location.name}</p>"
    content += f"<p>Start Zone {start_zone}</p>"
    content += f"<p>End Zone {end_zone}</p>"
    content += f"<p>Start Time {start_time}</p>"
    content += f"<p>End Time {end_time}</p>"
    content += f"<p>Error {error}</p>"

    sendMail(email, "Error in Turning Count API", content)

def pull_turning_count_data():
    t1 = datetime.datetime.now(datetime.timezone.utc).replace(second=0, microsecond=0) - datetime.timedelta(minutes=120)
    start = abs(t1.minute-(t1.minute%5))+5 if t1.minute%5 != 0  else t1.minute
    t1 = t1.replace(minute=0) + datetime.timedelta(minutes = start)
    
    t2 = datetime.datetime.now(datetime.timezone.utc).replace(second=0, microsecond=0) - datetime.timedelta(minutes=60)
    end = abs(t2.minute-(t2.minute%5))+5 if t2.minute%5 != 0  else t2.minute
    t2 = t2.replace(minute=0) + datetime.timedelta(minutes = end)
 
    # t1 = datetime.datetime(2024, 5, 1, tzinfo=datetime.timezone.utc)
    # t2 = datetime.datetime(2024, 5, 2, tzinfo=datetime.timezone.utc)
    
    api = VivacityAPI.objects.get(name = 'Turning Counts')
    error_list = []
    # result = []
    locations = api.locations.all()
    classes_mapping = {'car': ['car', 'taxi electric', 'taxi other', 'towed trailer', 'emergency car'], 'lgv': ['van', 'emergency van', 'van small', 'van luton', 'small_van','luton_van'], 'ogv1': ['rigid', 'fire engine', 'tractor', 'agriculture vehicle'], 'ogv2': ['truck'], 'psv': ['bus', 'minibus', 'bus coach', 'bus london'], 'm/c': ['motorbike'], 'p/c': ['pedestrian', 'pushchair', 'wheelchair', 'mobility scooter', 'jogger', 'e-scooter', 'cyclist', 'cargo bike', 'rental bike']}
    
    for location in locations:
        # data = {'location': location.name,'data':[]}
        start_date = location.lastNonZeroDataReceived.replace(tzinfo=datetime.timezone.utc) if location.lastNonZeroDataReceived else t1
        end_date = t2
        arms = list(location.arms_set.all().values('pk','zone_id'))
        projects = list(api.locations.all().values_list('projects', flat=True).distinct())
        classes = {cl.obsClass.name.lower(): cl for cl in location.classes.all()}
  
        for project in projects:
            # Nested loop to traverse each arm with every other arm in the same location
            for i in range(len(arms)):
                for j in range(i, len(arms)):
                    arm1 = arms[i]
                    arm2 = arms[j]
                    while start_date < end_date:
                        try:
                            response = get_turning_counts_data(api.APIKey, arm1['zone_id'], arm2['zone_id'], start_date, start_date+datetime.timedelta(days=1))
                        except Exception as e:
                            error_list.append([location, arm1, arm2, start_date, start_date+datetime.timedelta(days=1),str(e)])
                            break
                        values = list(list(response.values())[0].values())[0]
                        for value in values:
                            value['from'] = datetime.datetime.strptime(value['from'], '%Y-%m-%dT%H:%M:%S.%fZ')
                            value['to'] = datetime.datetime.strptime(value['to'], '%Y-%m-%dT%H:%M:%S.%fZ')
                            counts = {}
                            for cls,count in value['turning_movements'].items():
                                obs_class = find_key_for_value(classes_mapping, cls.lower())
                                # print([ classes[obs_class], obs_class, arm1['pk'], ] if obs_class in classes else None)
                                if obs_class in classes:
                                    counts[obs_class] = counts[obs_class] + int(count) if obs_class in counts else int(count)
                                    
                            # data['data'].append(counts) 
                            for count_cls in counts:
                                Jtc_Data.objects.update_or_create(
                                    location = location,
                                    origin_arm_id = arm1['pk'],
                                    destination_arm_id = arm2['pk'],
                                    start_date = value['from'],
                                    end_date = value['to'],
                                    start_time = value['from'].time(),
                                    end_time = value['to'].time(),
                                    project_id = project,
                                    obsClass = classes[count_cls],
                                    defaults={'pcu':0, 'count' : counts[count_cls],}
                                )
                              
                        
                        start_date += datetime.timedelta(days=1)
        # result.append(data)               
 
    if error_list:
        pass
        # for error in error_list:
        #     send_error_email(error[0], error[1], error[2], error[3], error[4], error[5])

    
def find_key_for_value(data, target_value):
    return next((key for key, values in data.items() if target_value in values), None)


def check_for_upload_timeout():
    print("Checking for unproccessed uploads")

    EXCEL_ROOT = settings.MEDIA_ROOT

    processing_path = os.path.join(EXCEL_ROOT, 'processing')
    json_file_path = os.path.join(processing_path, 'upload_data.json')

    User = get_user_model()

    if os.path.exists(json_file_path):
        with open(json_file_path, 'r+') as json_file:
            jsondata = json.load(json_file)
            print(jsondata)
            if jsondata == {}:
                print("No data was found to need proccessing")
                stop_timeout_job()
                return False
            try:
                jsondata = json.load(json_file)
                for user_key in jsondata.keys():
                    for survey_type_flag in jsondata[user_key].keys():
                        if time.time() - jsondata[user_key][survey_type_flag]['process start time'] > 122*60:
                            print("Recovering timed out upload")
                            jsondata[user_key][survey_type_flag]['processing'] = False
                            json_file.seek(0)
                            json.dump(jsondata, json_file, indent=4)
                            json_file.truncate()
                            from aecon.views import check_if_still_processing
                            check_if_still_processing(
                                get_object_or_404(User, username=user_key))

            except json.JSONDecodeError:
                print(
                    f"Failed to decode JSON from {json_file_path}. File might be empty or corrupted.")
    else:
        print(f"JSON file not found at {json_file_path}.")
        return False
    print("Reached Here")
    return True
    


def stop_timeout_job():
    if is_upload_timeout_job_active():
        print("Stopping timeout job")
        apscheduler.remove_job("upload_timeout_job")
    else:
        print("Upload timeout job is not active")

def start_timeout_job():
    if not is_upload_timeout_job_active():
        print("Starting timeout job")
        apscheduler.add_job(check_for_upload_timeout, 'interval', minutes=10, id='upload_timeout_job')
    else:
        print("Upload timeout job is already active")

def is_upload_timeout_job_active():
    job = apscheduler.get_job('upload_timeout_job')
    return job is not None and job.next_run_time is not None

