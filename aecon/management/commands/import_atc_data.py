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
from multiprocessing import Pool
import tkinter as tk
from tkinter import filedialog

BASE_DIR = settings.BASE_DIR

def import_assocaiation (filename, project_no):
    Direction_lst = {'N0':[0,1],'S1':[1,2],'N1':[0,1],'S0':[1,2],'E0': [0,9],'W1':[1,10] ,'E1': [0,9],'W0':[1,10]}

    project = Project.objects.using(DB_NAME).get(project_no = project_no)

    locs = {loc.api_identifier: loc for loc in Location.objects.using(DB_NAME).filter(projects = project,observationType_id = 9 ) }
    class_lst  =  {1:43107,2:43108,3:43109,4:43110,5:43111,6:43112,7:43117,8:43118,9:43119,10:43120,11:43121,12:43122,13:43122}
    class_id = [43107,43108,43109,43110,43111,43112,43117,43118,43119,43120,43121,43122]


    data = pd.read_csv(filename)
    data = data.dropna()
    data['Date'] = data['Date'].apply(lambda date: str(date.split(" ")[0]))

    data['Date']= pd.to_datetime(data['Date'] , format="%Y-%m-%d") # other format that i might need: 1- %m/%d/%Y 2-%Y-%m-%d
    data = data.fillna('')


    for index,row in data.iterrows():

        Datetime = parser.parse(str(row['Date']) + " " + str(row['Time']))
        timezone1 = pytz.timezone("Europe/London")
        Datetime = Datetime.astimezone(timezone1)

        location = Location.objects.using(DB_NAME).get(api_identifier =row['Site_No'] ,observationType_id = 9)

        value = row['Speed']

        tmp_dir = row['Direction'].strip()[0]
        # tmp_dir = row['Direction'].strip()[1]
        # if tmp_dir == 2:
        #     tmp_dir = 0
        # elif tmp_dir == 3:
        #     tmp_dir = 1

        DirectionList = location.directions.all()
        ClassList = location.classes.all()

        loc_class = ClassList.get(location=location, obsClass_id=class_lst[row['Class']])
        loc_dir = DirectionList.filter(direction__abbrev=tmp_dir,).first() # location=location, direction__abbrev=tmp_dir

        # loc_dir = LocationDirection.objects.using(DB_NAME).get(location=location, order=tmp_dir)

        assoc_observation = AssociatedObservation.objects.using(DB_NAME).update_or_create(location = location,date = Datetime,direction = loc_dir ,obsClass =loc_class , project = project, defaults={'location':location, 'value' : value , 'obsClass':loc_class,'date':Datetime,'direction':loc_dir,'project':project, 'is_aggregated': False})
        print("added obesrvation -",index)

    updateaggregatedData(project_no)

        #---------------------------------------------- OLD CODE ----------------------------------------
        # loc_dir = Direction_lst[tmp_dir]

        # loc_dir =  LocationDirection.objects.using(DB_NAME).get_or_create(location = location,direction_id = loc_dir[1],defaults={'location':location,'direction_id': loc_dir[1],'order':loc_dir[0]})
        # loc_dir_combine =  LocationDirection.objects.using(DB_NAME).get_or_create(location = location,direction_id = 15,defaults={'location':location,'direction_id': 15,'order':2})
        #
        #
        # loc_dir = loc_dir[0] if len(loc_dir) > 1  else loc_dir


        # for i in range(len(class_id)):
        #     LocationObservationClass.objects.using(DB_NAME).get_or_create(location = location,obsClass_id = class_id[i] ,order = i, defaults={'location':location,'obsClass_id':class_id[i],'order':i} )
        #
        # loc_class = LocationObservationClass.objects.using(DB_NAME).get(location = location,obsClass_id = class_lst[row['Class']] )

        #------------------------------------------------------------------------------------------------



def updateaggregatedData(projectno,loc_id=None):
    # get all data for a project as it will always calculated for a project.
    sys.setrecursionlimit(10000)
    project  = Project.objects.using(DB_NAME).get(project_no = projectno)
    if loc_id != None:
        locations = Location.objects.using(DB_NAME).filter(projects = project,id = loc_id,observationType_id = 9).prefetch_related()
    else:
        locations = Location.objects.using(DB_NAME).filter(projects = project,observationType_id = 9).prefetch_related()

    for loc in locations:
        observationData = AssociatedObservation.objects.using(DB_NAME).filter(location=loc, project=project, is_aggregated=False)
        if not observationData:
            continue
        else:
            df = pd.DataFrame(list(observationData.values()))
            df['dayofweek'] = df['date'].dt.dayofweek + 1
            df['hour'] = df['date'].dt.hour

            df.drop(['status', 'removed', 'date' , 'obsClass_id' , 'id' ], axis=1, inplace=True)

            days = [1,2,3,4,5,6,7,8,9]
            dirs = loc.ordered_location_direction_queryset()
            for dir in dirs:

                dir_in = [dir.id]
                if dir.order !=2:
                    filtered_dir_df  = df[ (df['direction_id'] == dir.id) ]
                else:
                    filtered_dir_df  = df
                for day in days:
                    minday = day
                    maxday = day
                    if day < 8:
                        filtered_day_df  =   filtered_dir_df[ (filtered_dir_df['dayofweek'] == day)]
                    else:
                        if day == 8:
                            minday = 1
                            maxday = 5
                            filtered_day_df  =   filtered_dir_df[ (filtered_dir_df['dayofweek'] >= minday) & (filtered_dir_df['dayofweek'] <= maxday) ]
                        if day == 9:
                            filtered_day_df = filtered_dir_df
                    for timeval in range(0, 28):
                        timemin = timeval
                        timemax = timeval

                        if timeval < 24:
                            filtered_df =   filtered_day_df[ (filtered_day_df['hour'] == timeval)]

                        else:
                            if timeval == 24:
                                timemin = 7
                                timemax = 19
                            if timeval == 25:
                                timemin = 6
                                timemax = 22
                            if timeval == 26:
                                timemin = 6
                                timemax = 24
                            if timeval == 27:
                                timemin = 0
                                timemax = 24
                            filtered_df =   filtered_day_df[ (filtered_day_df['hour'] >= timemin) & (filtered_day_df['hour'] <= timemax) ]


                        avg =  filtered_df['value'].mean(skipna=True)
                        perc_85th =  filtered_df['value'].quantile(0.85)
                        perc_95th = filtered_df['value'].quantile(0.95)

                        filtered_df = filtered_df.groupby(['location_id',  'project_id' , 'dayofweek']).size().reset_index(name='value')

                        filtered_df =  filtered_df.groupby(['location_id',  'project_id' ], as_index=False).agg({"value": lambda x: x.mean(skipna=True)})

                        counts = 0
                        if len(filtered_df.index) > 1 :
                            print(filtered_df)
                            raise ValueError("count check")
                        elif  len(filtered_df.index) == 0:
                            counts = 0
                        else:
                            counts = filtered_df['value'].iloc[0]


                        avg = round(avg,2) if not np.isnan(float(avg)) else 0
                        perc_85th = round(perc_85th,2) if not np.isnan(float(perc_85th))  else 0
                        perc_95th = round(perc_95th,2) if not np.isnan(float(perc_95th)) else 0

                        print(avg, perc_85th , perc_95th , counts)

                        BordersAggregatedData.objects.using(DB_NAME).update_or_create(location = loc,
                         day = day,direction = dir , project = project, timeval = timeval,
                             defaults={'location':loc, 'day' : day , 'direction':dir,'project': project,'timeval':timeval,
                             'direction':dir,'avg':avg , 'perc_85th' : perc_85th ,'perc_95th':perc_95th , 'phase':1 , 'counts':counts })

            aggregatedObservationData = AssociatedObservation.objects.using(DB_NAME).filter(location=loc, project=project, is_aggregated = False).update(is_aggregated = True)


def import_excel_base(filename):    #for importing locations
    data = pd.read_csv(filename)
    data = data.fillna("")
    # this will replace "Boston Celtics" with "Omega Warrior"
    print(data)
    # data["start_date"].replace({"": None}, inplace=True)
    # data["end_date"].replace({"": None}, inplace=True)
    class_lst = {1:43107,2:43108,3:43109,4:43110,5:43111,6:43112,7:43117,8:43118,9:43119,10:43120,11:43121,12:43122,13:43122}
    class_id = [43107,43108,43109,43110,43111,43112,43117,43118,43119,43120,43121,43122]

    for index,row in data.iterrows():
        # for adding Project
        project = Project.objects.using(DB_NAME).update_or_create(project_no = row['Project_No'].strip(), name= row['Project_No'].strip(),defaults={'survey_type':row['Survey_Type'].strip()})
        project = project[0]
        print(project)
        #-------------------------------------------------------------------------------------------

        #for adding Location
        # obj = ObservationType.objects.using(DB_NAME).update_or_create(name = row['Survey_Type'].strip(),defaults={'name':row['Survey_Type'].strip()})
        obj = 9

        primaryDir  = Direction.objects.using(DB_NAME).get(descriptive =  row['Primary'].strip())
        secDir  = Direction.objects.using(DB_NAME).get(descriptive =  row['Secondary'].strip())
        Combined  = Direction.objects.using(DB_NAME).get(id = 15)
        dir_lst = [primaryDir,secDir , Combined]

        location = Location.objects.using(DB_NAME).get_or_create(observationType_id = obj ,
                                                                 api_identifier =row['Site_No'] ,
                                                                 defaults={'name': row['Site_Name'].strip(),
                                                                 'observationType_id':obj,
                                                                 'api_identifier' : row['Site_No'] ,
                                                                 'lat':row['Lat'],
                                                                 'lon':row['Long'],
                                                                 'speedLimit':row['Speed_Limit']})
        location = location[0]

        ## For adding the location to the client
        client = Client.objects.using(DB_NAME).get(id=18)
        client.locations.add(location)

        project = Project.objects.using(DB_NAME).get(project_no= row['Project_No'].strip())
        startDate = datetime.datetime.strptime(str(row['startDate']),"%Y-%m-%d").date() # 1- %Y-%m-%d, 2- %m/%d/%Y
        endDate = datetime.datetime.strptime(str(row['endDate']),"%Y-%m-%d").date()

        pro_loc = ProjectLocations.objects.using(DB_NAME).update_or_create(location=location, project=project,
                                                                                   defaults={'location': location,
                                                                                             'speed_limit': row['Speed_Limit'],
                                                                                             'project': project,
                                                                                             'startDate': startDate,
                                                                                             'endDate': endDate})

        for i in range(len(class_id)):
            LocationObservationClass.objects.using(DB_NAME).get_or_create(location = location,obsClass_id = class_id[i] ,order = i, defaults={'location':location,'obsClass_id':class_id[i],'order':i} )

        # ----------------------------------------------------------------------------------------------

        # for mapping of location direction

        # loc_dir = []
        for i in range(len(dir_lst)):
            print(dir_lst[i])
            print(location)
            print(i)
            # direction_id = dir_lst[i].id,
            temp = LocationDirection.objects.using(DB_NAME).get_or_create(location = location,order = i,defaults={'location':location,'direction_id':dir_lst[i].id,'order':i})
            # loc_dir.append(temp[0])
        # ----------------------------------------------------------------------------------------------

        print("Added loc - ",location)
        print("-----------------------------------------------------")


def test(filename,siteno=None,projectno=None):
    class_lst  =  {1:43103,2:43104,3:43104,4:43105,5:43105,6:43106,7:43106,8:43106,9:43106,10:43106,11:43106,12:43106,13:43106}
    location_dir  = LocationDirection.objects.using(DB_NAME).filter( location_id = siteno).values('id','order')
    print(location_dir)
    def set_date_formate(date):
        return datetime.datetime.strptime(date, '%d/%m/%Y %H:%M:%S').replace(tzinfo=pytz.UTC)
    df = pd.read_csv(filename)
    df['Date'] = df['Date'].astype(str) + " " + df['Time'].astype(str)
    df['Date']=df['Date'].apply(set_date_formate)
    df.drop(['Time','Scheme','Site_No','Project_No','Survey_Type','Client_ID'],axis=1,inplace=True)
    print(df.columns)
    # df['Class'] = np.where(df['Class'] in class_lst.keys(),class_lst[df['Class']] , 0)
    df['Class'] = df['Class'].apply(lambda a: class_lst[a])
    # print(LocationDirection.objects.using(DB_NAME).get( location_id = siteno,order = a.strip()[-1] ).id)
    test = df['Direction'].apply(lambda a: [x for x in location_dir if x['order'] == a.strip()[-1]])
    print(test)

    print(df)
    exit()



    db_data = AssociatedObservation.objects.using(DB_NAME).filter( location_id  = siteno, project = projectno).values('date','value','obsClass','direction')
    print(df['Date'][0])
    db_date = [i['date'] for i in db_data]
    print(type(db_data[0]['date']))


    # df = df[df['Site_No'] == siteno]
    # df.drop(['Time'], axis=1, inplace=True)
    #
    # # df['Time'] = pd.to_datetime(df['Time'],format= '%H:%M:%S' ).dt.time
    # start_date = parser.parse(str(df['Date'].min()))
    # end_date = parser.parse(str(df['Date'].max()))
    # df = df[df['Date']==start_date]

    # df = df[df['Class']==1]


    # print(start_date,end_date)

class Command(BaseCommand):
    help = "Command to import excel file to DB for Project"

    def handle(self, *args, **kwargs):

        # location = Location.objects.using(DB_NAME).get(api_identifier=1, observationType_id=9)
        # DirectionList = location.directions.all()
        #
        # loc_dir = DirectionList.filter(location=location,order=2).first()
        # print(loc_dir)

        #-------------for setting is_aggregated from None to False for newly added observations-----------------

        # project = Project.objects.using(DB_NAME).get(project_no='3928-SCO-S1')
        # locations = Location.objects.using(DB_NAME).filter(observationType_id=9).prefetch_related() #projects= project,
        #
        # for loc in locations:
        #     observationData = AssociatedObservation.objects.using(DB_NAME).filter(location=loc,
        #                                                                           is_aggregated=True).update(is_aggregated=False)



            # print(pd.DataFrame(list(observationData.values())))

        # sitecsv_path = filedialog.askopenfilename()
        # datacsv_path = filedialog.askopenfilename()
        # print(sitecsv_path)
        #--------------------------------------------------------------------------------------------------------

        #------------for dynamiclly uploading combined observations or sites from .csv file----------------------

        root = tk.Tk()
        root.withdraw()
        root.call('wm', 'attributes', '.', '-topmost', True)

        project_directory = filedialog.askdirectory()
        new_site_path = os.path.join(project_directory, "Raw_sites.csv")
        new_data_path = os.path.join(project_directory, "Raw_Data.csv")
        files_needed = []

        # Lists out the paths for all the files in the project
        for subdir, dirs, files in os.walk(project_directory):
            for filename in files:
                filepath = subdir + os.sep + filename
                if filepath.endswith(".xlsx"):
                    files_needed.append(filepath)

        # Site Details
        site_for_DB = pd.DataFrame(
            columns=['Site_ID', 'Project_No', 'Site_No', 'Site_Name', 'Survey_Type', 'Lat', 'Long', 'Speed_Limit',
                     'Primary', 'Secondary', 'startDate', 'endDate'])

        # Hard Coded as all same survey type and no arms for ATC survey
        default_survey_type = 'ATC'

        # Scheme and Client_ID are hardcoded as well remain constant for this project
        default_scheme = 'ARX'
        project_name = str(files_needed[0]).split("\\")[-1].split("_")[0].split(" ")[-1]
        default_client_id = project_name

        for i in files_needed:
            # Can mostly be read in from dashboard tab
            xlsx = pd.ExcelFile(i)

            metadata = xlsx.parse('Dashboard', skipfooter=24)
            directiondata = xlsx.parse('Raw Data - To Be Deleted At End', skipfooter=24)

            # Extracting key values
            site_name = metadata.iat[2, 20]
            site = site_name.split(" - ")

            site_no = int(site[0])

            project = metadata.iat[1, 20]
            project_no = project[0: 8]

            site_id = project_no + '-' + default_survey_type + '-' + str(site_no)

            lat = metadata.iat[1, 6]
            long = metadata.iat[1, 7]

            speed_limit = metadata.iat[4, 20]

            date = metadata.iat[3, 19]

            if directiondata.iloc[0, 11][0] == 'N':
                primary_direct = 'Northbound'
            elif directiondata.iloc[0, 11][0] == 'S':
                primary_direct = 'Southbound'
            elif directiondata.iloc[0, 11][0] == 'E':
                primary_direct = 'Eastbound'
            elif directiondata.iloc[0, 11][0] == 'W':
                primary_direct = 'Westbound'

            if directiondata.iloc[1, 11][0] == 'N':
                second_direct = 'Northbound'
            elif directiondata.iloc[1, 11][0] == 'S':
                second_direct = 'Southbound'
            elif directiondata.iloc[1, 11][0] == 'E':
                second_direct = 'Eastbound'
            elif directiondata.iloc[1, 11][0] == 'W':
                second_direct = 'Westbound'

            date_data = directiondata.iloc[8:, 0]
            date_data = date_data.dropna()
            date_data = date_data.apply(lambda date: datetime.datetime.strptime(str(date)[:-9], '%Y-%m-%d'))
            start_date = parser.parse(str(date_data.min()))
            end_date = parser.parse(str(date_data.max()))

            # Creating dataframe of relevant values
            complete_data_list = [site_id, project_no, site_no, site_name, default_survey_type, lat, long, speed_limit,
                                  primary_direct, second_direct, start_date, end_date]

            site_for_DB.loc[0] = complete_data_list

            # Raw Data
            # Majority of data can be used as is
            rawdata = xlsx.parse('Raw Data - To Be Deleted At End', header=8)  # Dropping Blank Rows at Top
            rawdata = rawdata.iloc[:, :9]  # Dropping the Blank Columns

            rawdata = rawdata.assign(Scheme=default_scheme)
            rawdata = rawdata.assign(Site_No=site_no)
            rawdata = rawdata.assign(Project_No=project_no)
            rawdata = rawdata.assign(Survey_Type=default_survey_type)
            rawdata = rawdata.assign(Client_ID=default_client_id)

            # Writing to Excel File
            with pd.ExcelWriter(xlsx, mode='a', engine="openpyxl") as writer:
                site_for_DB.to_excel(writer, sheet_name='site_for_DB', index=False)
                rawdata.to_excel(writer, sheet_name='raw_data_for_DB', index=False)

            print("Writing Complete for: " + i)

        files_needed2 = []

        # Lists out the paths for all the files in the project
        for subdir, dirs, files in os.walk(project_directory):
            for filename in files:
                filepath = subdir + os.sep + filename
                if filepath.endswith(".xlsx"):
                    files_needed2.append(filepath)

        New_site_for_DB = pd.DataFrame(
            columns=['Site_ID', 'Project_No', 'Site_No', 'Site_Name', 'Survey_Type', 'Lat', 'Long', 'Speed_Limit',
                     'Primary', 'Secondary', 'startDate', 'endDate'])

        New_Raw_data_for_DB = pd.DataFrame(
            columns=['Date', 'Time', 'Direction', 'Speed', 'Class', 'Scheme', 'Site_No', 'Project_No', 'Survey_Type',
                     'Client_ID'])

        for i in files_needed2:
            xlsx = pd.ExcelFile(i)
            print(xlsx.sheet_names)

            df1 = xlsx.parse('site_for_DB')
            df2 = xlsx.parse('raw_data_for_DB')

            New_site_for_DB = pd.concat([New_site_for_DB, df1])

            New_Raw_data_for_DB = pd.concat([New_Raw_data_for_DB, df2])

            New_site_for_DB.to_csv(new_site_path)
            New_Raw_data_for_DB.to_csv(new_data_path)

        # Code for site----------------
        #
        import_excel_base(new_site_path)
        # -----------------------------

        # Code for raw data------------

        import_assocaiation(new_data_path, project_name)
        # -----------------------------

        #--------------------------------------------------------------------------------------------------------

        # ----for explicitly aggregating the data (if there is no location, the whole project will be taken------

        # for i in range(1, 6):
        #     updateaggregatedData('3928-SCO-S'+str(i))

        # --------------------------------------------------------------------------------------------------------


        #     import_assocaiation_byLocation("projects/3986-SCO/Raw_data_for_DB-DB2021-04RawSite"+ str(i) +".csv" ,'3986-SCO',i)
