from django import forms
from django.forms import ModelForm
from .models import *


class LocationForm(ModelForm):
    class Meta:
        model = Location
        fields = ["id","name","area","observationType","installDate","device","lat","lon","imgURL"]
