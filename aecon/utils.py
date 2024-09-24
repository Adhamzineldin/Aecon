import pandas as pd
import os
import sys

from aecon.tracsis_api_helpers import get_turning_counts_data, APIDataRetrievalError
from .models import Project, Location, Client, ProjectLocations, LocationObservationClass, Arms, Jtc_Data, VivacityAPI
from .automatedemails import sendMail
import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from django.conf import settings
from concurrent.futures import ThreadPoolExecutor, wait
from django.db import transaction
import threading

apscheduler = BackgroundScheduler()
EXCEL_ROOT = settings.MEDIA_ROOT

def upload_jtc_data_todb(user, uploaded_files_list, Obs_type, token):
    print('reached here')
    try:
        print_path = os.path.join(EXCEL_ROOT, f'{token}.txt')

        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = []

            for index, name in enumerate(uploaded_files_list):
                future = executor.submit(process_and_insert_file, name, Obs_type, print_path, index+1, uploaded_files_list,user)
                futures.append(future)
            
            # Wait for all database insertion threads to complete
            wait(futures)
            write_status_in_file(print_path, f'Uploading Process Completed')

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno,e)


def process_and_insert_file(name, Obs_type, print_path, index, total_files,user):
    try:
        processing_path = os.path.join(EXCEL_ROOT, 'processing')
        file_path = os.path.join(processing_path, name)
        sheet_names = pd.ExcelFile(file_path).sheet_names

        df1 = pd.read_excel(file_path, sheet_name=[name for name in sheet_names if name not in ['Arms', 'Raw_Data']][0])
        df2 = pd.read_excel(file_path, sheet_name='Arms')
        df3 = pd.read_excel(file_path, sheet_name='Raw_Data')

        return_data = upload_jtc_site_information_to_db(df1, df2, Obs_type, print_path)
        upload_jtc_raw_data_to_db(return_data, df3, print_path)

        try:
            os.unlink(file_path)
        except Exception as e:
            raise Exception(f'Failed to delete {file_path}. Reason: {e}')
        
        if ((index+1) % 5) == 0:
            filenames = total_files[index-4:index+1]
            last_file = (len(total_files) == index+1)
            send_email_for_jtc(filenames, user, last_file=last_file)
        elif len(total_files) == index+1:
            filenames = total_files[-abs(len(total_files)%5):]
            send_email_for_jtc(filenames, user, last_file=True)
                
        write_status_in_file(print_path, f'Processing Completed for {name} & {index}/{len(total_files)}')

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno,e)
        
    
def upload_jtc_site_information_to_db(site_df, arms_df, obs_typ, print_path):  # for importing locations
    try:
        data = site_df
        data = data.fillna("")

        class_id = [1, 43123, 43124, 3, 43125, 43135, 43106, 169]
        for index, row in data.iterrows():
            # for adding Project
            project = Project.objects.update_or_create(project_no=row['Project_No'].strip(),
                                                                    name=row['Project Name'].strip(),
                                                                    survey_type = row['Survey_Type'].strip(),
                                                                    defaults={'survey_type': row['Survey_Type'].strip(),
                                                                                'name':  row['Project Name'].strip()})
            project = project[0]
            
            # -------------------------------------------------------------------------------------------

            # for adding Location

            location = Location.objects.update_or_create(observationType_id=obs_typ,
                                                                    api_identifier=row['Site_No'],
                                                                    defaults={'name': row['Site_Name'].strip(),
                                                                            'observationType_id': obs_typ,
                                                                            'api_identifier': row['Site_No'],
                                                                            'lat': row['Lat'],
                                                                            'lon': row['Long'],
                                                                            })
            location = location[0]

            # For adding the location to the client
            client = Client.objects.get(id=18)
            client.locations.add(location)
            project = Project.objects.get(project_no=row['Project_No'].strip())
            try:
                startDate = datetime.datetime.strptime(str(row['startDate']), "%d/%m/%Y").date()  # 1- %Y-%m-%d, 2- %m/%d/%Y
                endDate = datetime.datetime.strptime(str(row['endDate']), "%d/%m/%Y").date()
            except ValueError as ve:
                print(ve)
                startDate = row['startDate']
                endDate = row['endDate']

            print(startDate, endDate)
            ProjectLocations.objects.update_or_create(location=location, project=project,
                                                                    defaults={'location': location,
                                                                            'project': project,
                                                                            'startDate': startDate,
                                                                            'endDate': endDate})

            for i in range(len(class_id)):
                LocationObservationClass.objects.get_or_create(location=location, obsClass_id=class_id[i],
                                                                            order=i, defaults={'location': location,
                                                                                                'obsClass_id': class_id[i],
                                                                                                'order': i})

            # ----------------------------------------------------------------------------------------------

            write_status_in_file(print_path, f'Site No - {row["Site_No"]}, Added sucessfully')
            
            arms_data = arms_df.loc[(arms_df['Site_No'] == row['Site_No']) & (arms_df['Project_No'] == row['Project_No'].strip())]
            
            arms_temp_data = []
            for i, arms_row in arms_data.iterrows():
                

                arms = Arms.objects.update_or_create(location=location, project=project, name = arms_row['Name'],
                                                                    defaults={'location': location,
                                                                            'project': project,
                                                                            'name': arms_row['Name'],
                                                                            'display_name': arms_row['Display_Name'],
                                                                            'lat':arms_row['Lat'],
                                                                            'lon':arms_row['Lon']
                                                                            })
                write_status_in_file(print_path, f'Arms - {arms[0].name}, id - {arms[0].id}, Added sucessfully')
                arms_temp_data.append([arms[0].name, arms[0]])
            retrun_data = {'location':location, 'Arms':arms_temp_data, 'project':project}
        write_status_in_file(print_path, f'In Progress - {location.name}')
        return retrun_data
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno,e)

def upload_jtc_raw_data_to_db(retrun_data, raw_data_df, print_path):
    class_id = [1, 43123, 43124, 3, 43125, 43135, 43106, 169] # Ped = 1, PC = 2, MC = 3, Car = 4, LGV = 5, OGV1 = 6, OGV2 = 7, PSV/BUS = 8
    grouped = raw_data_df.groupby(['Site Number', 'Origin Arm', 'Destination Arm'])

    loc_obs_cls = {}
    for index, obs_cls in enumerate(class_id):
        loc_obs = LocationObservationClass.objects.get(location=retrun_data['location'], obsClass_id=obs_cls)
        loc_obs_cls[index + 1] = loc_obs

    bulk_insert_data = []

    try:
        with transaction.atomic():
            # Delete existing data for the given location and project
            Jtc_Data.objects.filter(location=retrun_data['location'], project=retrun_data['project']).delete()
            for name, group in grouped:
                origin_arm = [i[1] for i in retrun_data['Arms'] if i[0] == name[1]][0]
                destination_arm = [i[1] for i in retrun_data['Arms'] if i[0] == name[2]][0]

                for index, row in group.iterrows():
                    bulk_insert_data.append(Jtc_Data(
                        location=retrun_data['location'],
                        project=retrun_data['project'],
                        origin_arm=origin_arm,
                        destination_arm=destination_arm,
                        obsClass=loc_obs_cls[row['Vehicle Class']],
                        start_time=row['Start Time'],
                        end_time=row['End Time'],
                        count=row['Vehicle Count'],
                        pcu=row['PCU Value'],
                        peak_hour=row['Peak Hour']
                    ))

                    # Optionally, you can clear the bulk_insert_data list to reduce memory usage
                    if len(bulk_insert_data) == 3000:  # You can adjust this batch size based on your performance testing
                        Jtc_Data.objects.bulk_create(bulk_insert_data)
                        bulk_insert_data = []

            # Insert any remaining data
            if bulk_insert_data:
                Jtc_Data.objects.bulk_create(bulk_insert_data)

            write_status_in_file(print_path, f'{retrun_data["location"].name}, JTC Data for has been uploaded successfully')

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno, e)

    
def write_status_in_file(path, msg, edit_last_row=False):
    try:
    
        if edit_last_row:
                f = open(path,'r')        
                data = f.readlines()
                if 'row' in data[-1]:
                    data.pop() # remove the last element of list i.e row                
                data.append(f'{msg} \n')
                f.close()
                fw = open(path,'w')
                fw.writelines(data)
                fw.close()
        else:
            with open(path, 'a+') as f:
                f.write(f'{msg} \n')
    except OSError as e:

        write_status_in_file(path, msg, edit_last_row)
        
def send_email_for_jtc(filenames, user, last_file=False):
    email = str(user.email)
    
    content = "<p>Dear " + str(user.first_name) + ",</p>"
    content += "<br><p>Data Upload for AECON is completed.</p>"
    content += "<p>The Files uploaded are: " + ", ".join(filenames) + "</p>"
    content += "<p>You can now review it on the website.</p>"

    if last_file:
        content += "<p><strong>Note: This was the last batch of files in your upload request. " \
                    "Feel free to start a new upload process</strong></p>"

    content += "<br><p>Kind Regards,"
    content += "<br>AECON Team</p>"
    
    sendMail(email, "Upload Completed", content)
    
    
# def start_scheduler():
#     apscheduler.add_job(clean_temp_file, trigger='cron', hour='00', minute='30')
#     pull_turning_count_data()
#     # apscheduler.add_job(pull_turning_count_data, trigger='interval', seconds=5)
#     apscheduler.start()
#     print(apscheduler.get_jobs())
    
# def clean_temp_file():
#     for file in os.listdir(EXCEL_ROOT):
#         path = os.path.join(EXCEL_ROOT, file)
#         current_date = datetime.datetime.now()
#         created_date = datetime.datetime.fromtimestamp(os.path.getctime(path))
#         diff = current_date - created_date
#         if diff.days > 15:
#             os.unlink(path)
            
# def pull_turning_count_data():
    # t1 = datetime.datetime.now(datetime.timezone.utc).replace(second=0, microsecond=0) - datetime.timedelta(minutes=120)
    # start = abs(t1.minute-(t1.minute%5))+5 if t1.minute%5 != 0  else t1.minute
    # t1 = t1.replace(minute=0) + datetime.timedelta(minutes = start)
    
    # t2 = datetime.datetime.now(datetime.timezone.utc).replace(second=0, microsecond=0) - datetime.timedelta(minutes=60)
    # end = abs(t2.minute-(t2.minute%5))+5 if t2.minute%5 != 0  else t2.minute
    # t2 = t2.replace(minute=0) + datetime.timedelta(minutes = end)
 

    # api = VivacityAPI.objects.get(id=8)
    
    # for location in api.locations.all():
    #     start_date = location.lastNonZeroDataReceived.replace(tzinfo=datetime.timezone.utc) if location.lastNonZeroDataReceived else t1
    #     end_date = t2
    #     arms = list(location.arms_set.all().values('pk','zone_id'))
    #     projects = list(api.locations.all().values_list('projects', flat=True).distinct())
    #     classes = {cl.obsClass.name: cl for cl in location.classes.all()}
    #     for project in projects:
    #         # Nested loop to traverse each arm with every other arm in the same location
    #         data = []
    #         for i in range(len(arms)):
    #             for j in range(i, len(arms)):
    #                 arm1 = arms[i]
    #                 arm2 = arms[j]
    #                 while start_date < end_date:
    #                     try:
    #                         response = get_turning_counts_data(api.APIKey, arm1['zone_id'], arm2['zone_id'], start_date, start_date+datetime.timedelta(days=1))
    #                     except APIDataRetrievalError as e:
    #                         print(e)
    #                         break
    #                     values = list(list(response.values())[0].values())[0]
    #                     for value in values:
    #                         value['from'] = datetime.datetime.strptime(value['from'], '%Y-%m-%dT%H:%M:%S.%fZ')
    #                         value['to'] = datetime.datetime.strptime(value['to'], '%Y-%m-%dT%H:%M:%S.%fZ')
    #                         for cls,count in value['turning_movements'].items():
    #                             if cls in classes:
    #                                 data.append(Jtc_Data(
    #                                     location = location,
    #                                     origin_arm_id = arm1['pk'],
    #                                     destination_arm_id = arm2['pk'],
    #                                     obsClass = classes[cls],
    #                                     start_date = value['from'],
    #                                     end_date = value['to'],
    #                                     start_time = value['from'].time(),
    #                                     end_time = value['to'].time(),
    #                                     count = count,
    #                                     pcu = 0,
    #                                     project = project
    #                                 ))
    #                     start_date += datetime.timedelta(days=1)
                        
    #         if len(data):
    #             Jtc_Data.create_update_objects.bulk_update_or_create(data, ['count'], match_field=['location','origin_arm','destination_arm','obsClass','start_date','end_date','start_time','end_time'], batch_size=1000)
    # # for loc in api.locations.all():
    # #     for project in loc.arms_set.all():
    # #         print('project -', project )
    # return
    # proj = Project.objects.get(id=10)
    # start_zone = Arms.objects.get(zone_id=12867)
    # end_zone =  Arms.objects.get(zone_id=12869)
    # start_date = datetime.datetime(2024, 5, 1, 0, 0, 0)
    # end_date = datetime.datetime(2024, 5, 2, 0, 0, 0)
    # response = get_turning_counts_data(api.APIKey, start_zone.zone_id, end_zone.zone_id, start_date, end_date)
    # values = list(list(response.values())[0].values())[0]
    # loc = Location.objects.get(id=67)
    # classes = {cl.obsClass.name: cl for cl in loc.classes.all()}
    # print(classes)
    # data = []
    
    # for value in values:
    #     value['from'] = datetime.datetime.strptime(value['from'], '%Y-%m-%dT%H:%M:%S.%fZ')
    #     value['to'] = datetime.datetime.strptime(value['to'], '%Y-%m-%dT%H:%M:%S.%fZ')
    #     for cls,count in value['turning_movements'].items():
    #         if cls in classes:
    #             data.append(Jtc_Data(
    #                 location = loc,
    #                 origin_arm = start_zone,
    #                 destination_arm = end_zone,
    #                 obsClass = classes[cls],
    #                 start_date = value['from'],
    #                 end_date = value['to'],
    #                 start_time = value['from'].time(),
    #                 end_time = value['to'].time(),
    #                 count = count,
    #                 pcu = 0,
    #                 project = proj
    #             ))
    # Jtc_Data.create_update_objects.bulk_update_or_create(data, ['count'] ,match_field=['location','origin_arm','destination_arm','obsClass','start_date','end_date','start_time','end_time'])
        
def add_turning_counts_sensors(filename, print_path):
    sensor_df = pd.read_excel(filename, sheet_name='Sensors')
    sensor_df = sensor_df.fillna("-")
    zones_df = pd.read_excel(filename, sheet_name='Zones')
    zones_df = zones_df.fillna("")
    class_id = [1, 43123, 43124, 3, 43125, 43135, 43106, 169]
    obs_typ = 13
    length_sensors = sensor_df[sensor_df.columns[0]].count()
    for index, row in sensor_df.iterrows():
        # for adding Project
        project = Project.objects.update_or_create(project_no=row['Project_No'].strip(),
                                                                  name=row['Project_No'].strip(),
                                                                  survey_type = row['Survey_Type'].strip(),
                                                                  defaults={'survey_type': row['Survey_Type'].strip(),
                                                                            'name':  row['Project_No'].strip()})
        project = project[0]
        
        location = Location.objects.update_or_create(observationType_id=obs_typ,
                                                                 vivacity_sensor_id=row['Sensor_ID'],
                                                                 defaults={'name': row['Sensor_Name'].strip(),
                                                                           'observationType_id': obs_typ,
                                                                           'vivacity_sensor_id': row['Sensor_ID'],
                                                                           'api_identifier' : row['Site_ID'],
                                                                           'lat': row['Lat'],
                                                                           'lon': row['Long'],
                                                                           })
        location = location[0]
        write_status_in_file(print_path, f'''Sensor No - {row['Sensor_ID']}, Added sucessfully''')
        
        client = Client.objects.get(id=18)
        client.locations.add(location)
        
        api = VivacityAPI.objects.get(name = 'Turning Counts')
        api.locations.add(location)
        
        try:
            startDate = datetime.datetime.strptime(str(row['startDate']), "%Y-%m-%d").date()  # 1- %Y-%m-%d, 2- %m/%d/%Y
            endDate = datetime.datetime.strptime(str(row['endDate']), "%Y-%m-%d").date()
        except ValueError:
            startDate = row['startDate']
            endDate = row['endDate']
            
            
        ProjectLocations.objects.update_or_create(location=location, project=project,
                                                                 defaults={'location': location,
                                                                           'project': project,
                                                                           'startDate': startDate,
                                                                           'endDate': endDate})

        for i in range(len(class_id)):
            LocationObservationClass.objects.get_or_create(location=location, obsClass_id=class_id[i],
                                                                          order=i, defaults={'location': location,
                                                                                             'obsClass_id': class_id[i],
                                                                                             'order': i})
        
        print(project, location,'added successfully')
        zones_data = zones_df.loc[(zones_df['Sensor_ID'] == row['Sensor_ID']) & (zones_df['Project_No'] == row['Project_No'].strip())]
        
        if 'Display_Name' not in zones_data:
            zones_data['Display_Name'] = zones_data['Zone_name']
            
        for i, arms_row in zones_data.iterrows():

            arms = Arms.objects.update_or_create(location=location, project=project, zone_id = arms_row['Zone_ID'],
                                                                defaults={'location': location,
                                                                           'project': project,
                                                                           'name': arms_row['Zone_name'],
                                                                           'display_name': arms_row['Display_Name'],
                                                                           'lat':arms_row['Lat'],
                                                                           'lon':arms_row['Long']
                                                                           })
            print(arms, 'added successfully')
            write_status_in_file(print_path, f'Arms - {arms[0].name}, id - {arms[0].id}, Added sucessfully')

        write_status_in_file(print_path, f'''Processing Completed for {row['Sensor_Name'].strip()} & {index+1}/{length_sensors}''')
    
    write_status_in_file(print_path, f'Uploading Process Completed')

def turning_count_thread(upload_files, token):
    print_path = os.path.join(EXCEL_ROOT, f'{token}.txt')
    print("print_path print_path",print_path)
    for name in upload_files:
        file_path = os.path.join(EXCEL_ROOT, name)
        add_turning_counts_sensors(file_path, print_path)
        
     