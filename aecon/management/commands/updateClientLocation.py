from django.conf import settings
from django.core.management.base import BaseCommand
from schoolstreets.models import Client, Location, ObservationClass, LocationObservationClass, LocationDirection, Direction
DB_NAME = settings.DB_NAME
obs_id = [43073,43097,43098,43099,43100,43101,43102]
order_id = [0,1,2,3,4,5,6]
location_id = []
direction = []
direction_order = [1,0]
direction.append(Direction.objects.using(DB_NAME).get(id=3))
direction.append(Direction.objects.using(DB_NAME).get(id=4))
for i in range(77,90):
    location_id.append(i)

class Command(BaseCommand):
    help = "Update list of client location."

    def handle(self, *args, **kwargs):
        loc_list = Location.objects.using(DB_NAME).filter(id__in=location_id)
        for loc in loc_list:
            for i in range(2):
                LocationDirection.objects.using(DB_NAME).create(order=direction_order[i],direction=direction[i],location=loc)

        
        #to input obsclass***
        # obs_list = ObservationClass.objects.using(DB_NAME).filter(id__in=obs_id).order_by('id')
        # loc_list = Location.objects.using(DB_NAME).filter(id__in=location_id)
        #     for i in range(len(order_id)):
        #         order = order_id[i]
        #         obs = obs_list[i]
        #         LocationObservationClass.objects.using(DB_NAME).create(order=order,obsClass=obs,location=loc)
        # location_list = Location.objects.using(DB_NAME).all()
        # # client.locations.all().delete()
        # # client.locations.add(location_list)
        # print(len(location_list))
