import os
import json
import time
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.core.files.storage import FileSystemStorage

EXCEL_ROOT = settings.MEDIA_ROOT
LOCK_FILE = os.path.join(EXCEL_ROOT, 'processing', 'startup.lock')
PROCESSING_PATH = os.path.join(EXCEL_ROOT, 'processing')


def download_files_from_db():
    download_path = PROCESSING_PATH
    
    print(f"Downloading files from the db to: '{download_path}'!")

    from .models import UploadedFile, JSONFile
    
    # Create the download directory if it doesn't exist
    if not os.path.exists(download_path):
        os.makedirs(download_path)

    # Download upload data JSON file
    try:
        json_file = JSONFile.objects.get(file_name='upload_data.json')
    except:
        print("No upload_data.json was found in the Database")
        json_file = JSONFile(file_name = 'upload_data.json', file_content = {})
        json_file.save()

    file_path = os.path.join(download_path, json_file.file_name)
    with open(file_path, 'w') as destination:
        json.dump(json_file.file_content, destination)

    if json_file.file_content == {}:
        print("upload_data.json was empty. No data was downloaded.")
        UploadedFile.objects.all().delete()
        return
    
    # Initialize an empty list to hold all file names
    files_to_fetch = []

    data = json_file.file_content

    # Iterate over the dictionary and collect file names
    for user_data in data.values():
        for job_data in user_data.values():
            files_to_fetch.extend(job_data.get("files", []))

    files_to_fetch = list(set(files_to_fetch))

    # Download all uploaded files
    uploaded_files = UploadedFile.objects.filter(file_name__in=files_to_fetch).all()
    UploadedFile.objects.exclude(file_name__in=files_to_fetch).all().delete()


    for uploaded_file in uploaded_files:
        file_path = os.path.join(download_path, uploaded_file.file_name)
        with open(file_path, 'wb') as destination:
            destination.write(uploaded_file.file_content)

    print("These files have been downloaded: " + ",\n".join(file for file in os.listdir(download_path)))
        

def run_startup_tasks(server_start_time):
    print("Run_startup_tasks has been called!")
    if os.path.exists(LOCK_FILE):
        lock_file_mod_time = os.path.getmtime(LOCK_FILE)
        if lock_file_mod_time < server_start_time:
            os.remove(LOCK_FILE)
            print("Lock file is stale and has been removed.")
        else:
            print("Startup tasks have already been run.")
            return
            
    json_file_path = os.path.join(PROCESSING_PATH, 'upload_data.json')

    download_files_from_db()

    User = get_user_model()

    if os.path.exists(json_file_path):
        with open(json_file_path, 'r+') as json_file:
            try:
                jsondata = json.load(json_file)
                for user_key in jsondata.keys():
                    for survey_type_flag in jsondata[user_key].keys():
                        jsondata[user_key][survey_type_flag]['processing'] = False

                json_file.seek(0)
                json.dump(jsondata, json_file, indent=4)
                json_file.truncate()

                for user_key in jsondata.keys():
                    for survey_type_flag in jsondata[user_key].keys():
                        if not jsondata[user_key][survey_type_flag]['processing']:
                            from aecon.views import check_if_still_processing
                            check_if_still_processing(get_object_or_404(User, username=user_key))

                # Create the lock file to indicate that startup tasks have run
                with open(LOCK_FILE, 'w') as lock_file:
                    lock_file.write('done')

            except json.JSONDecodeError:
                print(f"Failed to decode JSON from {json_file_path}. File might be empty or corrupted.")
    else:
        print(f"JSON file not found at {json_file_path}.")
