import warnings
from ast import Raise
import itertools
import operator
from django.conf import settings
from django.core.management.base import BaseCommand
from datetime import datetime
from aecon.models import *
import pandas as pd
import pytz
from dateutil import parser
import tkinter as tk
from tkinter import filedialog

BASE_DIR = settings.BASE_DIR


def import_link_associated_observations(data_filename):
    warnings.filterwarnings('ignore')

    link_data = pd.read_csv(data_filename)
    link_data = link_data.dropna()
    sites_list_of_dicts = []

    for index, row in link_data.iterrows():
        test_location = Location.objects.using(DB_NAME).get(api_identifier=row['SiteNo'], observationType_id=10)
        observations_exists = LINKObservation.objects.using(DB_NAME).filter(location=test_location)
        if not observations_exists:
            sites_dict = {
                "location": test_location,
                "data_exist": False
            }
        else:
            sites_dict = {
                "location": test_location,
                "data_exist": True
            }
        sites_list_of_dicts.append(sites_dict)

    link_data = link_data.melt(id_vars=['SiteNo', 'Movement', 'SiteLocation', 'SurveyType', 'Date', 'Time'],
                               var_name="Obs_Class",
                               value_name="Value")

    link_data['Date'] = pd.to_datetime(link_data['Date'], format="%d/%m/%Y")
    link_data['Time'] = pd.to_datetime(link_data['Time'], format='%H:%M:%S')
    link_data['Date'] = link_data['Date'].dt.strftime("%d/%m/%Y")
    link_data['Time'] = link_data['Time'].dt.strftime("%H:%M:%S")

    class_lst = {'P/C': 43123, 'M/C': 43124, 'Car': 3, 'LGV': 43125, 'HGV 2X': 43126, 'HGV 3X': 43127, 'HGV 4x': 43128,
                 'HGV 5+X': 43130, 'Dbus': 43131, 'Obus': 43132, 'Taxi': 167, 'Ped': 1, 'eScooter': 43133,
                 'VehTotal': 43134}

    link_data = link_data.fillna('')

    print(link_data)
    for i in range(0, len(link_data.index), 50000):
        sub_data = link_data[i:i + 50000]
        out = []
        for index, row in sub_data.iterrows():
            date_time = parser.parse(str(row['Date']) + " " + str(row['Time']))

            location = Location.objects.using(DB_NAME).get(api_identifier=row['SiteNo'], observationType_id=10)

            value = row['Value']

            tmp_dir = row['Movement'].strip()[0]

            DirectionList = location.directions.all()
            ClassList = location.classes.all()

            loc_class = ClassList.get(location=location, obsClass_id=class_lst[row['Obs_Class']])

            # other implementation location=location, direction__abbrev=tmp_dir
            loc_dir = DirectionList.filter(direction__abbrev=tmp_dir, ).first()

            flagg = list(filter(lambda obj: obj["location"] == location, sites_list_of_dicts))

            if not flagg[0]['data_exist']:
                link_observation = LINKObservation(location=location, date=date_time, direction=loc_dir,
                                                   obsClass=loc_class, value=value)
                out.append(link_observation)
                print("added observation - ", index, " to the array")
            else:
                LINKObservation.objects.using(DB_NAME).update_or_create(location=location,
                                                                        date=date_time,
                                                                        direction=loc_dir,
                                                                        obsClass=loc_class,
                                                                        value=value,
                                                                        defaults={'location': location,
                                                                                  'value': value,
                                                                                  'obsClass': loc_class,
                                                                                  'date': date_time,
                                                                                  'direction': loc_dir, })
                print("added observations -", index, " to the database")

        if out:
            print("successfully appended observations")
            try:
                print("adding ", len(out), "observations")
                LINKObservation.objects.using(DB_NAME).bulk_create(out, batch_size=1000,
                                                                   ignore_conflicts=False)
                print("successfully added observations")
            except django.db.IntegrityError as e:
                print("counts were already in the database")
            except Exception as e:
                print(e)
                print("something went wrong when adding observations")
                raise django.db.Error("Failed to write data to database " + str(e))
        else:
            print("Data Already Exists for this project and location - Used update_or_create method")


def import_atc_excel_base(filename):  # for importing locations
    data = pd.read_csv(filename)
    data = data.fillna("")

    print(data)

    class_id = [43107, 43108, 43109, 43110, 43111, 43112, 43117, 43118, 43119, 43120, 43121, 43122]

    for index, row in data.iterrows():
        # for adding Project
        project = Project.objects.using(DB_NAME).update_or_create(project_no=row['Project_No'].strip(),
                                                                  name=row['Project_No'].strip(),
                                                                  defaults={'survey_type': row['Survey_Type'].strip()})
        project = project[0]
        print(project)
        # -------------------------------------------------------------------------------------------

        # for adding Location
        # obj = ObservationType.objects.using(DB_NAME).update_or_create(name = row['Survey_Type'].strip(),defaults={'name':row['Survey_Type'].strip()})
        obj = 9

        primaryDir = Direction.objects.using(DB_NAME).get(descriptive=row['Primary'].strip())
        secDir = Direction.objects.using(DB_NAME).get(descriptive=row['Secondary'].strip())
        Combined = Direction.objects.using(DB_NAME).get(id=15)
        dir_lst = [primaryDir, secDir, Combined]

        location = Location.objects.using(DB_NAME).get_or_create(observationType_id=obj,
                                                                 api_identifier=row['Site_No'],
                                                                 defaults={'name': row['Site_Name'].strip(),
                                                                           'observationType_id': obj,
                                                                           'api_identifier': row['Site_No'],
                                                                           'lat': row['Lat'],
                                                                           'lon': row['Long'],
                                                                           'speedLimit': row['Speed_Limit']})
        location = location[0]

        # For adding the location to the client
        client = Client.objects.using(DB_NAME).get(id=18)
        client.locations.add(location)

        project = Project.objects.using(DB_NAME).get(project_no=row['Project_No'].strip())
        startDate = datetime.datetime.strptime(str(row['startDate']), "%Y-%m-%d").date()  # 1- %Y-%m-%d, 2- %m/%d/%Y
        endDate = datetime.datetime.strptime(str(row['endDate']), "%Y-%m-%d").date()

        ProjectLocations.objects.using(DB_NAME).update_or_create(location=location, project=project,
                                                                 defaults={'location': location,
                                                                           'speed_limit': row['Speed_Limit'],
                                                                           'project': project,
                                                                           'startDate': startDate,
                                                                           'endDate': endDate})

        for i in range(len(class_id)):
            LocationObservationClass.objects.using(DB_NAME).get_or_create(location=location, obsClass_id=class_id[i],
                                                                          order=i, defaults={'location': location,
                                                                                             'obsClass_id': class_id[i],
                                                                                             'order': i})

        # ----------------------------------------------------------------------------------------------

        # for mapping of location direction

        # loc_dir = []
        for i in range(len(dir_lst)):
            print(dir_lst[i])
            print(location)
            print(i)
            # direction_id = dir_lst[i].id,
            LocationDirection.objects.using(DB_NAME).get_or_create(location=location, order=i,
                                                                   defaults={'location': location,
                                                                             'direction_id': dir_lst[i].id,
                                                                             'order': i})
            # loc_dir.append(temp[0])
        # ----------------------------------------------------------------------------------------------

        print("Added loc - ", location)
        print("-----------------------------------------------------")


class Command(BaseCommand):
    help = "Command to import excel file to DB for Project"

    def handle(self, *args, **kwargs):
        root = tk.Tk()
        root.withdraw()
        root.call('wm', 'attributes', '.', '-topmost', True)

        file_directory = filedialog.askopenfilename()
        import_link_associated_observations(file_directory)
