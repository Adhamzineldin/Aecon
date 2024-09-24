import os
import django
import sys
path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if path not in sys.path:
    sys.path.append(path)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "webapps.settings")
django.setup()
from aecon.views import *

def  update_location_cordinate(api,locs):
    print(locs)
    token = tracsis_api_helpers.get_vivacity_auth_token(api.username, api.password)
    countlines = [x.api_identifier for x in locs]
    countlines  = ",".join(countlines)
    countlines = tracsis_api_helpers.get_vivacity_countlines(countlines, token)
    for count in countlines:
       print(count['id'])
       lat = count['location']['start']['lat']
       lon = count['location']['start']['long']
       loc = Location.objects.using(DB_NAME).get(api_identifier=count['id'])
       loc.lat = lat
       loc.lon = lon
       loc.save(using=DB_NAME)
       
       print(loc.api_identifier,loc.lat == lat ,loc.lat,loc.lon == lon ,loc.lon)
       
    #    .update(lat=lat,lon=lon)
       

    
if __name__ == '__main__':
    #update_location_cordinate()
    api = VivacityAPI.objects.using(DB_NAME).get(id=6)
    locs  = api.locations.all()
    update_location_cordinate(api,locs)


# response = tracsis_api_helpers.get_vivacity_data(token, startDate, startDate + datetime.timedelta(days=1), loc.api_identifier)