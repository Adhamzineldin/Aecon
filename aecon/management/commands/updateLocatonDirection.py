from django.conf import settings
from django.core.management.base import BaseCommand
from schoolstreets.models import Client, Location, ObservationClass, LocationObservationClass, LocationDirection, Direction
DB_NAME = settings.DB_NAME
obs_id = [43073,43097,43098,43099,43100,43101,43102]
obs_name = ["Pedestrian","Cyclist","Motorbike","Car","Taxi","Van","Minibus","Bus","Rigid","Truck","Emergency_Car","Emergency_Van","Fire Engine"]
location_id = []
for i in range(1,77):
    location_id.append(i)

class Command(BaseCommand):
    help = "Update list of client location."

    def handle(self, *args, **kwargs):
        for loc in location_id:
            for i in range(len(obs_name)):
                print(obs_name[i])
                obs_id = ObservationClass.objects.using(DB_NAME).get(name__iexact=obs_name[i]).id
                LocationObservationClass.objects.using(DB_NAME).create(order=i,location_id=loc,obsClass_id=obs_id)