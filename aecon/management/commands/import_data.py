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

    locs = {loc.api_identifier: loc for loc in Location.objects.using(DB_NAME).filter(projects = project,observationType_id = 1 ) }
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

        location = Location.objects.using(DB_NAME).get(api_identifier =row['Site_No'] ,observationType_id = 1)

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


# file_for_Location,
def import_assocaiation_byLocation(filename,project_no,loc=None,speed_limit=None):
    print('started')

    # locs = {loc.api_identifier: loc for loc in Location.objects.using(DB_NAME).filter(projects = project,observationType_id = 9 ) }
    # class_lst  =  {1:43103,2:43104,3:43104,4:43105,5:43105,6:43106,7:43106,8:43106,9:43106,10:43106,11:43106,12:43106,13:43106}
    # class_id = [43103,43104,43105,43106]
    class_lst  =  {1:43107,2:43108,3:43109,4:43110,5:43111,6:43112,7:43117,8:43118,9:43119,10:43120,11:43121,12:43122,13:43122}
    class_id = [43107,43108,43109,43110,43111,43112,43117,43118,43119,43120,43121,43122]
    speed_limit = speed_limit if speed_limit else 30

    project  = Project.objects.using(DB_NAME).get_or_create(project_no = project_no,defaults={'project_no':project_no,'name':project_no,'survey_type':'ATC'})

    project = project[0]
    print('got project',project)
    # is_loc_there = Location.objects.using(DB_NAME).filter(api_identifier=loc).first()
    # if is_loc_there == None:
    #     import_ATCfromSite(file_for_Location, loc)

    location = Location.objects.using(DB_NAME).get(api_identifier = loc ,observationType_id = 9)
    print(location)
    print('got location',location)
    print("locations ended")




    # def set_date_formate(date):
    #     return datetime.datetime.strptime(str(date), '%d/%m/%Y %H:%M:%S').replace(tzinfo=pytz.UTC)


    data = pd.read_csv(filename)
    # data = data.fillna('')
    data=data.dropna()
    data = data.fillna('')

    data['Date'] = data['Date'].apply(lambda date : datetime.datetime.strptime(str(date), "%Y-%m-%d").date())


    # data['Time'] = pd.to_datetime(data['Time'],format= '%H:%M:%S' ).dt.time
    # start_date = parser.parse(str(data.head(1)['Date'].values[0]))
    # end_date = parser.parse(str(data.tail(1)['Date'].values[0]))
    start_date = parser.parse(str(data['Date'].min()))
    end_date = parser.parse(str(data['Date'].max()))
    # data = data.sort_values(by=['Date','Time'])
    pro_loc = ProjectLocations.objects.using(DB_NAME).update_or_create(location = location,project = project, defaults={'location':location, 'speed_limit' : speed_limit ,'project':project,'startDate':start_date,'endDate':end_date})

    print("project _locations - ",pro_loc)

    for index,row in data.iterrows():
        print("at index-",index+1)
        # print(row)
        if (int(row['Speed']) == 0):
            continue

        DirectionList = location.directions.all()
        # print(DirectionList)
        ClassList = location.classes.all()
        # print(ClassList)
        Datetime = parser.parse(str(row['Date']) + " " + str(row['Time']))
        Datetime  = Datetime.replace(tzinfo=pytz.utc)
        value  = row['Speed']

        # dirOder = row['Direction'].strip()[-1]
        # loc_dir  = DirectionList.filter(order=dirOder).first()
        dir_abbr = row['Direction'].strip()[0]
        loc_dir = DirectionList.filter(direction__abbrev=dir_abbr).first()
        loc_class = ClassList.get(location = location,obsClass_id = class_lst[row['Class']] )
        assoc_observation = AssociatedObservation.objects.using(DB_NAME).create(location = location,date = Datetime,direction = loc_dir ,obsClass =loc_class , project = project,value = value)
        print("added - ",assoc_observation)
    updateaggregatedData(project.project_no,location.id)



def updateaggregatedData(projectno,loc_id=None):
    # get all data for a project as it will always calculated for a project.
    sys.setrecursionlimit(10000)
    project  = Project.objects.using(DB_NAME).get(project_no = projectno)
    if loc_id != None:
        locations = Location.objects.using(DB_NAME).filter(projects = project,id = loc_id,observationType_id = 1).prefetch_related()
    else:
        locations = Location.objects.using(DB_NAME).filter(projects = project,observationType_id = 1).prefetch_related()

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
        obj = 1

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

def import_sensor_data(filename):
    data = pd.read_excel(filename)
    data = data.fillna("")
    # data['Start Receiving Date'].apply(datetime)
    print(data['Start Receiving Date'][1])
    data['Install Date'] = pd.to_datetime(data['Install Date'] , format="%d/%m/%Y")
    data['Start Receiving Date'] = pd.to_datetime(data['Start Receiving Date'] ,format="%d/%M/%Y")
    # this will replace "Boston Celtics" with "Omega Warrior"

    dirs = [9,10]
    classes  = [1,2,3,4,5,167,168,169,170,171,172]
    obj = 1
    vivacity_api = 6
    client_id = 18

    for index,row in data.iterrows():
        print(row)


        lat  = row['Lat/long'].split(",")[0]
        lon = row['Lat/long'].split(",")[1]





        location = Location.objects.using(DB_NAME).update_or_create(name = row['Countline Name'].strip(),
                                                                 observationType_id = obj,
                                                                 defaults={'name': row['Countline Name'].strip(),
                                                                 'installDate':row['Install Date'],
                                                                 'startRecievingDate': row['Start Receiving Date'],
                                                                 'observationType_id':obj,
                                                                 'vivacity_sensor_id' : None ,
                                                                 'api_identifier':row['Countline ID'],
                                                                 'lat':lat,
                                                                 'lon':lon})

        location = location[0]

        client = Client.objects.using(DB_NAME).get(id=client_id)
        client  = client.locations.add(location)


        for i in range(len(dirs)):
           loc_dir = LocationDirection.objects.using(DB_NAME).get_or_create(location = location,direction_id = dirs[i],order = i,defaults={'location':location,'direction_id':dirs[i],'order':i})
           print(loc_dir)

        for i in range(len(classes)):
            loc_cls  = LocationObservationClass.objects.using(DB_NAME).get_or_create(location = location,obsClass_id = classes[i] ,order = i, defaults={'location':location,'obsClass_id':classes[i],'order':i} )

            print(loc_cls)
        api = VivacityAPI.objects.using(DB_NAME).get(id = vivacity_api)
        api.locations.add(location)
        print("Added loc - ",location)
        print("*********************************************************")


def export_sheet_by_siteno(filename,siteno=None,projectno=None):
    df = pd.read_csv(filename)
    df  = df.groupby(['Site_No'])
    # print(df.groups.keys())
    if siteno is not None:
        if type(siteno) != list :
            print("Exporting data for site no - ",siteno)
            data = df.get_group(int(siteno))
            data.to_csv("D:\python\webapps\webapps_EastLothian\East-Lothian\projects\current_project\\"+str(projectno)+".csv")
        elif type(siteno) == list :
            for site in siteno:
                print("Exporting data for site no - ",site)
                data = df.get_group(int(site))
                data.to_csv("D:\python\webapps\webapps_EastLothian\East-Lothian\projects\current_project\\"+str(site)+".csv")
    else:
        for key in df.groups.keys():
            data = df.get_group(key)
            data.to_csv("D:\python\webapps\webapps_EastLothian\East-Lothian\projects\current_project\\"+str(key)+".csv")

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
        class_lst = {43107: 1, 43108: 2, 43109: 3, 43110: 4, 43111: 5,43112: 6,43117: 7,43118: 8, 43119: 9,
                     43120: 10, 43121: 11, 43122: 12}
        dir_lst = {1: 'N', 2: 'S', 9: 'E', 10: 'W'}

        observations = AssociatedObservation.objects.using(DB_NAME).filter(location_id=339, project=15).values('date','value','obsClass','direction')

        db_df = pd.DataFrame(list(observations.all()))
        obs_classes = sorted(db_df.obsClass.unique())
        obs_directions = sorted(db_df.direction.unique())

        location = Location.objects.using(DB_NAME).get(id=339)
        DirectionList = location.directions.filter(id__in=obs_directions).values("direction_id", "order")
        ClassList = location.classes.filter(id__in=obs_classes).values("obsClass_id")

        classes_mapping = {}
        directions_mapping = {}

        for i in range(len(obs_directions)):
            try:
                directions_mapping[obs_directions[i]] = dir_lst[DirectionList[i]["direction_id"]] + str(DirectionList[i]["order"])
            except:
                print("wrong observation direction value")


        for i in range(len(obs_classes)):
            try:
                classes_mapping[obs_classes[i]] = class_lst[ClassList[i]["obsClass_id"]]
            except:
                print("wrong observation class value")

        df_to_download = pd.DataFrame(columns=["Date", "Time", "Direction", "Speed", "Class"])

        try:
            df_to_download['Date'] = pd.to_datetime(db_df['date']).dt.date
            df_to_download['Time'] = pd.to_datetime(db_df['date']).dt.time
        except:
            print("dt.time is not working")

        df_to_download['Speed'] = db_df['value']

        for i in range(len(df_to_download)):
            df_to_download.loc[i, "Direction"] = directions_mapping[db_df.loc[i, "direction"]]
            df_to_download.loc[i, "Class"] = classes_mapping[db_df.loc[i, "obsClass"]]

        print(df_to_download)

        project_name_part = "20mph AECON"

