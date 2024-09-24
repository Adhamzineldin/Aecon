from django.contrib import admin
from .models import Location, Client, LocationObservationClass, LocationDirection

# Register your models here.
admin.site.register(Location)
admin.site.register(Client)
admin.site.register(LocationObservationClass)
admin.site.register(LocationDirection)
