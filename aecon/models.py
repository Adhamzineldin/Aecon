from django.db.transaction import atomic
from contextlib import contextmanager
from distutils.log import error
from webapps.settings import BASE_URL
from django.db import models, transaction
from django.conf import settings
from django.template import loader
# import tracsis_api_helpers
from . import tracsis_api_helpers
import requests
import json
import datetime
# from automatedemails import sendMail
from . import automatedemails
import pytz
import copy
import django
import geojson
from django.db.models.query import QuerySet
from django.db.models import Avg, Value, CharField, F, Sum, Count, IntegerField, Min, Max, Func, Case, When
from django.db.models.functions import Coalesce, Concat, Extract, TruncDate
from django.http import HttpResponse, JsonResponse, Http404, HttpResponseRedirect, HttpResponseForbidden, \
    HttpResponseBadRequest, HttpResponseServerError
import base64
from django.core.validators import URLValidator
from django.forms.models import model_to_dict
from rest_framework import serializers
import pandas as pd
import numpy as np
import random
import time
from django.db import connections
import xlrd
from django.contrib.auth.models import User
from django.core.cache import caches
# Create your models here.
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db.models.query import prefetch_related_objects
from contextlib import closing
from django.db.models import OuterRef, Subquery, Prefetch
from collections import OrderedDict
import threading
from scipy.integrate import quad
import sys
from bulk_update_or_create import BulkUpdateOrCreateQuerySet
import os

DB_NAME = settings.DB_NAME
SEND_MAIL_TO = settings.SEND_MAIL_TO
BASE_DIR = settings.BASE_DIR

classColors = ["#3e95cd", "#8e5ea2", "#3cba9f", "#e8c3b9", "#c45850", "#4286f4", "#60db97", "#ff3333", "#00ccff",
               "#ffff00", "#669999", "#999900",
               "#3e95cd", "#8e5ea2", "#3cba9f", "#e8c3b9", "#c45850", "#4286f4", "#60db97", "#ff3333", "#00ccff",
               "#ffff00", "#669999", "#999900"]


def normalProbabilityDensity(x):
    constant = 1.0 / np.sqrt(2 * np.pi)
    return (constant * np.exp((-x ** 2) / 2.0))


@contextmanager
def lock(key):
    pk = ThreadSafe.objects.using(DB_NAME).get_or_create(key=key)[0].pk
    try:
        objs = ThreadSafe.objects.using(
            DB_NAME).filter(pk=pk).select_for_update()
        with atomic(using=DB_NAME):
            list(objs)
            yield None
    finally:
        pass


def chunk(l, n):
    n = max(1, n)
    return (l[i:i + n] for i in range(0, len(l), n))


def convert_naive_date_to_timezone_then_utc(d, timezone="Europe/London"):
    d = pytz.timezone(timezone).localize(d)
    d = d.astimezone(pytz.utc)
    return d


def clean_text(text):
    return bytes(text, "utf-8", errors='ignore').decode("utf-8", errors='ignore')


def query_count_all():
    query_total = 0
    for c in connections.all():
        # print(c)
        for item in c.queries:
            print(item)
        query_total += len(c.queries)
    return query_total


def get_xth_percentile_by_direction(df, perc, numDirections):
    result = [0 for i in range(numDirections + 1)]
    if len(df) != 0:
        vals = df.groupby(["location", "directionorder"], as_index=False).quantile(perc).drop(["classorder"],
                                                                                              axis=1).reset_index()[
            ["location", "directionorder", "value"]].values.tolist()
        combined = df.groupby("location").quantile(
            perc).drop(["classorder"], axis=1).reset_index()
        combined["directionorder"] = "Combined"
        vals = vals + combined[["location",
                                "directionorder", "value"]].values.tolist()
        for item in vals:
            if item[1] == "Combined":
                result[-1] = item[2]
            else:
                result[item[1]] = item[2]
    return [round(r, 2) for r in result]


def get_average_speed_by_direction(df, numDirections):
    result = [0 for i in range(numDirections + 1)]
    if len(df) != 0:
        vals = df.groupby(["location", "directionorder"], as_index=False).agg({"value": "mean"})[
            ["location", "directionorder", "value"]].values.tolist()
        combined = df.groupby("location", as_index=False).agg(
            {"value": "mean", "directionorder": "first"})
        combined["directionorder"] = "Combined"
        vals = vals + combined[["location",
                                "directionorder", "value"]].values.tolist()
        # print("vakls are",vals)
        for item in vals:
            if item[1] == "Combined":
                result[-1] = item[2]
            else:
                result[item[1]] = item[2]
    return [round(r, 2) for r in result]


def get_percent_over_speed_limit_by_direction(df, speedLimit, numDirections):
    result = [0 for i in range(numDirections + 1)]
    if len(df) != 0:
        counts = df.loc[df["value"] > speedLimit].groupby(["location", "directionorder"])[
            "value"].count().reset_index()[["location", "directionorder", "value"]].values.tolist()
        combined = df.loc[df["value"] > speedLimit].groupby(
            ["location"])["value"].count().reset_index().values.tolist()
        for c in combined:
            c.insert(1, "Combined")
        sizes = df.groupby(["location", "directionorder"]
                           ).size().reset_index().values.tolist()
        combinedSizes = df.groupby(
            ["location"]).size().reset_index().values.tolist()
        for c in combinedSizes:
            c.insert(1, "Combined")
        counts = counts + combined
        sizes = sizes + combinedSizes
        for item in counts:
            if item[1] == "Combined":
                result[-1] = item[2]
            else:
                result[item[1]] = item[2]
        for item in sizes:
            if item[1] == "Combined":
                result[-1] = result[-1] / item[2]
            else:
                result[item[1]] = result[item[1]] / item[2]
    return [round(r * 100, 2) for r in result]


def get_class_totals_as_list(df, numClasses):
    output = [0 for r in range(numClasses)]
    for index, item in df.iterrows():
        output[item["classorder"]] += item["value"]
    return output


def create_donut_chart(labels, donutText, data):
    # data = [int(Decimal(d).to_integral_value(rounding=ROUND_HALF_UP)) for d in data]
    graph = {"baseColors": classColors[:len(labels)],
             "baseLabels": labels, "labels": labels,
             "baseData": data,
             "donuttext": donutText,
             "datasets": [
                 {
                     "backgroundColor": classColors[:len(labels)],
                     "data": data
                 }
    ]}
    return graph


def create_line_chart(labels, xAxisLabels, data):

    # print("data is",data)
    # print("labels are",labels)
    datasets = []
    for index, item in enumerate(data):
        # print("adding data",item)
        datasets.append({"data": item,
                         "label": labels[index], "borderColor": classColors[index], "fill": False, "pointRadius": 0,
                         "borderWidth": 1, "backgroundColor": classColors[index]})
    graph = {
        "labels": xAxisLabels,
        "datasets": datasets
    }
    # print("datasets are now",datasets)
    return graph


def create_bar_chart(labels, xAxisLabels, data, stacked=True):
    datasets = []
    for index, item in enumerate(data):
        datasets.append({"label": labels[index], "data": item,
                         "backgroundColor": classColors[index]})
    graph = {labels: xAxisLabels, "datasets": datasets}
    return graph


def df_to_hourly_classed_totals(df, numClasses):
    output = [["-" for r in range(49)] for c in range(numClasses)]
    # df["value"] = df["value"].apply((lambda d: int(Decimal(d).to_integral_value(rounding=ROUND_HALF_UP))))
    resampled = df.groupby(["classorder", "seg"],
                           as_index=False).agg({"value": "sum"})
    if False:
        df.reset_index(inplace=True)
        df.set_index("time", inplace=True)
        resampled = df.groupby(["classorder"]).resample("1H", base=0)
        resampled = resampled.agg({"value": "sum"})
        resampled["time"] = resampled["time"].apply(
            lambda x: int(x.total_seconds() // 3600))
    for item in resampled.values.tolist():
        output[item[0]][item[1]] = item[2]
    return output


def wkt_to_geojson(text):
    if text is None:
        return None
    if "LINESTRING" in text:
        item = geojson.LineString
        coords = text.replace("LINESTRING(", "").replace(")", "")
    if "POINT" in text:
        item = geojson.Point
        coords = text.replace("POINT(", "").replace(")", "")
    if "POLYGON" in text:
        result = []
        item = geojson.Polygon
        print("text is", text)
        coords = text.replace("POLYGON(", "").replace(")", "").replace("(", "")
    # print("text is",text)
    coords = coords.split(",")
    # coords = text.replace("LINESTRING(", "").replace(")", "").split(",")

    coords = [c.split(" ") for c in coords]
    coords = [float(item) for c in coords for item in c]
    coords = [coords[i:i + 2] for i in range(0, len(coords), 2)]
    coords = [[c[0], c[1]] for c in coords]
    # print("coords are",coords)
    # print("text is",text)
    if "POLYGON" in text:
        return item([coords])
    return item(coords)


def geojson_to_wkt(g):
    coords = g["coordinates"]
    if g["type"] == "Polygon":
        result = []
        for zone in coords:
            coords = [" ".join([str(item) for item in c]) for c in zone]
            print(coords)
            coords = ",".join(coords)
            result.append("(" + coords + ")")
        coords = ",".join(result)
        print(coords)
    else:

        coords = [" ".join([str(item) for item in c]) for c in coords]
        print(coords)
        coords = ",".join(coords)
        print(coords)
    return g["type"].upper() + "(" + coords + ")"


##################################################################
#
#
# THROUGH models
#
#
######################################################################

class GroupObservationClass(models.Model):
    group = models.ForeignKey("ObservationClassGroup",
                              on_delete=models.CASCADE)
    obsClass = models.ForeignKey("ObservationClass", on_delete=models.CASCADE)
    order = models.IntegerField("Order")


class LocationObservationClassQuerySet(models.QuerySet):
    def as_dashboard_class_list(self):
        print(self)
        html = "<ul>"
        if (self[0].location.observationType.id == 1 or self[0].location.observationType.id == 9 or self[
                0].location.observationType.id == 10 or self[0].location.observationType.id == 12):
            html += "<li class='menu-item'><a href='#' class='selectable-menu-item  selected  select-all'>"
            html += "<i class='fa fa-square' style='color:black'></i><span>All</span></a></li>"
        for i, d in enumerate(self):
            if str(d.obsClass.displayName) in ['NO2', 'PM2.5'] or self[0].location.observationType.id == 1 or self[
                    0].location.observationType.id == 9 or self[0].location.observationType.id == 10 or self[0].location.observationType.id == 12:
                html += "<li class='menu-item' id='" + \
                    str(d.obsClass.id) + "'>"
                if (self[0].location.observationType.id == 1 or self[0].location.observationType.id == 9 or self[
                        0].location.observationType.id == 10 or self[0].location.observationType.id == 12):
                    if str(d.obsClass.displayName) == "NO2":
                        html += "<a href='#' class='selectable-menu-item selected measurement' onclick='change_title(this)' id ='NO2_link' data-vehicle='" + \
                            d.obsClass.name + "'>"
                    else:
                        html += "<a href='#' class='selectable-menu-item selected' data-vehicle='" + \
                            d.obsClass.name + "'>"
                else:
                    if str(d.obsClass.displayName) == "NO2":
                        html += "<a href='#' class='selectable-menu-item selected measurement' onclick='change_title(this)' id ='NO2_link' data-vehicle='" + \
                            d.obsClass.name + "'>"
                    else:
                        html += "<a href='#' class='selectable-menu-item measurement' onclick=" + \
                            'change_title(this)' + " data-vehicle='" + \
                            d.obsClass.name + "'>"

                html += "<i class='fa fa-square' style='color:" + classColors[i] + "'></i><span>" + str(
                    d.obsClass.displayName) + "</span></a></li>"

        html += "</ul>"
        return html

    def as_dashboard_graph_selectors(self):
        html = ""
        for index, d in enumerate(self):
            html += "<label class='class-selector' data-bg = '" + \
                classColors[index] + "' "
            html += "data-index='" + str(index) + "' style='border-color:" + classColors[index] + "'>" + str(
                d.obsClass.displayName) + "</label>"
        return html


class LocationObservationClassManager(models.Manager):
    def get_queryset(self):
        return LocationObservationClassQuerySet(self.model, using=self._db)


class LocationObservationClass(models.Model):
    location = models.ForeignKey("Location", on_delete=models.CASCADE)
    obsClass = models.ForeignKey("ObservationClass", on_delete=models.CASCADE)
    order = models.IntegerField("Order")
    objects = LocationObservationClassManager()

    class Meta:
        db_table = "locationobservationclass"


class LocationDirection(models.Model):
    location = models.ForeignKey("Location", on_delete=models.CASCADE)
    direction = models.ForeignKey("Direction", on_delete=models.CASCADE)
    order = models.IntegerField("Order")
    line = models.BinaryField("Line string", blank=True, null=True)

    class Meta:
        db_table = "locationdirection"

    def as_geojson_feature(self):
        if type(self.line) != bytes:
            line = None
        else:
            line = base64.decodebytes(self.line).decode()
        if line is None or line == "":
            line = geojson.LineString()
        else:
            line = wkt_to_geojson(line)
        return geojson.Feature(geometry=line, properties={"order": self.order, "name": self.direction.descriptive,
                                                          "type": "direction"})

    def save(self, *args, **kwargs):
        print("saving", type(self.line))
        if type(self.line) == geojson.geometry.LineString:
            print("saving", self.line)
            self.line = base64.encodebytes(geojson_to_wkt(self.line).encode())
        else:
            self.line = None
        super(LocationDirection, self).save(*args, **kwargs)


class APIDirection(models.Model):
    api = models.ForeignKey("vivacityAPI", on_delete=models.CASCADE)
    direction = models.ForeignKey("Direction", on_delete=models.CASCADE)
    order = models.IntegerField("Order")

    class Meta:
        db_table = "APIDirection"


class DirectionQuerySet(models.QuerySet):

    def as_html(self):
        print(self, type(self))
        html = "<select class='form-control' id='direction'>"
        for d in self:
            html += "<option value='" + str(d.id) + "'>" + str(d) + "</option>"
        html += "</select>"
        return html

    def as_dropdown_list(self):
        html = "<ul>"

        for dir in self:
            html += "<li class ='menu-item' id='direction_" + \
                str(dir.id) + "'>"
            html += "<a href='#' class ='selectable-menu-item' > <span> " + \
                dir.descriptive + "</span></a></li>"

        # html += "<li class ='menu-item' id='direction_combined" + "'>"
        # html += "<a href='#' class ='selectable-menu-item selected' > <span> Combined </span></a></li>"
        html += "</ul>"
        return html


class DirectionManager(models.Manager):
    def get_queryset(self):
        return DirectionQuerySet(self.model, using=self._db)


class Direction(models.Model):
    name = models.CharField("class", max_length=20)
    descriptive = models.CharField("descriptive name", max_length=50)
    abbrev = models.CharField(
        "abbreviated name , eg NE for north east", max_length=10)
    objects = DirectionManager()

    class Meta:
        db_table = "direction"

    def __str__(self):
        return str(self.name)


class DirectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Direction
        fields = ["name", "abbrev", "descriptive"]


##################################################################
#
#
# normal models
#
#
######################################################################

class ObservationType(models.Model):
    name = models.CharField(max_length=100)
    iconURL = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "observationtype"

    def __str__(self):
        return str(self.name)

    def __unicode__(self):
        return str(self.name)


class ObservationTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ObservationType
        fields = '__all__'


class Area(models.Model):
    name = models.CharField(max_length=100, blank=False, null=False)
    region = models.CharField(max_length=100)

    class Meta:
        db_table = "area"

class UploadedFile(models.Model):
    file_name = models.CharField(max_length=255)
    file_content = models.BinaryField()
    
class JSONFile(models.Model):
    file_name = models.CharField(max_length=255)
    file_content = models.JSONField()

class UploadLogging(models.Model):
    file_name = models.CharField(max_length=255)
    uploaded_date = models.DateTimeField(auto_now_add=True)
    converstion_to_CSV_start = models.DateTimeField(null=True)
    converstion_to_CSV_end = models.DateTimeField(null=True)
    observation_upload_start = models.DateTimeField(null=True)
    observation_upload_end = models.DateTimeField(null=True)
    existing_data_delete_start = models.DateTimeField(null=True)
    existing_data_delete_end = models.DateTimeField(null=True)
    aggregation_start = models.DateTimeField(null=True)
    aggregation_end = models.DateTimeField(null=True)
    process_end = models.DateTimeField(null=True)
    error_txt = models.TextField(null=True)

    class Meta:
        db_table = "upload_logging"

##################################################################
#
#
# ObservationClass
#
#
######################################################################


class ObservationClassQuerySet(models.QuerySet):

    def as_list_of_selected_classes(self):
        print(self, type(self))
        allClasses = ObservationClass.objects.using(
            DB_NAME).all().order_by("displayName")
        selected = self
        html = "<ul>"
        for d in allClasses:
            html += "<li class='menu-item' id='" + str(d.id) + "'>"
            html += "<a href='#' class='selectable-menu-item "
            if d in selected:
                html += " selected"
            html += "'><span>" + str(d.displayName) + "</span></a></li>"
        html += "</ul>"
        # print("html is",html)
        return html

    def as_dashboard_class_list(self):
        html = "<ul>"
        html += "<li class='menu-item'><a href='#' class='selectable-menu-item selected  select-all'>"
        html += "<i class='fa fa-square' style='color:black'></i><span>All</span></a></li>"
        for i, d in enumerate(self):
            html += "<li class='menu-item' id='" + str(d.id) + "'>"
            html += "<a href='#' class='selectable-menu-item selected' data-vehicle='" + d.name + "'>"
            html += "<i class='fa fa-square' style='color:" + classColors[i] + "'></i><span>" + str(
                d.displayName) + "</span></a></li>"
        html += "</ul>"
        return html

    def as_dashboard_graph_selectors(self):
        html = ""
        for index, d in enumerate(self):
            html += "<label class='class-selector' data-bg = '" + \
                classColors[index] + "' "
            html += "data-index='" + str(index) + "' style='border-color:" + classColors[index] + "'>" + str(
                d.displayName) + "</label>"
        return html


class ObservationClassManager(models.Manager):
    def get_queryset(self):
        return ObservationClassQuerySet(self.model, using=self._db)


class ObservationClass(models.Model):
    name = models.CharField("class", max_length=50)
    units = models.CharField("class", max_length=20, blank=True, null=True)
    displayName = models.CharField(
        "Display name", max_length=50, blank=True, null=True)
    description = models.CharField(
        "Extended Description", max_length=255, blank=True, null=True)
    objects = ObservationClassManager()

    class Meta:
        db_table = "observationclass"

    def __str__(self):
        return str(self.name)

    def __unicode__(self):
        return str(self.name)

    @classmethod
    def get_speed_classes_as_list(self):
        cols = ["0-10"] + [str(i) + "-" + str((i + 5))
                           for i in range(10, 100, 5)] + ["100+"]
        classes = [ObservationClass.objects.using(
            DB_NAME).get(displayName=c) for c in cols]
        for index, c in enumerate(classes):
            c.order = index
        return classes

    @classmethod
    def get_blank_speeds_template(self, numdirections=2):
        classes = self.get_speed_classes_as_list()
        data = []
        dfs = []
        for d in range(numdirections):
            data += [[cl.id, d] for cl in classes]
        template = pd.DataFrame(data, columns=["classorder", "directionorder"])
        for d in range(7):
            for h in range(24):
                t = template.copy()
                t["time"] = datetime.datetime(2019, 1, 1, h, 0, 0).time()
                t["day"] = d
                t["value"] = 0
                dfs.append(t)
        return pd.concat(dfs)


class ObservationClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = ObservationClass
        fields = '__all__'


class ObservationClassGroupQuerySet(models.QuerySet):

    def as_html_list(self):
        print(self, type(self))
        html = "<ul>"
        for d in self:
            html += "<li class='menu-item' id='group-" + \
                str(d.id) + "' onclick='applyGroup(this);'>"
            html += "<a href='#' class='menu-item "
            html += "'><span>" + str(d.displayName) + "</span></a></li>"
        html += "</ul>"
        # print("html is",html)
        return html

    def as_dashboard_class_list(self):
        html = "<ul>"
        for d in self:
            html += "<li class='menu-item' id='" + str(d.id) + "'>"
            html += "<a href='#' class='selectable-menu-item "
            html += "'><span>" + str(d.displayName) + "</span></a></li>"
        html += "</ul>"
        return html


class ObservationClassGroupManager(models.Manager):
    def get_queryset(self):
        return ObservationClassGroupQuerySet(self.model, using=self._db)


class ObservationClassGroup(models.Model):
    name = models.CharField("Group Name", max_length=20)
    classes = models.ManyToManyField(
        ObservationClass, through="GroupObservationClass")
    displayName = models.CharField(
        "Display name", max_length=20, blank=True, null=True)
    description = models.CharField(
        "Extended Description", max_length=255, blank=True, null=True)
    objects = ObservationClassGroupManager()

    def ordered_class_list(self):
        return [ld.obsClass for ld in GroupObservationClass.objects.using(DB_NAME).filter(group=self).order_by("order")]


class ObservationClassGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = ObservationClassGroup
        fields = '__all__'


##################################################################
#
#
# VivacityAPI
#
#
######################################################################


class VivacityAPIQuerySet(models.QuerySet):
    def as_html_list(self):
        html = "<div class='conduit-selectable-menu  min-1'><ul>"
        for api in self:
            html += "<li id='" + str(api.id) + \
                "' class='menu-item popup-item '" > ""
            html += "<a href='#'><i></i><span>" + \
                str(api.name) + "</span></a></li>"
        return html


class VivacityAPIManager(models.Manager):
    def get_queryset(self):
        return VivacityAPIQuerySet(self.model, using=self._db)


class VivacityAPI(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    APIKey = models.CharField(max_length=255, blank=True, null=True)
    baseUrl = models.CharField(max_length=255, blank=True, null=True)
    record = models.BooleanField(default=False)
    locations = models.ManyToManyField("Location")
    classes = models.ManyToManyField("ObservationClass")
    directions = models.ManyToManyField("Direction", through="APIDirection")
    type = models.CharField(max_length=50, blank=True, null=True)
    username = models.CharField(max_length=255, blank=True, null=True)
    password = models.CharField(max_length=255, blank=True, null=True)
    period = models.CharField(max_length=255, blank=True, null=True)
    objects = VivacityAPIManager()

    class Meta:
        db_table = "vivacityapi"

    def directions_list(self):
        return self.directions.order_by("order")

    def class_list(self):
        return self.classes.all()

    def classes_as_html_menu_list(self):
        classes = self.classes.all()
        allClasses = ObservationClass.objects.using(DB_NAME).all()
        html = "<ul>"
        for cl in allClasses:
            html += "<li class='menu-item'>"
            html += "<a href='#'  id='" + cl.name + "'"
            if cl in classes:
                html += " class='selected'"
            html += "><span>" + cl.name.title() + "</span></a></li>"
        return html

    def get_data_from_api_and_save(self, startDate, endDate, selectedSites="ALL", save=True, update=False):
        timezone.activate("UTC")
        startDate = timezone.make_aware(startDate)
        endDate = timezone.make_aware(endDate)
        print("in get data from api, start date is", startDate, save)
        output = []
        if self.type == "old":
            result = tracsis_api_helpers.get_historic_vivacity_data(self.baseUrl + "/historic?", self.APIKey, startDate,
                                                                    endDate)
            output = self.process_data(result, selectedSites)
            # return
        elif self.type == "new":
            token = tracsis_api_helpers.get_vivacity_auth_token(
                self.username, self.password)
            if selectedSites == "ALL":
                # locs = [loc.api_identifier for loc in self.locations.all()]
                locs = []
            else:
                locs = [loc.api_identifier for loc in selectedSites]
            result = tracsis_api_helpers.get_vivacity_data(
                token, startDate, endDate, locs)
            output = self.process_new_style_vivacity_data(
                result, update=update)
            # return output
            # print("output is",output)
        elif self.type == "vdanet":
            output = []
            token = tracsis_api_helpers.get_TFWM_token(
                *tracsis_api_helpers.TFWMAPI)
            for site in self.locations.all():
                if selectedSites == "ALL" or site.id in selectedSites:
                    result = tracsis_api_helpers.get_TFWM_data(
                        token, site.id, startDate, endDate)
                    output += self.process_vdanet_style_data(result, site)
        elif self.type == "q-free":
            output = []
            token = tracsis_api_helpers.get_QFREE_token(
                self.APIKey, self.password)
            print("token is", token)
            if selectedSites == "ALL":
                selectedSites = self.locations.all()
            for site in self.locations.all():
                info = tracsis_api_helpers.get_QFREE_sites(
                    token, id=site.id.replace("qfree_", ""))
                if info["status"] == "Offline":
                    site.status = "offline"
                else:
                    site.status = "good"
                site.save()
                print("here1111", site.id, selectedSites)
                if selectedSites == "ALL" or site in selectedSites:
                    print("here")
                    for d in site.directions.all():
                        direction = d.direction.descriptive.title().replace("bound", "Bound")
                        for c in site.classes.all():
                            classification = c.obsClass.name.title()
                            #
                            # because the API returns results aggregated across days, classes and directions,
                            # we have to query for each direction and class
                            # we also have to submit the same startDate and endDate in order to get one days worth of
                            # data
                            #
                            result = tracsis_api_helpers.get_QFREE_data(token, site.id.replace("qfree_", ""),
                                                                        classification, direction, startDate, startDate)
                            print("result is", result)
                            for key, item in result["aggregations"]["totalsPerHour"].items():
                                obs = Observation(direction=d, obsClass=c, date=startDate.replace(hour=int(key)),
                                                  value=int(item), location=site)
                                # print(d, c, startDate.replace(hour=int(key)), item, site)
                                output.append(obs)
        try:
            print("adding ", len(output), "data points")
            if save:
                if update:
                    pass
                #     for item in output:
                #         obs  = Observation.objects.using(DB_NAME).update_or_create(location=item.location,date=item.date,direction=item.direction,obsClass=item.obsClass,defaults={'value':item.value})
                # Observation.create_update_objects.using(DB_NAME).bulk_update_or_create(output,['value'],match_field=['date','direction','obsClass','location','status','removed'],batch_size=1000)
                else:
                    Observation.objects.using(DB_NAME).bulk_create(
                        output, batch_size=1000, ignore_conflicts=False)
                print("successfully saved counts")
        except django.db.IntegrityError as e:
            print("counts were already in the database")
        except Exception as e:
            print(e)
            print("something went wrong when adding counts for api ", self.name)
            raise django.db.Error(
                "Failed to write data to database for api " + self.name + " " + str(e))
        return output

    def backfill(self, startDate, endDate, selectedSites="ALL"):
        #
        # fill the database from the relevant API
        #
        print("selected sites is", selectedSites)
        print("getting data for", startDate, endDate)
        if selectedSites == "ALL":
            # selectedSites = self.locations.all()
            selectedSites = 'ALL'
        elif type(selectedSites) == list:
            selectedSites = Location.objects.using(
                DB_NAME).filter(id__in=selectedSites)
        origStartDate = startDate.replace(
            hour=0, minute=0, second=0, microsecond=0)
        while startDate < endDate:
            if self.period == "hour":
                try:
                    self.get_data_from_api_and_save(startDate, startDate + datetime.timedelta(hours=1),
                                                    selectedSites=selectedSites)
                except Exception as e:
                    print('error was -', e)
                startDate += datetime.timedelta(hours=1)
            if self.period == "day":
                self.get_data_from_api_and_save(startDate, startDate + datetime.timedelta(days=1),
                                                selectedSites=selectedSites)
                startDate += datetime.timedelta(days=1)
            time.sleep(0.001)
        #
        # fill the daily classed totals table as the classed totals may have changed
        #
        print("in backfill, filling daily classed totals from ",
              origStartDate, endDate)

        while origStartDate < endDate:
            selectedSites = self.locations.all() if selectedSites == "ALL" else selectedSites
            selectedSites.fill_daily_classed_totals(origStartDate)
            origStartDate += datetime.timedelta(days=1)
        return startDate

    # def get_sites(self):
    #     if self.type == "old":
    #         result = tracsis_api_helpers.get_historic_vivacity_data(self.baseUrl + "/historic?", self.APIKey, startDate, endDate)
    #         output = self.process_data(result)
    #         # return
    #     elif self.type == "new":
    #         token = tracsis_api_helpers.get_vivacity_auth_token(self.username, self.password)
    #         if selectedSites == "ALL":
    #             locs = [loc.id for loc in self.locations.all()]
    #         else:
    #             locs = [loc.id for loc in selectedSites]
    #         result = tracsis_api_helpers.get_vivacity_data(token, startDate, endDate, locs)
    #         output = self.process_new_style_vivacity_data(result)
    #         # return output
    #         # print("output is",output)
    #     elif self.type == "vdanet":
    #         output = []
    #         token = tracsis_api_helpers.get_TFWM_token(*tracsis_api_helpers.TFWMAPI)

    def process_data(self, result, locations):
        ###
        # result is a list of dicts, each dict is a 5 minute time period, keys are times, values are lists of countlines and counts.
        ###
        output = []
        for timeData in result:
            for key, data in timeData.items():
                t = datetime.datetime.utcfromtimestamp(int(key))
                t = pytz.utc.localize(t)

                for loc in locations:
                    directions = loc.directions.all()
                    # print("directions are",directions)
                    classes = {c.obsClass.name: c for c in loc.classes.all()}
                    for vehName, obsClass in classes.items():
                        countIn = 0
                        countOut = 0
                        for item in data:
                            for cl in item["countlines"]:
                                if cl["countlineId"] == loc.id:
                                    for count in cl["counts"]:
                                        if count["class"] == vehName:
                                            countIn = count["countIn"]
                                            countOut = count["countOut"]
                        output.append(Observation(location=loc, date=t, direction=directions[1], value=countIn,
                                                  obsClass=obsClass))
                        output.append(Observation(location=loc, date=t, direction=directions[0], value=countOut,
                                                  obsClass=obsClass))
        return output

    def process_new_style_vivacity_data(self, result, update=False):
        ###
        # result is a list of dicts, each dict is a 5 minute time period, keys are times, values are lists of countlines and counts.
        ###
        output = []
        dataDict = {}
        countlines = self.locations.all()
        countlines = {cl.api_identifier: cl for cl in countlines}
        timezone = pytz.timezone("Europe/London")
        today_date = datetime.datetime.now()
        today_date = pytz.timezone("Europe/London").localize(
            today_date.replace(minute=today_date.minute - (today_date.minute % 15), second=0, microsecond=0))

        for countlineId, returnedCounts in result.items():
            # print("looking for", countlineId,countlines, type(countlineId))
            if countlineId in countlines:
                countline = countlines[countlineId]
                print("found countline", countline)
                directions = countline.directions.all()
                classes = {
                    cl.obsClass.name: cl for cl in countline.classes.all()}
                for t, countlineData in returnedCounts.items():
                    t = datetime.datetime.strptime(t[:19], "%Y-%m-%dT%H:%M:%S")
                    t = pytz.utc.localize(t)
                    dateTo = datetime.datetime.strptime(
                        countlineData["to"][:19], "%Y-%m-%dT%H:%M:%S")
                    if dateTo.minute % 5 != 0 or dateTo.second != 0 or t.minute % 5 != 0 or t.second != 0:
                        # print("found partial date segment", dateTo, "skipping import of this data")
                        continue
                    # print("processing date", t)
                    countline.lastDataReceived = today_date
                    countline.save()
                    for count in countlineData["counts"]:
                        # print("--------------- processing",countline, count)
                        if count["class"] not in classes:
                            # print("--------------- no class")
                            continue
                            # print("Creating new vehicle class: " + str(count["class"]))
                            vehicle = ObservationClass.objects.using(DB_NAME).create(name=count["class"],
                                                                                     displayName=count["class"].title())
                            classes[vehicle.name] = vehicle
                        else:
                            vehicle = classes[count["class"]]
                        try:
                            if update:

                                if count["countIn"] > 0:
                                    output.append(1)
                                    print("updating -", t)
                                    Observation.objects.using(DB_NAME).update_or_create(location=countline, date=t,
                                                                                        direction=directions[1],
                                                                                        obsClass=vehicle, defaults={
                                                                                            'value': count["countIn"]})
                                if count["countOut"] > 0:
                                    output.append(1)
                                    print("updating -", t)
                                    Observation.objects.using(DB_NAME).update_or_create(location=countline, date=t,
                                                                                        direction=directions[0],
                                                                                        obsClass=vehicle, defaults={
                                                                                            'value': count["countOut"]})
                            else:
                                if count["countIn"] > 0:
                                    i = Observation(location=countline, date=t, direction=directions[1],
                                                    value=count["countIn"], obsClass=vehicle, status=False,
                                                    removed=False, weekday=None, hr=None,
                                                    segment=None)  # [t][countline]["counts"][vehicle]["countIn"] = count["countIn"]
                                    output.append(i)
                                if count["countOut"] > 0:
                                    o = Observation(location=countline, date=t, direction=directions[0],
                                                    value=count["countOut"], obsClass=vehicle, status=False,
                                                    removed=False, weekday=None, hr=None, segment=None)
                                    output.append(o)
                            # updated = True
                        except Exception as e:
                            print("error adding data to output structure", e)
            else:
                pass
                # print(countlineId, "wasnt in the countlines list")
        return output

    def process_vdanet_style_data(self, result, site):
        ###
        ###
        ###
        output = []
        if result["properties"]["ReportError"]["HasError"]:
            print(site, "has error in output",
                  result["properties"]["ReportError"])
            return []
        directions = site.directions.all()
        classes = {cl.obsClass.name: cl for cl in site.classes.all()}
        # print("classes are",classes)
        with transaction.atomic():
            for item in result["properties"]["Channels"]:
                # print("looking at item",item)
                # print(item["ChannelName"])
                direction = None
                obsClass = site.classes.all()[1]
                for d in directions:
                    if d.direction.descriptive == item["ChannelName"]:
                        direction = d
                # print("direction is",direction,"vehicle class is",obsClass)
                for flow in item["Flows"]:
                    # print(flow)
                    d = flow["DateOfData"]
                    d = datetime.datetime.strptime(d, "%Y-%m-%dT%H:%M:%S")
                    values = flow["Values"]
                    # print("values are",values)
                    for t, v in values.items():
                        t = pytz.utc.localize(
                            d + datetime.timedelta(minutes=int(t)))
                        obs = Observation(
                            location=site, direction=direction, obsClass=obsClass, value=int(v), date=t)

                        output.append(obs)
        # print("returning",len(output))
        return output

    def add_data_to_database(self, data):
        processed = []
        for date, dataDict in data.items():
            for location, counts in dataDict.items():
                for veh, count in counts.items():
                    for direction, value in count.items():
                        dict = {"obsClass": veh, "direction": direction, "value": value,
                                "date": date, "location": location}
                        processed.append(Observation(**dict))
        Observation.objects.using(DB_NAME).bulk_create(
            processed, ignore_conflicts=True)

    @classmethod
    def create(self, **obj_data):
        print(obj_data)
        if "name" not in obj_data:
            raise django.core.exceptions.ValidationError(
                {"name": "missing unique name field"})
        if obj_data["name"] is None or obj_data["name"] == "":
            raise django.core.exceptions.ValidationError(
                {"name": "unique name cannot be blank"})
        try:
            VivacityAPI.objects.using(DB_NAME).get(name=obj_data["name"])
        except VivacityAPI.DoesNotExist as e:
            return VivacityAPI(name=obj_data["name"])
        raise django.db.IntegrityError

    def update(self, data):
        fields = [f.name for f in VivacityAPI._meta.get_fields()]
        for f in fields:
            if f in data:
                val = data[f]
                if val == "":
                    val = None
                setattr(self, f, val)
        self.full_clean()
        self.save()


##################################################################
#
#
# Location
#
#
######################################################################

class LocationQuerySet(models.QuerySet):

    def get_admin_stats(self):
        d = datetime.datetime.now().date()
        monday = d - datetime.timedelta(days=d.weekday())
        # print("correct start of calc period is", monday - datetime.timedelta(days=56))
        # .locations.filter(temp=0, observationType_id=1, virtual=0, vivacityapi__in=[1,2])
        locs = self
        obs = DailyClassedTotals.objects.using(DB_NAME).filter(date__gte=monday - datetime.timedelta(days=56),
                                                               date__lt=monday,
                                                               location_id=OuterRef("id"))
        #
        # get the average of the last 8 days that are the same day as yesterday, eg last 8 mondays
        #   so we subtract 1 day from todays isoweekday
        #
        q1 = obs.filter(date__iso_week_day=d.isoweekday() - 1).values("location_id").annotate(
            total=Coalesce(Sum("value") / 8, Value(0)))
        #
        # get the average week over the last 8 weeks
        #
        q2 = obs.values("location_id").annotate(weekly_avg=Sum("value") / 8)
        #
        # get the total counts from today so far
        #
        today = DailyClassedTotals.objects.using(DB_NAME).filter(
            date__contains=d, location_id=OuterRef("id"))
        today = today.values("location_id").annotate(today=Sum("value"))
        #
        # get the total counts from yesterday
        #
        yesterday = DailyClassedTotals.objects.using(DB_NAME).filter(date__contains=d - datetime.timedelta(days=1),
                                                                     location_id=OuterRef("id"))
        yesterday = yesterday.values(
            "location_id").annotate(yesterday=Sum("value"))
        #
        # get the total counts from last week
        #
        lastWeek = DailyClassedTotals.objects.using(DB_NAME).filter(date__gte=monday - datetime.timedelta(days=7),
                                                                    date__lt=monday, location_id=OuterRef("id"))
        lastWeek = lastWeek.values(
            "location_id").annotate(last_week=Sum("value"))

        locs = locs.annotate(weekday_avg=Subquery(q1.values("total")), weekly_avg=Subquery(q2.values("weekly_avg")),
                             weekly_total=Subquery(
                                 lastWeek.values("last_week")),
                             today_total=Subquery(today.values("today")),
                             yesterday_total=Subquery(
                                 yesterday.values("yesterday")),
                             )
        # project_name=Value(self.client.name, models.CharField()))

        locs = locs.values("client__name", "id", "area__name", "lastDataReceived", "lastNonZeroDataReceived",
                           "weekly_total", "name",
                           "yesterday_total", "weekday_avg", "weekly_avg", "today_total", "api_identifier",
                           "sensorcheck", "vivacity_sensor_id", "sensorcheck")

        return locs

    def count_num_days(self):
        for loc in self:
            qs = loc.observation_set.annotate(date_only=TruncDate(
                'date')).values("location_id", "date_only")
            qs = qs.distinct().aggregate(numDays=Count("date_only"))
            loc.numDays = qs["numDays"]
            loc.save()

    def update_weather(self, d):
        for loc in self:
            loc.update_weather(d)
            time.sleep(5)

    def get_weather_data(self, **params):
        sub = Subquery(WeatherCode.objects.using(DB_NAME).filter(
            id=OuterRef("value")).values("icon")[:1])
        sub2 = Subquery(WeatherCode.objects.using(DB_NAME).filter(
            id=OuterRef("value")).values("description")[:1])
        numCells = int(60 / int(params["period"]) * 24)
        data = [[0] * numCells for i in range(7)]
        print("data is", data)
        qs = AssociatedObservation.objects.using(DB_NAME).filter(location_id=params["id"],
                                                                 date__gte=params["startDate"],
                                                                 date__lte=params["endDate"], obsClass_id=43085)
        qs = qs.annotate(icon=sub, description=sub2).values(
            "date", "icon", "description")
        print(qs)
        numPeriods = int(60 / int(params["period"]))
        for item in qs:
            d = item["date"]
            print("day is", d, d.weekday(), d.hour)
            chunk = d.hour * numPeriods
            for i in range(numPeriods):
                data[d.weekday()][chunk + i] = [item["icon"],
                                                item["description"]]

        print(data)
        return data

    def download_weather(self, **params):
        case = Case(When(obsClass__units__isnull=True, then=F("obsClass__displayName")),
                    default=Concat(F("obsClass__displayName"), Value(" ("), F("obsClass__units"), Value(")")))

        dataframes = []
        weathercodes = {
            w.id: w for w in WeatherCode.objects.using(DB_NAME).all()}
        for loc in self:
            print("processing", loc.name)
            data = AssociatedObservation.objects.using(DB_NAME).filter(date__gte=params["startDate"],
                                                                       date__lt=params["endDate"], location=loc)
            data = data.annotate(header=case)
            df = pd.DataFrame(data.values(
                "location__area__name", "location__name", "date", "header", "value"))
            print("appending", df)
            dataframes.append(df)
        df = pd.concat(dataframes)
        if len(df) > 0:
            df = pd.pivot_table(df, values="value", columns="header",
                                index=["location__area__name", "location__name", "date"]).reset_index()
            for key, val in weathercodes.items():
                df.loc[df["Weather"] == key, "Weather"] = val.description
        print("columns are", df.columns)
        df.columns = ["Area", "Site", "Date"] + list(df.columns[3:])
        df["Time"] = df["Date"].dt.time
        df["Date"] = df["Date"].dt.date
        return df[
            ["Area", "Site", "Date", "Time"] + [c for c in df.columns if c not in ["Area", "Site", "Date", "Time"]]]

    def fill_daily_totals(self, d):
        # fill daily totals table with sum of all values for location on day indicated by d
        #
        timezone.activate("UTC")
        print("filling date", d, d + datetime.timedelta(days=1))
        # startDate = timezone.make_aware(d)
        # endDate = timezone.make_aware((d + datetime.timedelta(days=31)).replace(day=1))
        # print(startDate,endDate)
        output = Observation.objects.using(DB_NAME).filter(location__in=list(self), date__gte=d,
                                                           date__lt=d + datetime.timedelta(days=1))
        print("output is", output)
        output = output.values("location_id").annotate(total=Sum("value"))
        # print("value is",output.query)
        # dataToSave = []
        for item in output.values_list("location_id", "total"):
            print("processing", item)
            obj, _ = DailyTotals.objects.using(DB_NAME).get_or_create(
                location_id=item[0], date=d, value=item[1])
            obj.value = item[1]
            obj.save()
        pass

    def fill_daily_classed_totals(self, d):
        # fill daily totals table with sum of all values for location on day indicated by d
        #
        timezone.activate("Europe/London")
        d = timezone.make_aware(d)
        print("filling date", d, d + datetime.timedelta(days=1))

        #
        # get the data , date is in GMT, will be converted to UTC when extracting from db
        #
        output = Observation.objects.using(DB_NAME).filter(location__in=list(self), date__gte=d,
                                                           date__lt=d + datetime.timedelta(days=1))
        print("would save to", d.date())
        # print(output.query)
        output = output.values(
            "location_id", "obsClass").annotate(total=Sum("value"))
        # print("value is",output.query)
        dataToSave = []
        for item in output.values_list("location_id", "obsClass__obsClass_id", "total"):
            # print(item)
            obj, _ = DailyClassedTotals.objects.using(DB_NAME).get_or_create(location_id=item[0], date=d.date(),
                                                                             obsClass_id=item[1])
            obj.value = item[2]
            dataToSave.append(obj)
            # obj.save()
        print("saving daily totals")
        DailyClassedTotals.objects.using(DB_NAME).bulk_update(
            dataToSave, ["value"], batch_size=1000)
        print("finished")

    def copy_factored_month(self, sourceMonth):
        #
        # source month is date of first day of month that you want to copy
        # it copies to the next month
        #
        timezone.activate("UTC")
        startOfNextMonth = timezone.make_aware(
            datetime.datetime(sourceMonth.year + (sourceMonth.month // 12), ((sourceMonth.month % 12) + 1), 1))
        startDate = startOfNextMonth
        endOfNextMonth = timezone.make_aware(datetime.datetime(startOfNextMonth.year + (startOfNextMonth.month // 12),
                                                               ((startOfNextMonth.month % 12) + 1), 1))
        print("copying data to", startOfNextMonth, endOfNextMonth)
        #
        # create blank data for the month we are going to copy into, in 15 minute chunks.
        #

        for loc in self:
            print("processing", loc.name)
            while startDate < endOfNextMonth:
                loc.create_blank_data(startDate)
                startDate += datetime.timedelta(minutes=15)
        #
        # get data for the source month
        #
        for loc in self:
            print("getting raw data for", loc.name, "for dates",
                  sourceMonth, sourceMonth + datetime.timedelta(days=7))
            df = loc.get_raw_data_as_df(
                sourceMonth, sourceMonth + datetime.timedelta(days=7))
            # print(df)
            df["newValue"] = df["value"]
            loc.fill_values_with_factored_data_from_df(
                startOfNextMonth, endOfNextMonth, df)

    def fill_num_days(self):
        print("starting fill num days)", datetime.datetime.now())
        qs = Observation.objects.using(DB_NAME).filter(location__in=self).annotate(d=TruncDate("date")).values(
            "location_id").annotate(c=Count("d", distinct=True))
        print("finished full count of days")
        for loc in self:
            for item in qs:
                if loc.id == item["location_id"]:
                    print("setting", loc.name, "to", item["c"])
                    loc.numDays = item["c"]
                    loc.save()
        print("finished fill of num days", datetime.datetime.now())

    def get_date_range(self):
        timezone.activate("Europe/London")
        locationString = "('" + "','".join([str(s.id) for s in self]) + "')"

        sqlString = f"select min(date),max(date) from {DB_NAME}_observation where location_id in " + locationString
        sqlString += " group by location_id"
        with connections[DB_NAME].cursor() as cursor:
            cursor.execute(sqlString)
            result = cursor.fetchall()
            # print("result is",result)
            if result == ():
                return "No data"
            minDate = min([d[0] for d in result])
            maxDate = max([d[1] for d in result])
        return timezone.make_aware(minDate).strftime("%a %d/%m/%Y") + " - " + timezone.make_aware(maxDate).strftime(
            "%a %d/%m/%Y")

    def get_5_min_averages(self, startDate=None, endDate=None, aggFunc="COUNT", timezone="Europe/London"):
        #
        # gets average mon, tue wed, etc, by average 5 minutes
        #
        # returns a dataframe
        #
        #

        locationString = "('" + ",'".join([str(s.id) for s in self]) + "')"
        sqlString = "select s.id,s.location_id,WEEKDAY(s.d) as wkday, s.t, s.directionorder,s.classorder,avg(s.value) as value from ("
        sqlString += "select obs.id,obs.location_id,DATE(CONVERT_TZ(date,'UTC','" + \
            timezone + "')) d,"
        sqlString += "TIME(FROM_UNIXTIME(FLOOR(UNIX_TIMESTAMP(CONVERT_TZ(date,'UTC','Europe/London'))/300)*300)) AS t, "
        sqlString += f" dir.order directionorder,loc.order classorder, " + str(
            aggFunc) + "(obs.value) as value from {DB_NAME}_observation obs "
        sqlString += "join schoolstreets_locationobservationclass loc on loc.location_id = obs.location_id and loc.obsclass_id = obs.obsclass_id "
        sqlString += f"join {DB_NAME}_locationdirection dir on dir.location_id = obs.location_id and dir.direction_id = obs.direction_id "
        sqlString += " where obs.status = 0 and removed = 0 and obs.location_id in " + locationString
        if startDate is not None:
            sqlString += " and date >= '" + startDate.strftime("%Y-%m-%d")
        if endDate is not None:
            sqlString += "' and date < '" + endDate.strftime("%Y-%m-%d") + "' "
        sqlString += " group by location_id, d, t, obs.obsclass_id,obs.direction_id) s group by s.location_id, wkday,s.t,s.directionorder,s.classorder"
        sqlString += " UNION "
        sqlString += "select s.id,s.location_id,WEEKDAY(s.d) as wkday, s.t, 2,s.classorder,avg(s.value) as value from ("
        sqlString += "select obs.id,obs.location_id,DATE(CONVERT_TZ(date,'UTC','" + \
            timezone + "')) d,"
        sqlString += "TIME(FROM_UNIXTIME(FLOOR(UNIX_TIMESTAMP(CONVERT_TZ(date,'UTC','Europe/London'))/900)*900)) AS t, "
        sqlString += f" loc.order classorder," + \
            str(aggFunc) + \
            "(obs.value) AS value from {DB_NAME}_observation obs "
        sqlString += f"join {DB_NAME}_locationobservationclass loc on loc.location_id = obs.location_id and loc.obsclass_id = obs.obsclass_id "
        sqlString += " where obs.status = 0 and removed = 0 and  obs.location_id in " + locationString
        if startDate is not None:
            sqlString += " and date >= '" + startDate.strftime("%Y-%m-%d")
        if endDate is not None:
            sqlString += "' and date < '" + endDate.strftime("%Y-%m-%d") + "' "
        sqlString += " group by location_id, d, t, obs.obsclass_id) s group by s.location_id, wkday,s.t,s.classorder"

        data = Observation.objects.using(DB_NAME).raw(sqlString)
        return data

    def output_data_to_excel(self, *args, tz="Europe/London", **kwargs):
        file = args[0]
        timezone.activate(tz)
        startDate = timezone.make_aware(
            datetime.datetime.strptime(kwargs["startDate"], "%Y-%m-%d"))
        endDate = timezone.make_aware(
            datetime.datetime.strptime(kwargs["endDate"], "%Y-%m-%d"))
        qs = self.prefetch_related(
            "locationdirection_set", "locationobservationclass_set")
        header = True
        for loc in qs.all():
            dirs = list(loc.locationdirection_set.all(
            ).values_list("direction__name", flat=True))
            classes = list(loc.locationobservationclass_set.all(
            ).values_list("obsClass__displayName", flat=True))
            dates = pd.date_range(startDate, endDate,
                                  freq="5min", ambiguous=True)
            index = pd.MultiIndex.from_product([dates, dirs, classes], names=[
                                               "Date", "Direction", "Class"])
            counts = Observation.objects.using(DB_NAME).filter(
                location=loc, date__gte=startDate, date__lte=endDate)
            data = list(
                counts.values_list("obsClass__obsClass__displayName", "direction__direction__name", "date", "value"))
            df = pd.DataFrame(
                data, columns=["Class", "Direction", "Date", "Value"])
            df.set_index(["Date", "Direction", "Class"], inplace=True)
            df = df.reindex(index, columns=["Value"], fill_value="-")
            df["Area"] = loc.area.name
            df["Site"] = loc.name
            df = df.tz_localize(None, level="Date")
            df.reset_index()[["Area", "Site", "Direction", "Class", "Date", "Value"]].to_csv(file, mode="a",
                                                                                             index=False, header=header)
            header = False
        # print(query_count_all())

    def as_crt_style_table(self):
        if len(self) == 0:
            return ["", ""]
        classes = self[0].classes.all()
        classString = ""
        headerString = "<tr><th scope='col' onclick='tableHeaderClicked(event);' class='large-header' data-width='100'>Area</th>" \
                       "<th scope='col' onclick='tableHeaderClicked(event);' class='bar-header' data-width='200'>Site</th>" \
                       "<th scope='col' onclick='tableHeaderClicked(event);' class='bar-header' data-width='200'>Direction</th>" \
                       "<th scope='col' onclick='tableHeaderClicked(event);' class='bar-header' data-width='200'>Chart</th>" \
                       "<th scope='col' onclick='tableHeaderClicked(event);' class='small-header' data-width='70'>Days</th>" \
                       "<th scope='col' onclick='tableHeaderClicked(event);' class='small-header' data-width='70'>Total</th>" \
                       "<th scope='col' onclick='tableHeaderClicked(event);' class='small-header d-none' data-width='70'>Total</th>" \
                       "<th scope='col' onclick='tableHeaderClicked(event);' class='small-header d-none' data-width='70'>Total</th>" \
                       "<th scope='col' onclick='tableHeaderClicked(event);' class='small-header d-none' data-width='70'>Total</th>"

        for cl in classes:
            classString += "<td class='variable-cell' data-width='90' data-vehicle='" + str(
                cl.obsClass.name) + "'></td>"
            headerString += "<th class='variable-cell' data-width='90' onclick='tableHeaderClicked(event);' data-vehicle='" + str(
                cl.obsClass.name) + "'>" + str(cl.obsClass.displayName) + "</th>"
        headerString += "<th class='padding-cell' style='width:0px'></th></tr>"
        tableString = ""

        for site in self:
            dirString = "<select class='form-control'>"
            directions = site.directions.all()
            for dir in directions:
                dirString += "<option>" + \
                    str(dir.direction.descriptive) + "</option>"
            dirString += "<option>Combined</option></select>"
            tableString += "<tr id='" + site.id + "_row'>"
            areaName = site.area.name if site.area is not None else "Unknown Area"
            siteType = "perm" if site.temp == 0 else "temp"
            tableString += "<td onclick='zoomToSite(\"" + areaName + "_" + site.name + \
                "\");' data-width='100' class='large-header " + \
                siteType + "'>" + areaName + "</td>"
            tableString += "<td class='bar-header' data-width='200'>" + site.name + "</td>"
            tableString += "<td class='bar-header' data-width='100'>" + dirString + "</td>"
            tableString += "<td class='bar-header' data-width='200'><div><canvas width='200' height='25'></canvas></div></td>"
            tableString += "<td class='small-header' data-width='70'>" + \
                str(site.numDays) + "</td>"
            tableString += "<td class='small-header' data-width='70'>" + \
                str(44) + "</td>"
            tableString += "<td class='small-header d-none' data-width='70'>" + \
                str(44) + "</td>"
            tableString += "<td class='small-header d-none' data-width='70'>" + \
                str(44) + "</td>"
            tableString += "<td class='small-header d-none' data-width='70'>" + \
                str(44) + "</td>"
            tableString += classString
            tableString += "<td class='padding-cell' style='width:0px'></td></tr>"
        return [tableString, headerString]

    def as_geojson(self):
        col = []
        # locs = self.prefetch_related("locationdirection_set", "area", "locationobservationclass_set",
        #                                   "locationdirection_set__direction",
        #                                   "locationobservationclass_set__obsClass", "observationType")
        for loc in self:
            # print(loc)

            if loc.virtual:
                assoc = loc.associatedLocations.all()
                for item in assoc:
                    feature = item.as_geojson_feature()
                    feature["properties"]["type"] = "associated"
                    col.append(feature)
            feature = loc.as_geojson_feature()
            col.append(feature)
            for direction in loc.directions.all():
                feature = direction.as_geojson_feature()

                feature["properties"]["id"] = str(
                    loc.id) + "_direction_" + str(direction.order)
                col.append(feature)
        return geojson.FeatureCollection(col)

    def get_daily_15_min_averages(self, startDate, endDate, aggFunc="COUNT", timezone="Europe/London"):
        #
        # gets average mon, tue wed, etc, by average 15 minutes
        #
        # returns a dataframe
        #
        #

        locationString = "('" + ",'".join([str(s.id) for s in self]) + "')"
        sqlString = "select s.location_id,WEEKDAY(s.d) as wkday, s.t, s.directionorder,s.classorder,avg(s.value) as value from ("
        sqlString += "select obs.location_id,DATE(CONVERT_TZ(date,'UTC','" + \
            timezone + "')) d,"
        sqlString += "TIME(FROM_UNIXTIME(FLOOR(UNIX_TIMESTAMP(CONVERT_TZ(date,'UTC','Europe/London'))/300)*300)) AS t, "
        sqlString += " dir.order directionorder,loc.order classorder, " + str(
            aggFunc) + f"(obs.value) as value from {DB_NAME}_observation obs "
        sqlString += f"join {DB_NAME}_locationobservationclass loc on loc.location_id = obs.location_id and loc.obsclass_id = obs.obsclass_id "
        sqlString += f"join {DB_NAME}_locationdirection dir on dir.location_id = obs.location_id and dir.direction_id = obs.direction_id "
        sqlString += " where obs.status = 0 and removed = 0 and obs.location_id in " + locationString
        sqlString += " and date >= '" + startDate.strftime("%Y-%m-%d") + "' and date < '" + endDate.strftime(
            "%Y-%m-%d") + "' "
        sqlString += " group by location_id, d, t, obs.obsclass_id,obs.direction_id) s group by s.location_id, wkday,s.t,s.directionorder,s.classorder"
        sqlString += " UNION "
        sqlString += "select s.location_id,WEEKDAY(s.d) as wkday, s.t, 2,s.classorder,avg(s.value) as value from ("
        sqlString += "select obs.location_id,DATE(CONVERT_TZ(date,'UTC','" + \
            timezone + "')) d,"
        sqlString += "TIME(FROM_UNIXTIME(FLOOR(UNIX_TIMESTAMP(CONVERT_TZ(date,'UTC','Europe/London'))/900)*900)) AS t, "
        sqlString += " loc.order classorder," + \
            str(aggFunc) + \
            f"(obs.value) AS value from {DB_NAME}_observation obs "
        sqlString += f"join {DB_NAME}_locationobservationclass loc on loc.location_id = obs.location_id and loc.obsclass_id = obs.obsclass_id "
        sqlString += " where obs.status = 0 and removed = 0 and  obs.location_id in " + locationString
        sqlString += " and date >= '" + startDate.strftime("%Y-%m-%d") + "' and date < '" + endDate.strftime(
            "%Y-%m-%d") + "' "
        sqlString += " group by location_id, d, t, obs.obsclass_id) s group by s.location_id, wkday,s.t,s.classorder"

        # sqlString += "avTable group by location_id, d,h,obsclass_id,direction_id order by d,h,directionorder,classorder"
        # print(sqlString)
        with connections[DB_NAME].cursor() as cursor:
            cursor.execute(sqlString)
            result = cursor.fetchall()
            result = [list(l) for l in result]
            # print(result[:10])
            df = pd.DataFrame(result, columns=[
                              "location", "day", "time", "directionorder", "classorder", "value"])
            df["value"] = df["value"].astype(float)
            df["time"] = pd.to_timedelta(df["time"].astype(str))
            return df

    def get_speed_data(self, startDate, endDate):
        ###
        # gets average mon, tue wed, etc, SPEED DATA by average hour
        ###
        # returns a dataframe
        ###
        ###

        locationString = "('" + ",'".join([str(s.id) for s in self]) + "')"
        sqlString = ""
        sqlString += "select obs.location_id,WEEKDAY(date) d,Hour(date) h,avg(value) avg,obs.direction_id, obs.obsclass_id classorder,dir.order "
        sqlString += f"directionorder from {DB_NAME}_observation obs "

        sqlString += f"join {DB_NAME}_locationdirection dir on dir.location_id = obs.location_id and dir.direction_id = obs.direction_id "
        sqlString += " where obs.location_id in " + locationString
        sqlString += " and obs.obsclass_id between 17 and 36 "
        sqlString += " group by location_id, d, h, obsclass_id,direction_id order by d,h,directionorder,classorder"

        # print(sqlString)
        with connections[DB_NAME].cursor() as cursor:
            cursor.execute(sqlString)
            result = cursor.fetchall()
            result = [list(l) for l in result]
            # print(result)
            return pd.DataFrame(result,
                                columns=["location", "day", "hour", "value", "direction_id", "classorder",
                                         "directionorder"])

    def format_for_sidebar(self, style=None):
        if style == "crt":
            result = {}
            for loc in self:
                areaName = loc.area.name if loc.area else "Unknown Area"
                if areaName not in result:
                    result[areaName] = []
                result[areaName].append(loc)
            print("from location quewryset")
            html = loader.render_to_string(f"{BASE_URL}/crt-style-sidebar.html",
                                           {"sensors": {"Classified Counts": result}})
        else:
            html = "<ul>"
            for loc in self.order_by("name"):
                html += "<li id='" + str(
                    loc.id) + "'><div class='sidebar-chevron' data-toggle='popover' onclick=\"location.href='viewLocation?id=" + str(
                    loc.id) + "';\" " \
                              "data-content='" + \
                    str(loc.name) + "' data-obstype='" + \
                    str(loc.observationType.id) + "'>"
                html += "<div class='sidebar-item'>"
                html += "<div class='sidebar-item-icon'><i class='" + str(
                    loc.observationType.iconURL) + "' style='color: blue;'></i></div>"
                html += "<div class='sidebar-item-details'><div class='sidebar-item-details-title' " \
                        " >" + str(loc.name) + "</div></div>"
                html += "</div></div></li>"
            html += "</ul>"
        return html

    def include_associated_locations(self):
        # locs = self.only("id").prefetch_related("associatedLocations")
        qs = Location.objects.none()
        for loc in self:
            qs = qs | loc.associatedLocations.all()
        return (self | qs).filter(virtual=0).distinct()

    def exclude_associated_locations(self):
        print("in exclude associated locations", self)
        locs = self  # .only("id").prefetch_related("associatedLocations")
        qs = Location.objects.none()
        for loc in locs:
            qs = qs | loc.associatedLocations.all()
        # print(list(self.exclude(id__in=qs.values_list("id",flat=True))))
        return self.exclude(id__in=qs.values_list("id", flat=True))

    def build_dataframe(self, data, **kwargs):
        #
        # take the data from various database queries and put it in a dataframe for processing
        # the dataframe has a 7 day range, monday to sunday, denoted by day 0-6
        #
        # print("kwargs are",kwargs)
        # print("in build dataframe, dates are",kwargs["startDate"],kwargs["endDate"])
        start = time.time() * 1000
        df = pd.DataFrame(data,
                          columns=["location", "day", "seg", "direction_id", "directionorder", "classorder", "value"])
        # print("created dataframe",len(df.index))
        # if self[0].round_to_places == 0:
        #     df["value"] = df["value"].astype(float)

        if len(df) != 0:
            if 'speed' not in kwargs:
                combined = df.groupby(
                    ["location", "day", "seg", "classorder"], as_index=False).agg({"value": "sum"})
                combined["directionorder"] = 2
                combined["direction_id"] = 0
                df = pd.concat([df, combined])
        else:
            df = pd.DataFrame(
                columns=["location", "day", "seg", "direction_id", "directionorder", "classorder", "value"])

        df.set_index(["location", "day", "seg", "classorder",
                     "directionorder"], inplace=True)
        return df

    def get_totals(self, **kwargs):
        ###
        # get the classed overall totals for time period in each day in the date range
        ###
        # dates should already be aware datetimes at this point, so that django can use them to retrieve the data in UTC
        ###
        # data is returned in UTC so that calling function can deal with timezones.
        ###
        # print("kwargs are",kwargs)
        # print("locs are",self)

        siteIds = [str(s.id) for s in self]

        if kwargs["period"] != "D":
            period = int(kwargs["period"])
            divisor = 60 * period
        else:
            divisor = 86400
        if "project" in kwargs and kwargs["dataType"] == "atc" or kwargs["dataType"] == "radar":
            aggregrate = " count(obsclass_id) as value "
            table = 'associatedobservation'
            groupBy = " group by location_id,obsclass_id,direction_id,dateadd(s,(DATEDIFF(s, '1970-01-01 00:00:00',[date])/ " + str(
                divisor) + ")*" + str(divisor) + ",'1970-01-01')"
        elif "project" in kwargs and kwargs["dataType"] == "link":
            aggregrate = " sum(value) as value "
            table = 'LINK_observation'
            groupBy = " group by location_id,obsclass_id,direction_id,dateadd(s,(DATEDIFF(s, '1970-01-01 00:00:00',[date])/ " + str(
                divisor) + ")*" + str(divisor) + ",'1970-01-01')"
        else:
            aggregrate = " sum(value) as value "
            table = 'observation'
            groupBy = " group by location_id,obsclass_id,direction_id,dateadd(s,(DATEDIFF(s, '1970-01-01 00:00:00',[date])/ " + str(
                divisor) + ")*" + str(divisor) + ",'1970-01-01')"

        sql = "SELECT 1 as id,(dateadd(s,(DATEDIFF(s, '1970-01-01 00:00:00',[date])/ " + str(divisor) + ")*" + str(
            divisor) + ",'1970-01-01')) as extractedDate, "
        sql += "location_id,obsClass_id,direction_id, "
        sql += aggregrate
        # sql += " value "
        sql += "from " + table + " where "
        sql += "location_id in " + "('" + "','".join(siteIds) + "')  "
        if "project" in kwargs:
            sql += " and project_id = " + str(kwargs["project"])
        else:
            sql += " and date >= '" + timezone.localtime(kwargs["startDate"], timezone.utc).strftime("%Y-%m-%d %H:%M") + \
                   "'  and  date < '" + timezone.localtime(kwargs["endDate"], timezone.utc).strftime(
                "%Y-%m-%d %H:%M") + "'"

        sql += groupBy
        print(sql)
        if "project" in kwargs and kwargs["dataType"] == "atc" or kwargs["dataType"] == "radar":
            results = AssociatedObservation.objects.using(DB_NAME).raw(sql)
        elif kwargs["dataType"] == "link":
            results = LINKObservation.objects.using(DB_NAME).raw(sql)
        else:
            results = Observation.objects.using(DB_NAME).raw(sql)

        prefetch_related_objects(results, "direction")
        prefetch_related_objects(results, "direction__direction")
        prefetch_related_objects(results, "obsClass__obsClass")

        data = [[item.location_id, item.extractedDate, 0, item.direction.direction.id if item.direction else 0,
                 item.direction.order if item.direction else 0, item.obsClass.order, round(item.value, 3)] for item in
                results]
        df = self.build_dataframe(data, **kwargs).reset_index()
        print("num df", len(df))
        df["value"] = df["value"].astype(float)
        if len(df) == 0:
            print("no data")
            return df
        df["day"] = pd.to_datetime(df['day'])
        infer_dst = np.array([False] * df.shape[0])
        df["day"] = df["day"].dt.tz_localize("UTC")

        return df

    def get_average_week(self, **kwargs):
        df = self.get_totals(**kwargs)
        df.drop("direction_id", inplace=True, axis=1)
        classList = [c.order for c in self[0].classes.all()]
        locsDict = {s.id: s for s in self}
        siteIds = [s.id for s in self]
        if kwargs["period"] != "D":
            kwargs["period"] += "min"

        rangefrom = kwargs["startDate"] - \
            datetime.timedelta(days=kwargs["startDate"].weekday())
        rangeto = kwargs["endDate"] + \
            datetime.timedelta(days=7 - kwargs["startDate"].weekday())
        rng = pd.date_range(
            rangefrom, rangeto, freq=kwargs["period"], closed='left', ambiguous=True).tz_convert('UTC')

        index = pd.MultiIndex.from_product([siteIds, rng, classList, range(3)],
                                           names=["location", "day", "classorder", "directionorder"])

        df.set_index(["location", "day", "classorder",
                     "directionorder"], inplace=True)
        df = df.reindex(index, fill_value=None)
        df = df.reset_index()
        df = df.groupby(["location", df['day'].dt.weekday,
                        df['day'].dt.time, "classorder", "directionorder"]).mean()
        # df = df.groupby(["location", df['day'].dt.weekday, df['day'].dt.time, "classorder", "directionorder"]).agg({'value': 'sum'})
        df.index = df.index.set_names(
            ["location", "day", "time", "classorder", "directionorder"])
        df = df.reset_index()
        return df

    def get_average_week2(self, **kwargs):
        ###
        # dates are aware datetimes, need to convert them to UTC for the sql query
        ###
        hourMulti = 60 / int(kwargs["period"])
        siteIds = [str(s.id) for s in self]
        numClasses = len(self[0].classes.all())
        locationString = "('" + "','".join(siteIds) + "')"
        mysqlString = "select o.location_id,convertedDay,convertedSeg,d.direction_id,d.order,c.order, "
        mysqlString += "round(" + self[0].aggFunc_as_string + \
            "(av)," + str(self[0].round_to_places) + ") from"
        mysqlString += " (select location_id,WEEKDAY(CONVERT_TZ(date,'UTC','Europe/London')) as convertedDay," \
                       " (HOUR(CONVERT_TZ(date,'UTC','Europe/London')) * " + str(hourMulti) + ") " \
                                                                                              "+ MINUTE(CONVERT_TZ(date,'UTC','Europe/London')) DIV " + \
                       kwargs["period"] + " as convertedSeg,"

        mysqlString += " round(avg(value)," + \
            str(self[0].round_to_places) + ") av "

        mysqlString += f",obsclass_id,direction_id from {DB_NAME}_observation  " \
                       "where location_id in " + locationString
        mysqlString += " and date >= '" + timezone.localtime(kwargs["startDate"], timezone.utc).strftime(
            "%Y-%m-%d %H:%M") + "' "
        mysqlString += " and  date < '" + timezone.localtime(kwargs["endDate"], timezone.utc).strftime(
            "%Y-%m-%d %H:%M") + "' "
        if "day" in kwargs:
            mysqlString += " and WEEKDAY(CONVERT_TZ(date,'UTC','Europe/London')) = " + str(
                kwargs["day"]) + " "
        mysqlString += "group by convertedDay,segment,obsclass_id,direction_id) o "
        mysqlString += f" join {DB_NAME}_locationobservationclass c on o.obsclass_id = c.id "
        mysqlString += f" join {DB_NAME}_locationdirection d on o.direction_id = d.id "
        mysqlString += " group by o.location_id,o.obsclass_id,o.direction_id,o.convertedDay,o.convertedSeg "
        # print(mysqlString)
        with connections[DB_NAME].cursor() as cursor:
            cursor.execute(mysqlString)
            result = cursor.fetchall()
            result = [list(l) for l in result]
            periodRange = range(24 * 60 // int(kwargs["period"]))
            index = pd.MultiIndex.from_product([siteIds, range(7), periodRange, range(numClasses), range(3)],
                                               names=["location", "day", "seg", "classorder", "directionorder"])
            df = self.build_dataframe(result, **kwargs)
            df = df.reindex(index, fill_value=np.nan).reset_index()
            df["value"] = df["value"].astype(float)
            return df

    def fill_crt_averages_table(self, **kwargs):
        if "table" in kwargs:
            table = kwargs["table"]
        else:
            table = "crt_full_averages"
        siteIds = [str(s.id) for s in self]
        locationString = "('" + "','".join(siteIds) + "')"

        sqlString = " Insert into [Traffic_hub].[dbo].[" + str(table)
        sqlString += "] (location_id,direction_id,obsClass_id,[weekday],segment,[value]) "
        sqlString += "select location_id,direction_id,obsclass_id,  "
        sqlString += "CASE "
        sqlString += " When DATEPART(WEEKDAY, date)>1 and DATEPART(WEEKDAY, [date])<7 Then 1 "
        sqlString += " When DATEPART(WEEKDAY, date) = 7 Then 2 "
        sqlString += " When DATEPART(WEEKDAY, date) = 1 Then 3 "
        sqlString += " END "
        sqlString += " as convertedweekday , segment,  avg([value]) as value "
        sqlString += " from observation as o "
        sqlString += " where o.location_id in " + locationString
        if "startDate" in kwargs:
            sqlString += " and o.date >=  '" + \
                kwargs["startDate"].strftime("%Y-%m-%d") + "' "
            sqlString += " and o.date <= '" + \
                kwargs["endDate"].strftime("%Y-%m-%d") + "' "
        sqlString += " group by o.location_id,o.obsclass_id,o.direction_id,segment, "
        sqlString += " CASE "
        sqlString += " When DATEPART(WEEKDAY, date)>1 and DATEPART(WEEKDAY, [date])<7 Then 1  "
        sqlString += " When DATEPART(WEEKDAY, date) = 7 Then 2 "
        sqlString += " When DATEPART(WEEKDAY, date) = 1 Then 3 "
        sqlString += " END "
        sqlString += " order by convertedweekday,segment; "
        print(sqlString)
        print("starting", datetime.datetime.now())
        try:
            with connections[DB_NAME].cursor() as cursor:
                print("cursor - ", cursor)
                cursor.execute(sqlString)

                print("finished query", datetime.datetime.now())
        except Exception as e:
            print(e, sys.exc_info()[0])
            raise Exception("error in query")

    def get_temp_table_name(self, **kwargs):
        if "customRange" not in kwargs:
            return "crt_full_averages"
        kwargs["table"] = kwargs["table"] + kwargs["startDate"].strftime("%d%m%Y") + kwargs["endDate"].strftime(
            "%d%m%Y")
        fill = False
        with closing(connections[DB_NAME].cursor()) as cur:
            cur.execute("SELECT count(*) FROM [Traffic_hub].information_schema.TABLES WHERE "
                        " TABLE_NAME = '" + kwargs["table"] + "'")
            result = cur.fetchall()
            print("result is", result[0][0])
            if result[0][0]:
                cur.execute("select location_id,count(id) from " +
                            kwargs["table"] + " group by location_id")
                counts = cur.fetchall()
                counts = {c[0]: c[1] for c in counts}
                for site in self:
                    if site.id not in counts or counts[site.id] == 0:
                        print("in countlines")
                        cur.execute("truncate table " + kwargs["table"])
                        print("table contents dont match countlines")
                        fill = True
                        break
            else:
                print("table doesnt exist, creating table")
                # cur.execute("CREATE table " + kwargs["table"] + " [like] 'crt_full_averages'")
                cur.execute("Select Top 0 * into  " +
                            kwargs["table"] + " FROM crt_full_averages")
                fill = True
        if fill:
            print("going to fill table")
            self.fill_crt_averages_table(**kwargs)
        return kwargs["table"]

    def get_data_from_crt_averages_table(self, **kwargs):
        """
        :param kwargs: weekday :  1=week, 2=sat, 3 = sun, 4 = all
        :return: dataframe of count data

        the aggregation function differs depending on whether the sensors are counts, atcs, air quality, etc
        eg air quality the final aggregation is an average, where a vivacity count is summed up
        this assumes that the sensor types are all the same for each queryset

        """
        siteIds = [s.id for s in self]
        str_siteIds = [str(s.id) for s in self]
        numClasses = len(self[0].classes.all())
        locationString = "('" + "','".join(str_siteIds) + "')"
        table = self.get_temp_table_name(**kwargs)
        # return
        hourDivisor = int(kwargs["period"]) // 5
        print("hourDivisor is", hourDivisor)
        if kwargs["weekday"] != 4:
            weekdayIndicator = "0 "
        else:
            weekdayIndicator = " o.weekday - 1 "
        sqlString = "select o.location_id," + \
            weekdayIndicator + ", o.segment / " + str(hourDivisor)
        sqlString += " as seg ,d.direction_id,d.[order],c.[order]," + self[0].aggFunc_as_string + "(value) from " + str(
            table) + " as o "
        sqlString += f" join locationobservationclass as c on o.obsclass_id = c.id "
        sqlString += f" join locationdirection as d on o.direction_id = d.id "
        sqlString += " where o.location_id in " + locationString
        if kwargs["weekday"] != 4:
            sqlString += " and weekday = " + str(kwargs["weekday"])
        sqlString += " group by o.location_id,o.weekday - 1,o.segment/" + str(
            hourDivisor) + ",d.direction_id,d.[order],c.[order] "
        print('get_data_from_crt_averages_table - ', sqlString)
        start = time.time() * 1000
        with connections[DB_NAME].cursor() as cursor:
            cursor.execute(sqlString)
            result = cursor.fetchall()
            # print("database access took", time.time() * 1000 - start)
            result = [list(l) for l in result]
            # print("database access took",time.time() * 1000 - start)
            periodRange = range(24 * 60 // int(kwargs["period"]))
            # print("set index")
            index = pd.MultiIndex.from_product([siteIds, range(3), periodRange, range(numClasses), range(3)],
                                               names=["location", "day", "seg", "classorder", "directionorder"])
            # print(index)

            df = self.build_dataframe(result, **kwargs)
            dup = df.index.duplicated()
            df = df.reindex(index, fill_value=None)
            print("printing duplicated")
            df["value"] = df["value"].round(3)
            print("value rounded")
            df["value"] = df["value"].fillna("-")
            print("end ")
            return df.reset_index()

    def get_factoring_data(self, tz="Europe/London", **kwargs):

        temp = self.filter(temp=True)[0]
        startDate = Observation.objects.using(DB_NAME).filter(
            location=temp, status=0).earliest("date").date
        endDate = Observation.objects.using(DB_NAME).filter(
            location=temp, status=0).latest("date").date

        kwargs["startDate"] = startDate
        kwargs["endDate"] = endDate + datetime.timedelta(days=1)
        kwargs["customRange"] = True

        #
        # calculate and get the averages for the custom date range of the temp site
        #
        kwargs["weekday"] = 4
        fullDf = self.get_data_from_crt_averages_table(**kwargs)
        fullDf = fullDf[fullDf["day"] < 3]
        # fullDf.to_csv("full df before join.csv")
        #
        # get the full averages from the crt_averages_table
        #
        del kwargs["customRange"]
        kwargs["weekday"] = 4
        weekdayDf = self.get_data_from_crt_averages_table(**kwargs)
        weekdayDf = weekdayDf[weekdayDf["day"] < 3]
        weekdayDf.loc[weekdayDf["day"] == 0, "day"] = 3
        weekdayDf.loc[weekdayDf["day"] == 1, "day"] = 4
        weekdayDf.loc[weekdayDf["day"] == 2, "day"] = 5
        fullDf = fullDf.append([weekdayDf])
        return fullDf

    def format_dataframe_for_download(self, df, **kwargs):
        locsDict = {s.id: s for s in self}
        classList = [c.obsClass.name for c in self[0].classes.all()]

        def apply_direction(row):
            # print("applying",row)
            try:
                if row["directionorder"] == 2:
                    return "Combined"
                return locsDict[row["location"]].directions.all()[row["directionorder"]].direction.descriptive
            except IndexError as e:
                return "Drop"

        def apply_area(row):
            return locsDict[row["location"]].area.name

        df["directionorder"] = df.apply(apply_direction, axis=1)
        df = df[df["directionorder"] != "Drop"]
        df["Area"] = df.apply(apply_area, axis=1)
        cols = df.columns
        # print("columns are", cols)
        df = df[["Area", "location", "day", "Date", "directionorder"] + [c for c in cols if
                                                                         c not in ["Area", "location", "day", "Date",
                                                                                   "directionorder"]]]
        df.columns = ["Area", "Site", "day", "Date",
                      "Direction"] + [c.title() for c in classList]
        nonSelectedColumns = [c.obsClass.name.title() for c in self[0].classes.all() if
                              c.obsClass.id not in kwargs["classes"]]
        df.drop(nonSelectedColumns, inplace=True, axis=1)
        df['Total'] = df.iloc[:, 3:].sum(axis=1)

        df.fillna("-", inplace=True)

        if kwargs["direction"] == "split":
            return df[df["Direction"] != "Combined"]
        else:
            return df[df["Direction"] == "Combined"]

    def download_totals(self, **kwargs):
        timezone.activate("UTC")
        kwargs["startDate"] = timezone.make_aware(kwargs["startDate"])
        kwargs["endDate"] = timezone.make_aware(kwargs["endDate"])
        df = self.get_totals(**kwargs)
        print("len df -", len(df))
        if len(df):
            df["day"] = df["day"].dt.tz_convert(kwargs["clientTz"])
        df.drop("direction_id", inplace=True, axis=1)
        classList = [c.obsClass.name for c in self[0].classes.all()]
        dirList = [d.direction.descriptive for d in self[0].directions.all()]
        locsDict = {s.id: s for s in self}
        siteIds = [s.id for s in self]
        if kwargs["period"] != "D":
            kwargs["period"] += "min"
            rng = pd.date_range(kwargs["startDate"], kwargs["endDate"], freq=kwargs["period"], closed='left',
                                ambiguous=True, nonexistent='shift_forward')
        else:
            # because we get back the data in UTC and then convert it to the client Tz, if its daily totals we get
            # back data with time 00:00:00 which when converted to the client Tz can end up as 00:01:00
            # which then doesnt get matched to the reindexing range
            offset = datetime.timedelta(days=0)
            rng = pd.date_range(kwargs["startDate"] + offset, kwargs["endDate"] + offset, freq=kwargs["period"],
                                closed='left', ambiguous=True, nonexistent='shift_forward').tz_convert('UTC')
        index = pd.MultiIndex.from_product([siteIds, rng, range(len(classList)), range(len(dirList) + 1)],
                                           names=["location", "day", "classorder", "directionorder"])
        df.set_index(["location", "day", "classorder",
                     "directionorder"], inplace=True)
        df = df.reindex(index, fill_value=-1).reset_index()
        df = pd.pivot_table(df, values="value", columns="classorder",
                            index=["location", "day", "directionorder"]).reset_index()
        print("replacing minus one")
        df = df.replace(-1, np.nan)

        def apply_direction(row):
            if row["directionorder"] == len(dirList):
                return "Combined"
            try:
                return locsDict[row["location"]].directions.all()[row["directionorder"]].direction.descriptive
            except Exception as e:
                return "Drop"

        def apply_area(row):
            return locsDict[int(row["location"])].area.name

        df["directionorder"] = df.apply(apply_direction, axis=1)
        df = df.dropna(axis=0, subset=["directionorder"])
        df = df[df["directionorder"] != "Drop"]
        #
        # add in area column, split date into date and time, and then re-order columns
        #
        df["Area"] = df.apply(apply_area, axis=1)
        df["Time"] = df["day"].dt.time
        df["Date"] = df["day"].dt.date
        df.drop("day", inplace=True, axis=1)
        cols = df.columns
        df = df[["Area", "location", "Date", "Time", "directionorder"] + [c for c in cols if
                                                                          c not in ["Area", "location", "Date", "Time",
                                                                                    "directionorder"]]]

        df.columns = ["Area", "Site", "Date", "Time",
                      "Direction"] + [c.title() for c in classList]
        nonSelectedColumns = [c.obsClass.name.title() for c in self[0].classes.all() if
                              c.obsClass.id not in kwargs["classes"]]
        df.drop(nonSelectedColumns, inplace=True, axis=1)
        print("after non selecting - ", len(df))
        if self[0].observationType.id == 1:
            df['Total'] = df.iloc[:, 3:].sum(axis=1)
        df.fillna("-", inplace=True)
        if kwargs["direction"] == "split":
            df = df[df["Direction"] != "Combined"]
            print("after split - ", len(df))
        else:
            df = df[df["Direction"] == "Combined"]
        print("length of dataframe at last -", len(df))
        return df

    def build_chart_structure(self, df):
        grps = df.groupby(["location", "day", "directionorder", "classorder"])
        index = [key for key, _ in grps]
        l = grps["value"].apply(list)
        result = list(zip(index, l))
        output = {}
        for loc in self:
            output[loc.id] = {"directions": [
                {"order": i, "baseData": []} for i in range(3)]}
            for i in range(3):  # directions
                for d in range(9):  # number of days + 5 and 7 day averages
                    data = []
                    # classes
                    for classIndex, item in enumerate(loc.classes.all()):
                        data.append({"label": item.obsClass.name, "data": [], "borderColor": classColors[classIndex],
                                     "fill": False, "pointRadius": 0, "borderWidth": 1,
                                     "backgroundColor": classColors[classIndex]})
                    output[loc.id]["directions"][i]["baseData"].append(data)
        for item in result:
            index, data = item
            locId, day, d_order, classorder = index
            # print(type(locId), day, d_order, classorder,data)
            try:
                output[int(
                    locId)]["directions"][d_order]["baseData"][day][classorder]["data"] = data
            except Exception as e:
                print("error", e)
        return output

    def get_totals_speed(self, **kwargs):

        siteIds = [str(s.id) for s in self]
        if kwargs["period"] != "D":
            period = int(kwargs["period"])
            divisor = 60 * period
            # groupBy = " group by id,location_id,extractedDate,obsclass_id,direction_id,dateadd(s,(DATEDIFF(s, '1970-01-01 00:00:00',[date])/ " + str(divisor) + ")*" + str(divisor) + ",'1970-01-01')"
        else:
            divisor = 86400

        sql = "SELECT 1 as id,convert(char(14),[date],121)+'00:00.000000' as extractedDate, "
        sql += "location_id,obsClass_id,direction_id,value "
        sql += "from associatedobservation where "
        sql += "location_id in " + "('" + "','".join(siteIds) + "')  "
        sql += " and project_id = " + str(kwargs["project"])
        # sql += " group by value,location_id,obsclass_id,direction_id,convert(char(14),[date],121)+'00:00.0000'"
        print(sql)
        results = AssociatedObservation.objects.using(DB_NAME).raw(sql)
        prefetch_related_objects(results, "direction")
        prefetch_related_objects(results, "direction__direction")
        prefetch_related_objects(results, "obsClass__obsClass")
        data = [[item.location_id, item.extractedDate, 0, item.direction.direction.id if item.direction else 0,
                 item.direction.order if item.direction else 0, item.obsClass.order, round(item.value, 3)] for item in
                results]
        print("length -", len(data))

        # dataframe = pd.DataFrame(data,
        #   columns=["location", "day", "seg", "direction_id", "directionorder", "classorder", "value"])
        return self.build_dataframe(data, **kwargs).reset_index()

    def reset_index(self, df):
        siteIds = [s.id for s in self]
        time_rng = pd.date_range("00:00", "23:00", freq="60min").time
        index = pd.MultiIndex.from_product([siteIds, range(9), time_rng, range(3)],
                                           names=["location", "day", "time", "directionorder"])
        index = index.to_frame(index=False)
        return pd.merge(index, df, how="left", left_on=["location", "day", "time", "directionorder"],
                        right_on=["location", "day", "time", "directionorder"])

    def get_atc_counts(self, **kwargs):
        df = self.get_totals_speed(**kwargs)
        if len(df) == 0:
            print("no data")
            value = {}.fromkeys(
                range(24), {'speed': {}.fromkeys(range(20), 0), 'count': 0})
            # days = {}.fromkeys(range(9),{'direction' : {}.fromkeys(range(3),{'data':value})})
            days = [{'direction': [{'data': value}
                                   for y in range(3)]} for x in range(9)]
            return days
        df["day"] = pd.to_datetime(df["day"])
        df["day"] = df["day"].dt.tz_localize("UTC")
        df["time"] = df["day"].dt.time
        df["day"] = df["day"].dt.weekday
        df.drop("direction_id", inplace=True, axis=1)
        df.drop("classorder", inplace=True, axis=1)
        df.drop("seg", inplace=True, axis=1)

        for i in range(0, 20):
            df[i] = 0
            df[i] = np.where(df['value'] // 5 == i, 1, 0)
        df['count'] = np.where(df['value'] > 0, 1, 0)
        df = df.groupby(["location", "day", "directionorder", "time"]).sum()
        df = df.reset_index()
        aggr = {}.fromkeys(range(0, 20), lambda x: x.sum(skipna=True))
        aggr['count'] = lambda x: x.sum(skipna=True)
        combined = df.groupby(["location", "day", "time"],
                              as_index=False).agg(aggr)
        combined["directionorder"] = 2
        combined = combined.reset_index()
        df = pd.concat([df, combined])
        df.drop("index", inplace=True, axis=1)
        for i in range(0, 20):
            df[i].replace({0: None}, inplace=True)

        df['count'].replace({0: None}, inplace=True)
        aggr = {}.fromkeys(range(0, 20), lambda x: x.mean(skipna=True))
        aggr['count'] = lambda x: x.mean(skipna=True)
        avg5day = df[(df["day"] < 5)]
        avg5day = avg5day.groupby(
            ["location", "directionorder", "time"], as_index=False).agg(aggr)
        avg5day["day"] = 7
        avg7day = df.groupby(
            ["location", "directionorder", "time"], as_index=False).agg(aggr)
        avg7day["day"] = 8
        df.drop("value", inplace=True, axis=1)
        df = pd.concat([df, avg5day, avg7day])
        for i in range(0, 20):
            df[i].replace({None: 0}, inplace=True)
        df['count'].replace({0: None}, inplace=True)
        df = self.reset_index(df)
        df.fillna(0, inplace=True)
        days = [x for x in range(9)]
        for d in days:
            day = df[df['day'] == d]
            direction = [x for x in range(3)]
            for dir in direction:
                directn = day[day['directionorder'] == dir]
                t1 = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                t2 = datetime.datetime.now().replace(hour=23, minute=00, second=0, microsecond=0)
                value = []
                while t1 <= t2:
                    time = directn[directn['time'] == t1.time()]
                    speed = time[[x for x in range(20)]].values[0]
                    speed = [int(x) for x in speed]
                    count = round(time['count'].values[0])
                    t1 += datetime.timedelta(hours=1)
                    value.append({'speed': speed, 'count': count})
                direction[dir] = {'data': value}
            days[d] = {'direction': direction}
        return days

    def get_atc_psl(self, **kwargs):
        df = self.get_totals_speed(**kwargs)
        if len(df) == 0:
            print("no data")
            value = {'acpo': ["-" for x in range(24)], 'acpo_per': ["-" for x in range(24)],
                     "dft": ["-" for x in range(24)], "dft_per": ["-" for x in range(24)],
                     "psl": ["-" for x in range(24)], "psl_per": ["-" for x in range(24)]}
            days = [{'direction': [{'data': value}
                                   for y in range(3)]} for x in range(9)]
            return days
        df["day"] = pd.to_datetime(df["day"])
        df["day"] = df["day"].dt.tz_localize("UTC")
        df["time"] = df["day"].dt.time
        df["day"] = df["day"].dt.weekday
        df.drop("direction_id", inplace=True, axis=1)
        df.drop("classorder", inplace=True, axis=1)
        df.drop("seg", inplace=True, axis=1)

        count = df.groupby(["location", "day", "directionorder", "time"]).agg(
            {'value': 'count'})
        count = count.reset_index()
        count['count'] = count['value']
        count.drop('value', inplace=True, axis=1)

        df["PSL"] = np.where(df['value'] >= kwargs['PSL'], 1, 0)
        df["ACPO"] = np.where(df['value'] >= kwargs['ACPO'], 1, 0)
        df["DFT"] = np.where(df['value'] >= kwargs['DFT'], 1, 0)
        df.drop("value", inplace=True, axis=1)
        df = df.groupby(["location", "day", "directionorder", "time"]).agg(
            {"PSL": 'sum', "ACPO": 'sum', "DFT": 'sum'})
        df = df.reset_index()
        df = df.join(count['count'])

        combined = df.groupby(["location", "day", "time"], as_index=False).agg(
            {'PSL': sum, 'ACPO': sum, 'DFT': sum, 'count': sum})
        combined["directionorder"] = 2
        combined = combined.reset_index()
        combined.drop("index", inplace=True, axis=1)
        df = pd.concat([df, combined])

        # df["%PSL"] = ((df["PSL"]/df["count"])*100)
        # df["%ACPO"] = ((df["ACPO"]/df["count"])*100)
        # df["%DFT"] = ((df["DFT"]/df["count"])*100)

        def mean_lmbda(x): return x.mean(skipna=True)
        avg5day = df[(df["day"] < 5)]
        avg5day = avg5day.groupby(["location", "directionorder", "time"], as_index=False).agg(
            {'PSL': mean_lmbda, 'ACPO': mean_lmbda, 'DFT': mean_lmbda, 'count': mean_lmbda})
        avg5day["day"] = 7
        avg7day = df.groupby(["location", "directionorder", "time"], as_index=False).agg(
            {'PSL': 'mean', 'ACPO': 'mean', 'DFT': 'mean', 'count': 'mean'})
        avg7day["day"] = 8
        df = pd.concat([df, avg5day, avg7day])

        # df = df.applymap(lambda x: int(round(x, 0)) if isinstance(x, (int, float)) else x)

        df = self.reset_index(df)
        df.fillna("-", inplace=True)

        days = [x for x in range(9)]
        for d in days:
            day = df[df['day'] == d]
            direction = [x for x in range(3)]
            for dir in direction:
                directn = day[day['directionorder'] == dir]
                t1 = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                t2 = datetime.datetime.now().replace(hour=23, minute=00, second=0, microsecond=0)
                psl = []
                acpo = []
                dft = []
                psl_per = []
                acpo_per = []
                dft_per = []
                count = []
                while t1 <= t2:
                    time = directn[directn['time'] == t1.time()]
                    psl.append(
                        round(time['PSL'].values[0]) if type(time['PSL'].values[0]) == float else time['PSL'].values[0])
                    acpo.append(
                        round(time['ACPO'].values[0]) if type(time['ACPO'].values[0]) == float else time['ACPO'].values[
                            0])
                    dft.append(
                        round(time['DFT'].values[0]) if type(time['DFT'].values[0]) == float else time['DFT'].values[0])
                    psl_per.append(
                        round(((time['PSL'].values[0] / time['count'].values[0]) * 100)) if time['PSL'].values[
                            0] != "-" else "-")
                    acpo_per.append(
                        round(((time['ACPO'].values[0] / time['count'].values[0]) * 100)) if time['ACPO'].values[
                            0] != "-" else "-")
                    dft_per.append(
                        round(((time['DFT'].values[0] / time['count'].values[0]) * 100)) if time['DFT'].values[
                            0] != "-" else "-")

                    count.append(round(time['count'].values[0]) if type(time['count'].values[0]) == float else
                                 time['count'].values[0])
                    t1 += datetime.timedelta(hours=1)
                direction[dir] = {
                    'data': {'psl': psl, 'acpo': acpo, 'dft': dft, 'psl_per': psl_per, 'acpo_per': acpo_per,
                             'dft_per': dft_per, "count": count}}
            days[d] = {'direction': direction}
        return days

    def as_daily_hourly_classed_chart_datasets(self, classes, **kwargs):
        # allLocations = self.include_associated_locations()
        # print("in classed chart datasets, kwargs are",kwargs)

        if "table" in kwargs:
            if "factoring" in kwargs:
                df = self.get_factoring_data(**kwargs)
            else:
                print("getting full averages", datetime.datetime.now())
                df = self.get_data_from_crt_averages_table(**kwargs)
                # chartStructure = self.build_chart_structure(df)
                # return chartStructure
        else:
            def calc_avg(row):
                # print
                lst = [i for i in row.values.tolist() if i !=
                       0 and not (np.isnan(i))]
                return (sum(lst) / len(lst)) if len(lst) > 0 else 0

            df = self.get_average_week(**kwargs)
            # return

            if len(df) > 0:
                avg5day = df[df["day"] < 5].groupby(["location", "directionorder", "classorder", "time"],
                                                    as_index=False).agg({"value": lambda x: x.mean(skipna=True)})
                # print(avg5day)
                # avg5day["value"] = avg5day["value"].astype(float).apply(np.round).round(1).fillna("-")
                # print("avg5day is",avg5day)
                avg5day["day"] = 7
                avg7day = df.groupby(["location", "directionorder", "classorder", "time"], as_index=False).agg(
                    {"value": lambda x: x.mean(skipna=True)})
                # avg7day["value"] = avg7day["value"].astype(float).apply(np.round).round(1).fillna("-")
                avg7day["day"] = 8
                df = pd.concat([df, avg5day, avg7day])
            if self[0].observationType.id == 1 or self[0].observationType.id == 4 or self[0].observationType.id == 9 or \
                    self[0].observationType.id == 10 or self[0].observationType.id == 12:
                df["value"] = df["value"].apply(np.round).round()
                # df['value'] = np.round(df['value'], decimals = 3)
                # df['value'] = round(df['value'],3)

            df["value"] = df["value"].replace(np.nan, "-")
        return self.build_chart_structure(df)

        if False:
            result = {}
            for loc in self:
                if loc.virtual:
                    locs = loc.associatedLocations.all().values_list("id", flat=True)
                else:
                    locs = [loc.id]
                directions = []
                df = fullDf[fullDf["location"].isin(locs)]
                directionOrder = range(
                    loc.locationdirection_set.all().count() + 1)
                for dirIndex in directionOrder:
                    direction = {"order": int(dirIndex), "baseData": []}
                    for day in range(7):
                        dataset = []
                        data = \
                            df[(df["directionorder"] == dirIndex) & (df["day"] == day)].groupby(["classorder", "seg"],
                                                                                                as_index=False) \
                            .agg({"value": "sum"}).groupby("classorder", as_index=False)["value"].apply(list).values
                        for classIndex, item in enumerate(classes):
                            dataset.append(
                                {"label": item.name, "data": data[classIndex], "borderColor": classColors[classIndex],
                                 "fill": False, "pointRadius": 0, "borderWidth": 1,
                                 "backgroundColor": classColors[classIndex]})
                        direction["baseData"].append(dataset)
                    avg5day = df[(df["day"] < 5) & (df["directionorder"] == int(dirIndex))].groupby(
                        ["classorder", "seg"], as_index=False).agg({"value": "mean"})
                    avg5day["value"] = avg5day["value"].astype(
                        float).apply(np.round).round(1).fillna("-")
                    data = avg5day.groupby(["classorder", "seg"], as_index=False) \
                        .agg({"value": "sum"}).groupby("classorder", as_index=False)["value"].apply(list).values
                    dataset = []
                    for classIndex, item in enumerate(classes):
                        dataset.append(
                            {"label": item.name, "data": data[classIndex], "borderColor": classColors[classIndex],
                             "fill": False, "pointRadius": 0, "borderWidth": 1,
                             "backgroundColor": classColors[classIndex]})
                    direction["baseData"].append(dataset)
                    avg7day = df[(df["directionorder"] == int(dirIndex))].groupby(
                        ["classorder", "seg"], as_index=False).agg({"value": "mean"})
                    avg7day["value"] = avg7day["value"].astype(
                        float).apply(np.round).round(1).fillna("-")
                    data = avg7day.groupby(["classorder", "seg"], as_index=False) \
                        .agg({"value": "sum"}).groupby("classorder", as_index=False)["value"].apply(list).values
                    dataset = []
                    for classIndex, item in enumerate(classes):
                        dataset.append(
                            {"label": item.name, "data": data[classIndex], "borderColor": classColors[classIndex],
                             "fill": False, "pointRadius": 0, "borderWidth": 1,
                             "backgroundColor": classColors[classIndex]})
                    direction["baseData"].append(dataset)
                    directions.append(direction)
                    # print("finished 7 day", datetime.datetime.now())

                result[loc.id] = {"directions": directions}
        print("finished full data formatting", datetime.datetime.now())
        return result

    def get_classed_occupancy(self, **kwargs):
        classes = ObservationClass.objects.using(DB_NAME).filter(
            locationobservationclass__location=self[0]).order_by("locationobservationclass__order")
        # print("starting db query",datetime.datetime.now())
        df = self.get_average_week2(**kwargs)
        df = df[df["directionorder"] < 2]
        df.loc[df["directionorder"] == 0, "direction_id"] = 4
        df.loc[df["directionorder"] == 1, "direction_id"] = 3
        df = df.groupby(["day", "seg", "direction_id", "classorder"],
                        as_index=False).agg({"value": "sum"})
        # df.to_csv("output.csv")
        df["occupancy"] = df.groupby(
            ["day", "classorder", "direction_id"], as_index=False)["value"].cumsum()
        outdf = df[df["direction_id"] == 4]
        indf = df[df["direction_id"] == 3]
        result = indf.merge(outdf, on=["day", "classorder", "seg"])
        result["value"] = result["occupancy_x"] - result["occupancy_y"]
        directions = []
        directionOrder = [4, 3]
        df["value"] = df["value"].astype(float).apply(np.round).fillna("-")
        for dirIndex in directionOrder:
            direction = {"order": int(dirIndex), "baseData": []}
            for day in range(7):
                dataset = []
                data = \
                    df[(df["direction_id"] == dirIndex) & (df["day"] == day)].groupby(["classorder", "seg"],
                                                                                      as_index=False) \
                    .agg({"value": "sum"}).groupby("classorder", as_index=False)["value"].apply(list).values
                if dirIndex == 4:
                    ##
                    # direction is OUTBOUND, want to make all values negative to show on graph
                    ###
                    data = [[0 - item if type(item) == int or type(item) == float else "-" for item in classData] for
                            classData in data]
                    # print("data is now",data)
                for classIndex, item in enumerate(classes):
                    dataset.append(
                        {"label": item.name, "data": data[classIndex], "borderColor": classColors[classIndex],
                         "fill": False, "pointRadius": 0, "borderWidth": 1,
                         "backgroundColor": classColors[classIndex]})
                direction["baseData"].append(dataset)
            directions.append(direction)
        direction = {"order": 2, "baseData": []}
        for day in range(7):
            dataset = []

            data = result[(result["day"] == day)].groupby(["classorder", "seg"], as_index=False) \
                .agg({"value": "sum"}).groupby("classorder", as_index=False)["value"].apply(list).values

            # print("data for day", day, "is", data)
            for classIndex, item in enumerate(classes):
                dataset.append(
                    {"label": item.name, "data": data[classIndex], "borderColor": classColors[classIndex],
                     "fill": False, "pointRadius": 0, "borderWidth": 1,
                     "backgroundColor": classColors[classIndex]})
            direction["baseData"].append(dataset)
        directions.append(direction)
        return directions

    def get_classed_volumes(self, tz="Europe/London", **kwargs):

        timezone.activate(tz)
        kwargs["startDate"] = timezone.make_aware(
            datetime.datetime.strptime(kwargs["startDate"], "%Y-%m-%d %H:%M"))
        kwargs["endDate"] = timezone.make_aware(
            datetime.datetime.strptime(kwargs["endDate"], "%Y-%m-%d %H:%M"))
        kwargs["clientTz"] = tz

        result = {}
        timeString = ""
        classes = self[0].classes.all()
        if "live" in kwargs:
            print("live")
            kwargs["period"] = "D"
            if kwargs["live"] == "ALL":
                kwargs["endDate"] = kwargs["startDate"] + \
                    datetime.timedelta(days=1)
                timeString = kwargs["startDate"].strftime(
                    "%A %b %d %Y, 00:00 - 24:00")
            else:
                latest = timezone.localtime(
                    Location.objects.using(DB_NAME).get(id="Birmingham_Barclaycard_Arena").observation_set.all().latest(
                        "date").date)
                kwargs["endDate"] = latest
                kwargs["startDate"] = (
                    latest - datetime.timedelta(minutes=int(kwargs["live"])))
                timeString = (kwargs["startDate"] + datetime.timedelta(minutes=5)).strftime("%A %b %d %Y, %H:%M - " +
                                                                                            (kwargs[
                                                                                                "endDate"] + datetime.timedelta(
                                                                                                minutes=5)).strftime(
                                                                                                "%H:%M"))
            df = self.filter(observationType_id=1,
                             temp=False).get_totals(**kwargs)
            df.drop("direction_id", axis=1, inplace=True)
            df.set_index(["location", "day", "classorder",
                         "directionorder"], inplace=True)
            rng = pd.date_range(kwargs["startDate"].replace(hour=0, minute=0, second=0, tzinfo=pytz.timezone("UTC")),
                                (kwargs["startDate"].replace(hour=0, minute=0, second=0,
                                                             tzinfo=pytz.timezone("UTC")) + datetime.timedelta(days=1)), freq="D", closed='left', ambiguous=True)
            index = pd.MultiIndex.from_product([[s.id for s in self], rng, range(len(classes)), range(3)],
                                               names=["location", "day", "classorder", "directionorder"])
            # print("index is",rng)
            df = df.reindex(index, fill_value="-").reset_index()
            df["day"] = 0

            result = self.build_chart_structure(df)
        elif kwargs["resultType"] == "counts":

            result = self.as_daily_hourly_classed_chart_datasets(
                classes, **kwargs)
        else:
            loc = self[0]
            locs = loc.associatedLocations.all()
            result[loc.id] = {
                "directions": locs.get_classed_occupancy(**kwargs)}

        rng = pd.date_range('2011-03-01 00:00', '2011-03-02 00:00',
                            freq=(kwargs["period"] + 'T') if kwargs["period"] != "D" else "D", ambiguous=True)
        eventEndDate = kwargs["endDate"].date() if kwargs["endDate"].date() != kwargs["startDate"].date() \
            else (kwargs["endDate"] + datetime.timedelta(days=1)).date()
        return {"data": result, "selectors": classes.as_dashboard_graph_selectors(), "time": timeString,
                "graphLabels": [r[:5] for r in rng.time.astype(str)],
                "events": Event.objects.using(DB_NAME).filter(date__gte=kwargs["startDate"].date(),
                                                              date__lt=eventEndDate).order_by("-date").as_html()}

    def update_status(self):
        print("updating status of api locations")
        for cl in self:
            print("updating", cl.id)
            try:
                if cl.virtual == 0:
                    latest = cl.observation_set.latest("date").date
                    try:
                        latestNonZero = cl.observation_set.filter(value__gt=0,
                                                                  date__gte=(
                                                                      datetime.datetime.now() - datetime.timedelta(
                                                                          days=1)).date()).latest("date").date
                    except Exception as e:
                        #
                        # if we dont find the latest non zero, we just set to None
                        #
                        latestNonZero = None
                else:
                    latest = None
                    latestNonZero = None
                cl.lastDataReceived = latest
                if latestNonZero:
                    cl.lastNonZeroDataReceived = latestNonZero
                cl.save()
                if cl.lastDataReceived is not None:
                    diff = pytz.utc.localize(
                        datetime.datetime.utcnow()) - cl.lastDataReceived
                    if cl.status != "offline" and diff.total_seconds() > 86400:
                        cl.status = "offline"
                        cl.save()
                        automatedemails.sendMail(SEND_MAIL_TO, f"{DB_NAME} API recording - sensor potentially offline",
                                                 "Countline " + str(cl.name) +
                                                 " has been marked offline at " + datetime.datetime.now().strftime(
                                                     "%d/%m/%Y %H:%M:%S") +
                                                 " as it is more than 12 hours since the last data was received",
                                                 )
                    if cl.status != "good" and diff.total_seconds() < 86400:
                        cl.status = "good"
                        cl.save()

                        automatedemails.sendMail(SEND_MAIL_TO, f"{DB_NAME} API recording - sensor online",
                                                 "Countline " + str(cl.name) +
                                                 " has been marked online at " + datetime.datetime.now().strftime(
                                                     "%d/%m/%Y %H:%M:%S") +
                                                 " as it has received recent data",
                                                 )
            except requests.exceptions.RequestException as e:
                print("Requests exception", e)
            except django.db.utils.Error as e:
                print("Database error", e)
            except Observation.DoesNotExist as e:
                print("couldnt find latest entry")

    def get_clusters(self):
        if len(self) != 2:
            raise ValidationError({"Sites": "too many sites selected"})
        if sum([l.temp for l in self]) != 1:
            raise ValidationError(
                {"Sites": "Can only select 1 temp and 1 permanent site to match"})
        for item in self:
            if item.temp:
                temp = item
            else:
                perm = item
        result = []
        for dayIndex in range(1, 4):
            tempClusterObject, _ = Clustering.objects.using(DB_NAME).get_or_create(location=temp, day=dayIndex,
                                                                                   defaults={"value": 1})
            permClusterObject, _ = Clustering.objects.using(DB_NAME).get_or_create(location=perm, day=dayIndex,
                                                                                   defaults={"value": 1})
            isClustered = ClusterMatch.objects.using(DB_NAME).filter(
                temp=temp, perm=perm, day=dayIndex).exists()
            result += [tempClusterObject.value,
                       isClustered, permClusterObject.value]
        return result

    def set_clusters(self, clustering):
        if len(self) != 2:
            raise ValidationError({"Sites": "too many sites selected"})
        if sum([l.temp for l in self]) != 1:
            raise ValidationError(
                {"Sites": "Can only select 1 temp and 1 permanent site to match"})
        for item in self:
            if item.temp:
                temp = item
            else:
                perm = item
        clustering = chunk(clustering, 3)
        for dayIndex, cluster in enumerate(clustering, start=1):
            # print("processing cluster",cluster)
            tempCluster, isClustered, permCluster = cluster
            if not ClusterMatch.objects.using(DB_NAME).filter(temp=temp, perm=perm, day=dayIndex).exists() \
                    and isClustered:
                ClusterMatch.objects.using(DB_NAME).create(
                    temp=temp, perm=perm, day=dayIndex)
                temp.factoringEdited = True
                temp.save()
            if ClusterMatch.objects.using(DB_NAME).filter(temp=temp, perm=perm, day=dayIndex).exists() \
                    and not isClustered:
                ClusterMatch.objects.using(DB_NAME).get(
                    temp=temp, perm=perm, day=dayIndex).delete()
                temp.factoringEdited = True
                temp.save()
            tempClusterObject, _ = Clustering.objects.using(
                DB_NAME).get_or_create(location=temp, day=dayIndex)
            tempClusterObject.value = tempCluster
            tempClusterObject.save()
            permClusterObject, _ = Clustering.objects.using(
                DB_NAME).get_or_create(location=perm, day=dayIndex)
            # print("permcluster object is",permClusterObject.location.name,permClusterObject.day,permClusterObject.value,)
            permClusterObject.value = permCluster
            permClusterObject.save()


class LocationManager(models.Manager):
    def get_queryset(self):
        prefetchClasses = Prefetch(
            'classes',
            queryset=LocationObservationClass.objects.using(
                DB_NAME).order_by("order").select_related("obsClass")
        )

        prefetchDirections = Prefetch(
            'directions',
            queryset=LocationDirection.objects.using(
                DB_NAME).order_by("order").select_related("direction")
        )
        return LocationQuerySet(self.model, using=self._db).prefetch_related(prefetchClasses, prefetchDirections,
                                                                             "associatedLocations",
                                                                             "locationobservationclass_set",
                                                                             "area", "observationType")


class Location(models.Model):
    class StatusChoices(models.IntegerChoices):
        LIVE = 1,
        UNDER_REVIEW = 2,
        NO_LONGER_IN_USE = 3

    id = models.AutoField(primary_key=True)
    # id = models.CharField(max_length=255, primary_key=True)
    geometry = models.BinaryField(blank=True, null=True)
    lat = models.FloatField("Lat", null=True, blank=True)
    lon = models.FloatField("Lon", null=True, blank=True)
    name = models.CharField(max_length=100, blank=True, null=True)
    device = models.IntegerField(blank=True, null=True)
    imgURL = models.FilePathField(
        path=settings.STATIC_ROOT, blank=True, null=True)
    directions = models.ManyToManyField(
        "Direction", through="LocationDirection")
    classes = models.ManyToManyField(
        ObservationClass, through="LocationObservationClass")
    area = models.ForeignKey(
        "Area", on_delete=models.SET_NULL, blank=True, null=True)
    numDays = models.IntegerField(
        "number of days data", blank=True, null=True, default=0)
    validationDate = models.DateField("validationDate", blank=True, null=True)
    lastDataReceived = models.DateTimeField(
        "Last Data Received At", blank=True, null=True)
    lastNonZeroDataReceived = models.DateTimeField("Last Non Zero Data Received At", blank=True, null=True,
                                                   db_column="last_non_zero_data")
    installDate = models.DateField("Install Date", blank=True, null=True)
    startRecievingDate = models.DateField(
        "startRecievingDate", blank=True, null=True)
    observationType = models.ForeignKey(
        ObservationType, blank=True, null=True, on_delete=models.SET_NULL)
    speedLimit = models.IntegerField(
        "Posted Speed Limit", blank=True, null=True)
    speedLimit2 = models.IntegerField(
        "Posted Speed Limit", blank=True, null=True, default=20)
    speedLimit3 = models.IntegerField(
        "Posted Speed Limit", blank=True, null=True, default=20)
    api_identifier = models.IntegerField(
        "Posted Speed Limit", blank=True, null=True)
    status = models.CharField(
        max_length=20, blank=True, null=True, default="Good")
    objects = LocationManager()  # The default manager.
    # 0 = normal countline, 1 = virtual countline, 2 = occupancy zone
    virtual = models.IntegerField(default=0)
    # 0 = normal location, 1 = temporary location
    temp = models.IntegerField(default=0)
    associatedLocations = models.ManyToManyField("Location")
    factoringEdited = models.BooleanField(default=False)
    processingFactoring = models.BooleanField(default=False)

    #
    # because I had to switch from crt old api to new api, it was going to take too long to update the
    # observation table with the new ids for each location, i added a new column to hold the vivacity id
    # data pulled from the vivacity API will look to this column to identify the correct countline
    #
    api_identifier = models.CharField(
        max_length=255, db_column="api_identifier")
    #
    # added in a column to allow admins to add and edit a vivacity sensor id number, which is different to
    # the tracsis id and the api id.
    #
    vivacity_sensor_id = models.CharField(
        max_length=20, db_column="vivacity_sensor_id")

    #
    # added in a column to allow admins to set status of a sensor
    #
    sensorcheck = models.IntegerField(choices=StatusChoices.choices, default=StatusChoices.LIVE,
                                      db_column="sensorcheck_status")
    projects = models.ManyToManyField('Project', through="ProjectLocations")

    class Meta:
        db_table = "location"

    @property
    def aggFunc(self):
        if self.observationType.id == 4:
            return Count
        if self.observationType.id == 1:
            return Sum
        if self.observationType.id == 2:
            return Avg

    @property
    def aggFunc_as_string(self):
        if self.observationType.id == 4:
            return "count"
        if self.observationType.id == 1 or self.observationType.id == 5:
            return "sum"
        if self.observationType.id == 2:
            return "avg"

    @property
    def round_to_places(self):
        #
        # sometimes we want to round aggregated data to a whole number, sometimes we dont, eg for Air Quality Sensors
        # This property indicates whether to round or not
        #
        if self.observationType.id == 2:
            return 3
        return 0

    @property
    def api(self):
        try:
            return self.vivacityapi_set.all()[0]
        except Exception as e:
            return None

    def get_weather_data(self, **params):
        sub = Subquery(WeatherCode.objects.using(DB_NAME).filter(
            id=OuterRef("value")).values("icon")[:1])
        sub2 = Subquery(WeatherCode.objects.using(DB_NAME).filter(
            id=OuterRef("value")).values("description")[:1])
        data = [[["", ""]] * 96 for i in range(7)]
        qs = AssociatedObservation.objects.using(DB_NAME).filter(location=self,
                                                                 date__gte=params["startDate"],
                                                                 date__lte=params["endDate"], obsClass_id=43085)
        qs = qs.annotate(icon=sub, description=sub2).values(
            "date", "icon", "description")
        numPeriods = 4
        for item in qs:
            d = item["date"]
            chunk = d.hour * numPeriods
            for i in range(numPeriods):
                data[d.weekday()][chunk + i] = [item["icon"].replace("n",
                                                                     "d") + ".png", item["description"]]
        return data

    def update_weather(self, d):
        #
        # get data for a day from the open weather API oneCall, can only look 5 days in the past.
        #
        classes = ObservationClass.objects.using(DB_NAME).filter(
            id__in=[43075, 43077, 43078, 43079, 43080, 43081, 43082, 43083, 43084, 43085])
        classes = {cl.name: cl for cl in classes}
        timezone.activate("UTC")
        result = tracsis_api_helpers.get_weather_data(
            self.lat, self.lon, d, settings.OPEN_WEATHER_API_KEY)
        df = pd.DataFrame.from_records(result["hourly"])
        df["dt"] = df["dt"].apply(lambda x: datetime.datetime.fromtimestamp(x))
        df.rename(columns={"temp": "Temp"}, inplace=True)
        df = df.where(pd.notnull(df), None)
        data = []
        for _, row in df.iterrows():
            print(row)
            date = timezone.make_aware(row["dt"])
            for field in ["Temp", "feels_like", "pressure", "humidity", "dew_point", "clouds", "visibility",
                          "wind_speed", "wind_deg"]:
                obsClass = classes[field]
                data.append(AssociatedObservation(location=self,
                            date=date, obsClass=obsClass, value=row[field]))
            for item in row["weather"][:1]:
                print("processsing item", item)
                data.append(
                    AssociatedObservation(location=self, date=date, obsClass=classes["weather"], value=item["id"]))
                if not WeatherCode.objects.using(DB_NAME).filter(id=item["id"]).exists():
                    print("creating item", item)
                    WeatherCode.objects.using(DB_NAME).create(**item)
        AssociatedObservation.objects.using(
            DB_NAME).bulk_create(data, ignore_conflicts=True)

    def fill_monthly_totals(self, d):
        # fill monthly totals table with sum of all values for location in month indicated by d
        #
        timezone.activate("UTC")
        d = d.replace(hour=0, minute=0, second=0, microsecond=0)
        startDate = timezone.make_aware(d.replace(day=1))
        endDate = timezone.make_aware(
            (d + datetime.timedelta(days=31)).replace(day=1))
        print(startDate, endDate)
        value = Observation.objects.using(DB_NAME).filter(
            location=self, date__gte=startDate, date__lt=endDate)
        value = value.values("location_id").annotate(total=Sum("value"))
        print("value is", value.query)
        print("values is", value.values_list("total", flat=True))
        try:
            val = value.values_list("total", flat=True)[0]
        except Exception as e:
            val = 0
        obj, _ = DailyTotals.objects.using(DB_NAME).get_or_create(
            location=self, date=startDate, value=val)
        obj.value = val
        obj.save()
        pass

    def get_daily_data_point_counts(self, year):
        index = pd.date_range(start='1/1/' + str(year),
                              end='31/12/' + str(year))
        allData = DailyClassedTotals.objects.using(
            DB_NAME).filter(location=self.id)
        allData = list(allData.values("date").annotate(
            count=Sum("value")).values_list("date", "count"))
        vals = [v[1] for v in allData]
        std = np.std(vals)
        avg = np.mean(vals)
        print("stats is", std, avg)
        data = DailyClassedTotals.objects.using(
            DB_NAME).filter(location=self.id, date__year=year)
        data = list(data.values("date").annotate(
            count=Sum("value")).values_list("date", "count"))
        if len(data):
            m = max(data, key=lambda x: x[1])[1]

        else:
            m = 0
        print("m average is", m)
        df = pd.DataFrame(data, columns=["date", "count"])
        df["date"] = pd.to_datetime(df["date"], format='%Y-%m-%d')
        df["date"] = df["date"].dt.date
        df.set_index("date", inplace=True)
        df = df.reindex(index, columns=["count"], fill_value=0).reset_index()
        data = [list(l) for l in df.values.tolist()]

        for item in data:
            zscore = (item[1] - avg) / std
            zscoreminus = 0 - zscore
            prob = 1 - abs(quad(normalProbabilityDensity, np.NINF, zscore)[0] -
                           quad(normalProbabilityDensity, np.NINF, zscoreminus)[0])

            item.append(prob)
        df = pd.DataFrame(data)
        # df.to_excel("percentile calcs.xlsx")
        return {"data": data, "max": m}

    def get_daily_data_point_counts_hourly(self, date):
        pass

    def as_dashboard_graph_selectors(self):
        html = ""
        for index, d in enumerate(self.ordered_class_list()):
            html += "<label class='class-selector' data-bg = '" + \
                classColors[index] + "' "
            html += "data-index='" + str(index) + "' style='border-color:" + classColors[index] + "'>" + str(
                d.obsClass.displayName) + "</label>"
        return html

    def ordered_direction_queryset(self):
        direction = [
            {
                "id": 1,
                "descriptive": "Inbound"
            },
            {
                "id": 2,
                "descriptive": "Outbound"
            },
            {
                "id": 3,
                "descriptive": "Combined"
            }
        ]

        html = "<ul>"
        selected = ""
        for i in range(len(direction)):
            if self.observationType.id == 9 or self.observationType.id == 1 or self.observationType.id == 10 or self.observationType.id == 12:
                if i == len(direction) - 1:
                    selected = "selected"
            html += "<li class ='menu-item' id='direction_" + \
                str(direction[i]["id"]) + "'>"
            html += "<a href='#' class ='selectable-menu-item " + selected + \
                "' > <span> " + \
                    direction[i]["descriptive"] + "</span></a></li>"

        # if self.observationType.id == 1:
        #     html += "<li class ='menu-item' id='direction_combined" + "'>"
        #     html += "<a href='#' class ='selectable-menu-item selected' > <span> Combined </span></a></li>"
        # html += "</ul>"
        return html

    def ordered_location_direction_queryset(self):
        return LocationDirection.objects.using(DB_NAME).filter(location=self).order_by("order")

    def ordered_class_queryset(self):
        return ObservationClass.objects.using(DB_NAME).filter(locationobservationclass__location=self).order_by("locationobservationclass__order")
        return LocationObservationClass.objects.using(DB_NAME).filter(location=self).order_by("order")

    def ordered_direction_dictionary(self):
        result = []
        dirs = self.ordered_location_direction_queryset().values_list("direction__name", "direction__descriptive",
                                                                      "order")
        for dir in dirs:
            result.append(
                {"name": dir[0], "descriptive": dir[1], "order": dir[2]})
        return result

    def directions_as_geojson(self):
        ld = LocationDirection.objects.using(
            DB_NAME).filter(location=self).order_by("order")
        # print("direction objects are",ld.values())
        features = []
        for p in ld:
            geom = p.as_geojson_linestring()
            features.append(geojson.Feature(geometry=geom, properties={"order": p.order, "direction": p.direction.name,
                                                                       "direction_id": p.direction.id,
                                                                       "location_id": self.id, "type": "direction"}))
        return features

    def create_directions_from_geojson(self, directions):
        print("processing directions", directions)
        dirs = []
        for d in json.loads(directions):
            try:
                direction_id = int(d["properties"]["direction"])
            except ValueError as e:
                raise django.core.exceptions.ValidationError(
                    {"Direction": "selected direction is not valid"})
            try:
                order = int(d["properties"]["order"])
            except ValueError as e:
                raise django.core.exceptions.ValidationError(
                    {"order": "order must be an integer"})
            line = d["geometry"]
            dirObject = Direction.objects.using(DB_NAME).get(id=direction_id)
            dirs.append(LocationDirection(location=self,
                        direction=dirObject, order=order, line=line))
        return dirs

    def as_geojson_feature(self, client=None):
        feature = None
        properties = LocationSerializer(self, context={"client": client}).data
        properties["type"] = "countline" if not self.virtual else "virtual"
        if self.geometry is not None:
            geom = wkt_to_geojson(base64.decodebytes(self.geometry).decode())
        else:
            geom = geojson.Point(coordinates=[self.lon, self.lat])
        feature = geojson.Feature(geometry=geom, properties=properties)
        return feature

    @classmethod
    def create(self, **obj_data):
        if "id" not in obj_data:
            raise django.core.exceptions.ValidationError(
                {"id": "missing unique id field"})
        if obj_data["id"] is None or obj_data["id"] == "":
            raise django.core.exceptions.ValidationError(
                {"id": "unique ID cannot be blank"})
        try:
            Location.objects.using(DB_NAME).get(id=obj_data["id"])
        except Location.DoesNotExist as e:
            return Location(id=obj_data["id"])
        raise django.db.IntegrityError

    def update(self, data, files=None):
        print("update data is", data)
        try:
            # assert data["area"] != ""
            area, _ = Area.objects.using(
                DB_NAME).get_or_create(name=data["area"])
            self.area = area
        except Exception as e:
            print(e)
            raise django.core.exceptions.ValidationError(
                {"Area": "couldnt find or create area"})

        try:
            print("obstype from data is", int(data["observationType"]))
            obsType = ObservationType.objects.using(
                DB_NAME).get(id=int(data["observationType"]))
            # self.observationType = obsType
        except Exception as e:
            print(e)
            # raise django.core.exceptions.ValidationError({"Observation Type": "couldnt find Observation Type"})

        fields = [f.name for f in Location._meta.get_fields() if
                  f.name not in ["directions", "area", "imgURL", "observationType", "geometry"]]
        for f in fields:
            print("checking field", f)
            if f in data:
                val = data[f]
                if val == "":
                    val = None
                print("setting", f, val)
                setattr(self, f, val)
        self.full_clean()
        if files and "imgURL" in files:
            file_obj = files["imgURL"]
            fileLoc = f"/static/{BASE_URL}/countlines/" + file_obj.name
            with open(settings.BASE_DIR + fileLoc, 'wb+') as destination:
                for chunk in file_obj.chunks():
                    destination.write(chunk)
            self.imgURL = fileLoc
        if False:
            if "directions" in data:
                dirs = self.create_directions_from_geojson(data["directions"])
            else:
                dirs = []

            order = sorted([ld.order for ld in dirs])
            maxOrder = order[-1] if len(order) > 0 else -1
            print("max order is", order, maxOrder)
            if len(order) != maxOrder + 1:
                raise django.core.exceptions.ValidationError(
                    {"direction order": "the order of directions must be a sequence from 0 to " + str(len(order) - 1)})

        try:
            marker = json.loads(data["marker"])
            print("marker is", marker)
            self.lon, self.lat = marker["geometry"]["coordinates"]
        except Exception as e:
            print("error", e)
            raise django.core.exceptions.ValidationError(
                {"lat/lon": "Couldnt convert marker to a valid lat/lon"})
        self.save()
        if False:
            self.directions.clear()
            for dir in dirs:
                dir.save()

    def save_classes(self, classes):
        cleanedClasses = []
        for cl in classes:
            try:
                cleanedClasses.append(
                    ObservationClass.objects.using(DB_NAME).get(id=int(cl)))
            except Exception as e:
                print("error,", e)
                raise django.core.exceptions.ValidationError(
                    {"Observation Class": "Class does not exist in database"})
        LocationObservationClass.objects.using(
            DB_NAME).filter(location=self).delete()
        for index, cl in enumerate(cleanedClasses):
            LocationObservationClass.objects.using(DB_NAME).create(
                location=self, obsClass=cl, order=index)

    def import_data_from_file(self, file, startDate):
        if self.observationType.id == 4:
            try:
                self.import_ATC_data_from_excel(startDate, file)
            except FileNotFoundError as e:
                print("file not found", e)
            except xlrd.biffh.XLRDError as e:
                print("couldnt find sheet", e)
        else:
            pass

    def import_speed_data_from_file(self, file, startDate):
        d = datetime.datetime.strptime(startDate, "%d/%m/%Y")
        startRow = 11
        numRows = 24
        result = []
        cols = [1] + list(range(3, 23)) + list(range(34, 54))
        for day in range(7):
            df = pd.read_excel(file, sheet_name="Speed Data - Values", skiprows=startRow,
                               usecols=cols, nrows=numRows, header=None)
            df["day"] = day
            startRow += 30
            result.append(df)
        df = pd.concat(result)
        df.to_excel("speeds.xlsx")
        #

        if list(df.columns) != [r for r in range(39)] + ["day"]:
            print("wrong sheet, or incorrectly formatted data")
            # return
        df["Date"] = df.apply(lambda x: pytz.timezone("Europe/London").localize(
            pd.datetime.combine(d + datetime.timedelta(days=x["day"]), x[0])).astimezone(pytz.utc), axis=1)

        directions = self.ordered_direction_list()
        classes = ObservationClass.get_speed_classes_as_list()
        print(classes)
        data = []
        for index, row in df.iterrows():
            print("looking at row", row)
            for r in range(1, (len(df.columns) - 1) // 2):
                data.append(
                    Observation(date=row["Date"], value=int(row[r]), direction=directions[0], obsClass=classes[r - 1],
                                location=self))
                data.append(Observation(date=row["Date"], value=int(row[r + 20]), direction=directions[1],
                                        obsClass=classes[r - 1], location=self))
        # Observation.objects.using(DB_NAME).bulk_create(data)
        for d in data:
            print(d.date, d.direction, d.obsClass.displayName, d.value)

    def import_ATC_data_from_excel(self, startDate, file, numclasses=12):
        d = datetime.datetime.strptime(startDate, "%Y-%m-%d")
        startRow = 20
        numRows = 96
        result = []
        for day in range(7):
            df = pd.read_excel(file, sheet_name="Classed Volumes 15min - Values ", skiprows=startRow,
                               usecols=[1, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 17, 18, 19, 20, 21, 22, 23, 24, 25,
                                        26, 27, 28], nrows=numRows, header=None)
            df["day"] = day
            startRow += 102
            result.append(df)
        df = pd.concat(result)
        if list(df.columns) != [r for r in range(25)] + ["day"]:
            print("wrong sheet, or incorrectly formatted data")
            return
        df["Date"] = df.apply(lambda x: pytz.timezone("Europe/London").localize(
            pd.datetime.combine(d + datetime.timedelta(days=x["day"]), x[0])).astimezone(pytz.utc), axis=1)
        # df.to_excel("atc output.xlsx")
        data = []
        directions = self.ordered_direction_list()
        print("num directions", len(directions))
        classes = self.ordered_class_list()
        print("num classes", len(classes))
        for index, row in df.iterrows():
            for r in range(1, (len(df.columns) - 1) // 2):
                data.append(
                    Observation(date=row["Date"], value=int(row[r]), direction=directions[0], obsClass=classes[r - 1],
                                location=self))
                data.append(Observation(date=row["Date"], value=int(row[r + 12]), direction=directions[1],
                                        obsClass=classes[r - 1], location=self))
        Observation.objects.using(DB_NAME).bulk_create(data)

    def import_ATC_data_from_raw_metrocount_text_file(self, file, numclasses=12):
        data = []
        start = False
        with open(file, 'r') as f1:
            lines = f1.readlines()

            for l in lines:
                line = [e for e in l.split(" ") if e != ""]
                print("line is", line)
                if start and len(line) > 13:
                    data.append([line[3], line[4], line[5],
                                line[6], line[8], line[9], line[13]])
                if len(line) > 1 and line[0] == "DS":
                    start = True

        df = pd.DataFrame(data)
        df.columns = ["Date", "Time", "Direction",
                      "Speed", "Head", "Gap", "Class"]
        df["Date"] = df.apply(lambda r: pd.to_datetime(
            r['Date'] + " " + r['Time']), 1)
        df["Date"] = df.apply(lambda x: pytz.timezone(
            "Europe/London").localize(x["Date"]).astimezone(pytz.utc), axis=1)
        df["Direction"] = df.apply(lambda r: int(r["Direction"][-1]), 1)
        df["Class"] = df["Class"].astype(int)
        df["Speed"] = df["Speed"].astype(float)
        df["Head"] = df["Head"].astype(float)
        df["Gap"] = df["Gap"].astype(float)
        print(len(df))
        df = df[(df["Head"] > 0) & (df["Gap"] > 0)]
        # print("after dropping, df is", len(df))  #
        df = df.drop_duplicates(["Date", "Class", "Direction"])
        data = []
        classes = self.ordered_class_list()
        directions = self.ordered_direction_list()
        for index, row in df.iterrows():
            data.append(Observation(date=row["Date"], value=row["Speed"], direction=directions[row["Direction"]],
                                    obsClass=classes[row["Class"] - 1], location=self))
        Observation.objects.using(DB_NAME).bulk_create(data)

    def get_speed_data(self):
        directions = list(Direction.objects.using(DB_NAME).filter(locationdirection__location=self)
                          .values("name", "descriptive").order_by("locationdirection__order"))
        classes = ObservationClass.objects.using(DB_NAME).filter(locationobservationclass__location=self).order_by(
            "locationobservationclass__order")
        directions.append({"name": "Combined", "descriptive": "Combined"})

        qs = Observation.objects.using(DB_NAME).filter(location=self, status=0).values_list("location_id",
                                                                                            "direction__order",
                                                                                            "obsClass__order", "value",
                                                                                            "date")
        df = pd.DataFrame(list(qs), columns=[
                          "location", "directionorder", "classorder", "value", "date"])
        df.set_index("date", inplace=True)
        df = df[df["location"] == self.id]
        bins = [0, 10, 15, 20, 25, 30, 35, 40, 45, 50,
                55, 60, 65, 70, 75, 80, 85, 90, 95, 100, 1000]
        binLabels = [index for index in range(0, len(bins) - 1)]
        d = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        xAxisLabels = [(d + datetime.timedelta(minutes=60 * i)
                        ).strftime("%H:%M") for i in range(25)]
        df["bin"] = pd.cut(df["value"], bins=bins, labels=binLabels)

        result = df.groupby(["location", "classorder", "directionorder", "bin"]).resample(
            "60T").agg({"bin": "count"})
        result.rename(columns={"bin": "value"}, inplace=True)
        result.reset_index(inplace=True)
        # result.rename(columns={"bin": "classorder"}, inplace=True)
        result.set_index("date", inplace=True)
        # result.to_csv("test.csv")
        for index, direction in enumerate(directions):
            lineCharts = []
            for day in range(7):
                dayCharts = []
                for binIndex in range(len(binLabels)):
                    binCharts = []
                    data = [[0 for i in range(25)]
                            for b in range(len(self.classes.all()))]
                    dayDf = result[(result.index.weekday == day) & (result["directionorder"] == index) & (
                        result["bin"] == binIndex)]
                    for _, row in dayDf.iterrows():
                        hour = row.name.hour
                        data[row["classorder"]][hour] = row["value"]
                    dayCharts.append(
                        create_line_chart([cl.obsClass.name for cl in self.classes.all()], xAxisLabels, data))
                lineCharts.append(dayCharts)
            direction["speedCharts"] = lineCharts
        return directions

    def get_speed_overview(self):
        output = []
        qs = Observation.objects.using(DB_NAME).filter(location=self).values_list("location_id", "direction__order",
                                                                                  "obsClass__order", "value", "date")
        df = pd.DataFrame(list(qs), columns=[
                          "location", "directionorder", "classorder", "value", "date"])
        df.set_index("date", inplace=True)
        # print(df)
        numDirections = self.directions.count()
        output.append(get_average_speed_by_direction(
            df[df.index.weekday < 5], numDirections))
        output.append(get_average_speed_by_direction(df, numDirections))
        output.append(get_xth_percentile_by_direction(
            df[df.index.weekday < 5], 0.85, numDirections))
        output.append(get_xth_percentile_by_direction(df, 0.85, numDirections))
        output.append(get_xth_percentile_by_direction(
            df[df.index.weekday < 5], 0.95, numDirections))
        output.append(get_xth_percentile_by_direction(df, 0.95, numDirections))
        output.append(
            get_percent_over_speed_limit_by_direction(df[df.index.weekday < 5], self.speedLimit, numDirections))
        output.append(get_percent_over_speed_limit_by_direction(
            df, 30, numDirections))
        output.append(get_percent_over_speed_limit_by_direction(df[df.index.weekday < 5],
                                                                self.speedLimit +
                                                                (self.speedLimit * 0.1) + 2,
                                                                numDirections))
        output.append(get_percent_over_speed_limit_by_direction(
            df, 35, numDirections))
        output.append(
            get_percent_over_speed_limit_by_direction(df[df.index.weekday < 5], self.speedLimit + 15, numDirections))
        output.append(get_percent_over_speed_limit_by_direction(
            df, 45, numDirections))
        # print(output)
        return output

    def get_atc_overview(self):
        classes = ObservationClass.objects.using(DB_NAME).filter(locationobservationclass__location=self) \
            .order_by("locationobservationclass__order")
        classLabels = [cl.displayName for cl in classes]
        directions = list(Direction.objects.using(DB_NAME).filter(locationdirection__location=self)
                          .values("name", "descriptive").order_by("locationdirection__order"))
        donutCharts = []
        classSelectors = classes.as_dashboard_class_list()
        ###
        # Total Volumes pie charts
        ###
        kwargs = {"period": "D", "startDate": self.observation_set.earliest("date").date,
                  "endDate": self.observation_set.latest("date").date}
        loc = Location.objects.using(DB_NAME).filter(id="dfhhjdj")
        df = loc.get_totals(**kwargs)
        # print(df)
        totalVols = df.groupby(
            ["location", "classorder", "directionorder"], as_index=False).sum()
        totalVols["day"] = 0
        av5day = df[df["day"].dt.weekday < 5].groupby(["location", "classorder", "directionorder"],
                                                      as_index=False).mean()
        av5day["day"] = 7
        av5day["value"] = av5day["value"].round(0)

        av7day = df.groupby(
            ["location", "classorder", "directionorder"], as_index=False).mean()

        av7day["day"] = 8
        av7day["value"] = av7day["value"].round(0)

        # print(av5day)
        df = pd.concat([totalVols, av5day, av7day])
        # print(df)
        # Av7day = df.groupby(["location", "classorder", "directionorder"]).mean()
        # Av7day["day"] = 8
        charts = loc.build_chart_structure(df)

        speedData = self.get_speed_overview()

        return {"selectors": classSelectors, "donuts": charts, "directions": directions, "speedData": speedData,
                "breadcrumbs": "/ATCs/" + self.project_set.all()[0].id + " " + self.project_set.all()[0].name + "/ ",
                "siteName": str(self.name), "speedLimit": self.speedLimit}

        print("getting 15 min averages", datetime.datetime.now())

        df = Location.objects.using(DB_NAME).filter(
            id=self.id).get_daily_15_min_averages("", "")
        avg5day = df[df["day"] < 5].groupby(["location", "directionorder", "classorder", "time"], as_index=False).agg(
            {"value": "mean"})
        avg7day = df.groupby(["location", "directionorder", "classorder", "time"], as_index=False).agg(
            {"value": "mean"})

        for index, dir in enumerate(directions):
            data = df_to_hourly_classed_totals(
                avg5day[(avg5day["directionorder"] == index)], len(classLabels))
            result = [sum(d) for d in data]
            donutCharts.append(create_donut_chart(
                classLabels, dir["descriptive"], result))

        for index, dir in enumerate(directions):
            data = df_to_hourly_classed_totals(
                avg7day[(avg7day["directionorder"] == index)], len(classLabels))
            result = [sum(d) for d in data]
            donutCharts.append(create_donut_chart(
                classLabels, dir["descriptive"], result))

        print("getting speed data", datetime.datetime.now())
        speedData = self.get_speed_overview()
        print("finished", datetime.datetime.now())
        return {"selectors": classSelectors, "donuts": charts, "directions": directions, "speedData": speedData,
                "breadcrumbs": "/ATCs/" + self.project_set.all()[0].id + " " + self.project_set.all()[0].name + "/ ",
                "siteName": str(self.name), "speedLimit": self.speedLimit}

    def get_tracks(self, startDate, endDate, timezone="Europe/London"):
        sqlString = "select vehicleId, DATE(CONVERT_TZ(firstseen,'UTC','" + timezone + "')) start, " \
                                                                                       "DATE(CONVERT_TZ(lastseen,'UTC','" + timezone + "')) end ,AsText(path) path " \
                                                                                                                                       f"from {DB_NAME}_tracks"
        # print(sqlString)
        features = []

        with connections[DB_NAME].cursor() as cursor:
            cursor.execute(sqlString)
            result = cursor.fetchall()
            for item in result:
                # print(item)
                feature = geojson.Feature(geometry=wkt_to_geojson(
                    item[3]), properties={"vehicle": item[0]})
                features.append(geojson.Feature(geometry=wkt_to_geojson(
                    item[3]), properties={"vehicle": item[0]}))
        return geojson.FeatureCollection(features)

    def add_cluster_value(self, value):
        cluster = Clustering.objects.using(
            DB_NAME).get_or_create(location=self)
        cluster.value = int(value)
        cluster.save()

    def fill_with_blank_data(self, startDate, endDate):
        while startDate < endDate:
            self.create_blank_data(startDate)
            startDate += datetime.timedelta(minutes=15)

    def create_blank_data(self, date):
        # print("creating blank data for",self.name,date)
        data = []
        for cl in self.classes.all():
            for d in self.directions.all():
                o = Observation(location=self, direction=d,
                                obsClass=cl, date=date, status=1, value=0)
                data.append(o)
        # print("data for",self.name," is",data)
        Observation.objects.using(DB_NAME).bulk_create(
            data, ignore_conflicts=True)

    def get_raw_data_as_df(self, startDate, endDate, status=1):
        vals = Observation.objects.using(DB_NAME).filter(location=self, status=status, date__gte=startDate,
                                                         date__lte=endDate)
        vals = vals.values_list("location", "date", "obsClass__order", "direction__order",
                                "direction__direction__id", "value")
        originalValuesDf = pd.DataFrame(list(vals),
                                        columns=["location", "day", "classorder", "directionorder", "direction_id",
                                                 "value"])
        # print(originalValuesDf)
        try:
            originalValuesDf["weekday"] = originalValuesDf["day"].dt.weekday
            originalValuesDf["time"] = originalValuesDf["day"].dt.time
            originalValuesDf["seg"] = 0
        except Exception as e:
            #
            # empty dataframe, so pass
            originalValuesDf["weekday"] = None
            originalValuesDf["time"] = None
            originalValuesDf["seg"] = None
        return originalValuesDf

    def fill_values_with_factored_data_from_df(self, startDate, endDate, df):
        print("filling values for", startDate, endDate)
        newValues = Observation.objects.using(DB_NAME).filter(location=self, status=1, date__gte=startDate,
                                                              date__lt=endDate).select_related("obsClass", "direction")
        print("num values for date range is", newValues.count())
        for item in newValues:
            # print(item.id,item.date,item.date.time(),item.date.weekday(),item.obsClass.order,item.direction.order,item.value)
            mask = (df["weekday"] == item.date.weekday()) & \
                   (df["classorder"] == item.obsClass.order) & \
                   (df["time"] == item.date.time()) & \
                   (df["directionorder"] == item.direction.order)
            try:
                item.value = df.loc[mask]["newValue"].values[0]
            except Exception as e:
                #
                # the matching value didnt exist in the df, so do set the value to 0
                item.value = 0
        Observation.objects.using(DB_NAME).bulk_update(
            newValues, ["value"], batch_size=3000)

    def apply_factoring(self, **kwargs):
        # print("in factoring, kwargs are",kwargs)
        timezone.activate("UTC")
        permLocs = Location.objects.using(DB_NAME).filter(
            id__in=self.temp_site.all().values_list("perm"))
        permdict = ClusterMatch.objects.using(
            DB_NAME).filter(temp=self).get_perm_days_dict()
        if len(permLocs) == 0:
            return
        surveyStartDate = Observation.objects.using(DB_NAME).filter(
            location=self, status=0).earliest("date").date
        surveyEndDate = Observation.objects.using(DB_NAME).filter(
            location=self, status=0).latest("date").date
        # print("survey dates are",surveyStartDate,surveyEndDate)
        ###
        # set up the dataframe with raw data from the original survey period in the temp site
        ###
        originalValuesDf = self.get_raw_data_as_df(
            surveyStartDate, surveyEndDate, status=0)
        # print("original values are",originalValuesDf)
        #
        # average any extra days, eg if there are 2 mondays in the survey, this will average them
        #
        originalValuesDf = originalValuesDf.groupby(["location", "weekday", "time",
                                                     "classorder", "directionorder"], as_index=False).mean()
        originalValuesDf["ratio"] = 0.0
        originalValuesDf["newValue"] = 0.0
        # originalValuesDf.to_csv("original values.csv")

        ###
        # get the average daily totals for the perm sites over the original survey date
        ###
        try:
            permValuesDf = permLocs.get_totals(period="D", startDate=surveyStartDate - datetime.timedelta(days=14),
                                               endDate=surveyEndDate + datetime.timedelta(days=14))
        except Exception as e:
            #
            # no data for the temp survey period, or something went wrong, so finish
            #
            return
        if len(permValuesDf) == 0:
            return
        permValuesDf["day"] = permValuesDf["day"].dt.weekday
        permValuesDf = permValuesDf.groupby(
            ["location", "day", "classorder", "directionorder"], as_index=False).mean()
        permValuesDf = permValuesDf.loc[permValuesDf["directionorder"] != 2]
        permValuesDf["newTotal"] = 0

        ###
        # indicate whether the clustermatch applies for each particular piece of data
        ###
        def calculate_applies(row):
            return row["day"] in permdict[row["location"]]

        permValuesDf["applies"] = permValuesDf.apply(calculate_applies, axis=1)
        # permValuesDf.to_csv("perm values.csv")

        s = kwargs["applyStart"]
        e = kwargs["applyEnd"]
        while s < e:
            startOfNextMonth = timezone.make_aware(datetime.datetime(
                s.year + (s.month // 12), ((s.month % 12) + 1), 1))
            print("processing", s, "to", startOfNextMonth)
            ###
            # get the average daily totals for the perm sites over the time period we are interested in factoring
            ###

            df = permLocs.get_totals(
                period="D", startDate=s, endDate=startOfNextMonth)
            if len(df) != 0:

                df["day"] = df["day"].dt.weekday
                # df.to_csv("before.csv")
                df = df.groupby(["location", "day", "classorder",
                                "directionorder"], as_index=False).mean()
                # df.to_csv("monthly data for perm sites.csv")

                # add the totals for the period of interest to the dataframe for the perm sites original survey period
                # then calculate the ratios of original period to period of interest

                for index, row in permValuesDf.iterrows():
                    mask = (df["location"] == row["location"]) & (df["day"] == row["day"]) & (
                        df["classorder"] == row["classorder"]) & \
                        (df["directionorder"] == row["directionorder"])
                    try:
                        permValuesDf.at[index,
                                        "newTotal"] = df.loc[mask]["value"]
                    except Exception:
                        #
                        # the mask location didnt exist in the dataframe, likely because its too early in the month
                        #
                        pass

                permValuesDf["ratio"] = permValuesDf["newTotal"] / \
                    permValuesDf["value"]
                # permValuesDf.to_csv("perm values with ratio.csv")

                # get the average of the ratios across all perm sites, and fill in the temp site data for each class , direction and day
                ##
                # print("num original values",len(originalValuesDf))
                for index, row in originalValuesDf.iterrows():
                    mask = (permValuesDf["day"] == row["weekday"]) & (permValuesDf["classorder"] == row["classorder"]) & \
                           (permValuesDf["directionorder"]
                            == row["directionorder"])

                    # print("full mean is",permValuesDf.loc[mask]["ratio"].mean())
                    # print("mean with applies",permValuesDf.loc[mask & (permValuesDf["applies"])]["ratio"].mean())
                    originalValuesDf.at[index, "ratio"] = permValuesDf.loc[mask & (permValuesDf["applies"])][
                        "ratio"].mean()

                #
                # calculate the new factored values
                #

                originalValuesDf["newValue"] = originalValuesDf["value"] * \
                    originalValuesDf["ratio"]
                originalValuesDf = originalValuesDf.replace(
                    [np.inf, -np.inf], np.nan)
                originalValuesDf["newValue"] = originalValuesDf["newValue"].round(
                    0).fillna(0)

                # originalValuesDf.to_csv("final factored data.csv")

                #
                # retrieve the data objects for the time period of interest, put in the new factored value for each data point
                # and then save
                #
                newValues = Observation.objects.using(DB_NAME).filter(location=self, status=1, date__gte=s,
                                                                      date__lt=startOfNextMonth)
                if newValues.count() == 0:
                    self.fill_with_blank_data(s, startOfNextMonth)
                newValues = newValues.select_related("obsClass", "direction")
                for item in newValues:
                    # print(item.id,item.date,item.date.time(),item.date.weekday(),item.obsClass.order,item.direction.order,item.value)
                    mask = (originalValuesDf["weekday"] == item.date.weekday()) & \
                           (originalValuesDf["classorder"] == item.obsClass.order) & \
                           (originalValuesDf["time"] == item.date.time()) & \
                           (originalValuesDf["directionorder"]
                            == item.direction.order)
                    try:
                        item.value = originalValuesDf.loc[mask]["newValue"].values[0]
                    except Exception:
                        # print("couldnt find item for mask")
                        pass
                Observation.objects.using(DB_NAME).bulk_update(
                    newValues, ["value"], batch_size=3000)
            s = startOfNextMonth


class LocationSerializerForAPI(serializers.ModelSerializer):
    area = serializers.CharField(source='area.name')
    location = serializers.SerializerMethodField()
    countlineId = serializers.CharField(source='id')

    class Meta:
        model = Location
        fields = ['countlineId', 'name', "area", "location"]

    def get_location(self, obj):
        return {"lat": obj.lat, "lon": obj.lon}


class LocationSerializer(serializers.ModelSerializer):
    obsType = serializers.SerializerMethodField()
    area = serializers.SerializerMethodField()
    active = serializers.SerializerMethodField()
    imgURL = serializers.SerializerMethodField()

    class Meta:
        model = Location
        fields = ["id", "name", "imgURL", "area", "lastDataReceived", "installDate", "obsType", "active", "status",
                  "temp"]

    def get_imgURL(self, obj):
        return obj.imgURL if obj.imgURL is not None else f"/static/{BASE_URL}/blank site image.jpg"

    def get_area(self, obj):
        return obj.area.name if obj.area is not None else ""

    def get_obsType(self, obj):
        return ObservationTypeSerializer(instance=obj.observationType).data

    def get_active(self, obj):
        return True
        if self.context.get("client") is None:
            return True
        clients = obj.client_set.filter(id=self.context.get("client").id)
        print("clients for", obj.name, "are", clients)
        if len(clients) == 0:
            return False
        return True
        # return  "test"


##################################################################
#
#
# Observation
#
#
######################################################################


class ObservationQuerySet(models.QuerySet):

    def get_classed_totals(self):
        qs = self.values("location", "obsClass__id").annotate(
            value=Count("id"))
        return qs

    def convert_dates(self):
        print("converting dates", type(self))
        result = []
        for item in self:
            # print("type of ite is",type(item),type(item) == dict)
            if type(item) == dict:
                item["date"] = timezone.localtime(item["date"])
                item["seg"] = (item["date"].hour * 12) + \
                    (item["date"].minute // 5)
                item["day"] = item["date"].isoweekday()
                # print("ite is now",item)
            if type(item) == Observation:
                item.date = timezone.localtime(item.date)
                item.seg = (item.date.hour * 12) + (item.date.minute // 5)
                item.day = item.date.isoweekday()
                print("date is now", item.date)
            result.append(item)

    def as_daily_hourly_occupancy_datasets(self, classes, average=False):
        df = self.as_dataframe(average)
        directions = []
        df = df[df["directionorder"] < 2]
        hourly = df.groupby(["day", "classorder", "directionorder",
                            "hour"], as_index=False).agg({"value": "sum"})
        # hourly.to_excel("basic hourly.xlsx")
        hourly["occupancy"] = hourly.groupby(
            ["day", "classorder", "directionorder"], as_index=False)["value"].cumsum()
        # hourly.to_excel("hourly with cumsum.xlsx")
        outdf = hourly[hourly["directionorder"] == 0]
        # outdf.to_excel("outdf.xlsx")
        indf = hourly[hourly["directionorder"] == 1]
        # indf.to_excel("indf.xlsx")
        result = indf.merge(outdf, on=["day", "classorder", "hour"])
        result["value"] = result["occupancy_x"] - result["occupancy_y"]
        # result.to_excel("merged.xlsx")
        directionOrder = df["directionorder"].sort_values().unique()
        for index, dirIndex in enumerate(directionOrder):
            direction = {"order": int(dirIndex), "baseData": []}
            for day in range(7):
                dataset = []
                data = df_to_hourly_classed_totals(df[(df["directionorder"] == int(dirIndex)) & (df["day"] == day)],
                                                   len(classes))
                for classIndex, item in enumerate(data):
                    dataset.append(
                        {"label": classes[classIndex].name, "data": item, "borderColor": classColors[classIndex],
                         "fill": False, "pointRadius": 0, "borderWidth": 1, "backgroundColor": classColors[classIndex]})
                direction["baseData"].append(dataset)
            directions.append(direction)
        direction = {"order": 2, "baseData": []}
        for day in range(7):
            dataset = []
            data = df_to_hourly_classed_totals(
                result[(result["day"] == day)], len(classes))
            print("data for day", day, "is", data)
            for classIndex, item in enumerate(data):
                dataset.append({"label": classes[classIndex].name, "data": item, "borderColor": classColors[classIndex],
                                "fill": False, "pointRadius": 0, "borderWidth": 1,
                                "backgroundColor": classColors[classIndex]})
            direction["baseData"].append(dataset)
        directions.append(direction)
        return directions

    def as_daily_hourly_classed_chart_datasets(self, classes, directions, average=False):
        df = self.as_dataframe(average)
        directions = []
        directionOrder = df["directionorder"].sort_values().unique()
        for index, dirIndex in enumerate(directionOrder):
            direction = {"order": int(dirIndex), "baseData": []}
            for day in range(7):
                dataset = []
                data = df_to_hourly_classed_totals(df[(df["directionorder"] == int(dirIndex)) & (df["day"] == day)],
                                                   len(classes))
                for classIndex, item in enumerate(data):
                    dataset.append(
                        {"label": classes[classIndex].name, "data": item, "borderColor": classColors[classIndex],
                         "fill": False, "pointRadius": 0, "borderWidth": 1, "backgroundColor": classColors[classIndex]})
                direction["baseData"].append(dataset)
            avg5day = df[(df["day"] < 5) & (df["directionorder"] == int(dirIndex))].groupby(["classorder", "hour"],
                                                                                            as_index=False).agg(
                {"value": "mean"})
            data = df_to_hourly_classed_totals(avg5day, len(classes))
            dataset = []
            for classIndex, item in enumerate(data):
                dataset.append({"label": classes[classIndex].name, "data": item, "borderColor": classColors[classIndex],
                                "fill": False, "pointRadius": 0, "borderWidth": 1,
                                "backgroundColor": classColors[classIndex]})
            direction["baseData"].append(dataset)
            avg7day = df[(df["directionorder"] == int(dirIndex))].groupby(
                ["classorder", "hour"], as_index=False).agg({"value": "mean"})
            data = df_to_hourly_classed_totals(avg7day, len(classes))
            dataset = []
            for classIndex, item in enumerate(data):
                dataset.append({"label": classes[classIndex].name, "data": item, "borderColor": classColors[classIndex],
                                "fill": False, "pointRadius": 0, "borderWidth": 1,
                                "backgroundColor": classColors[classIndex]})
            direction["baseData"].append(dataset)
            directions.append(direction)
        print("finished full data formatting", datetime.datetime.now())
        return directions

    def extract_time_data_for_timezone(self, timezone="Europe/London", minute=False):
        tz = pytz.timezone(timezone)
        qs = self.annotate(
            hour=(Extract("date", lookup_name="hour", tzinfo=tz)))
        qs = qs.annotate(
            day=((Extract("date", lookup_name="week_day", tzinfo=tz) + 5) % 7))
        if minute:
            qs = qs.annotate(
                minute=(Extract("date", lookup_name="minute", tzinfo=tz)))
        return qs

    def as_dataframe(self, average=False, timezone="Europe/London"):
        ###
        # only for specific week, as we are not averaging monday.tuesday, etc
        # only for 1 location, no location filtering done here
        ###
        qs = self.extract_time_data_for_timezone(timezone, minute=False)
        if average:
            qs = qs.values("day", "hour", "minute", "direction",
                           "obsClass").annotate(value=Avg(F("value")))
        qs = qs.values("day", "hour", "direction",
                       "obsClass").annotate(total=Sum(F("value")))

        result = qs.values_list("day", "hour", "direction__order", "obsClass__order", "obsClass__obsClass__name",
                                "total")

        df = pd.DataFrame(list(result))
        if len(df) != 0:
            df.columns = ["day", "hour", "directionorder",
                          "classorder", "name", "value"]
            combined = df.groupby(["day", "hour", "classorder"], as_index=False).agg(
                {"value": "sum", "name": "first"})
            combined["directionorder"] = 2
            df = pd.concat([df, combined])
        else:
            df = pd.DataFrame([["0", 0, 0, 0, 0, 0, 0, "00:00"]],
                              columns=["location", "day", "hour", "minute", "directionorder", "classorder", "value",
                                       "time"])
        df["time"] = df.apply(lambda x: datetime.datetime(
            2020, 1, 1, x["hour"], 0).time(), axis=1)
        df["time"] = pd.to_timedelta(df["time"].astype(str))
        return df

    def toggle_bad_data(self, timezone="Europe/London", **kwargs):
        date = kwargs["date"]
        hour = kwargs["hour"]
        loc = kwargs["location"]
        if hour == "null":
            hour = None
        with connections[DB_NAME].cursor() as cursor:
            sqlString = f" select distinct(status) from {DB_NAME}_observation where location_id='" + str(
                loc.id) + "'"
            sqlString += " and DATE(CONVERT_TZ(date,'UTC','" + \
                timezone + "')) = '" + str(date.date()) + "'"
            if hour:
                sqlString += " and Hour(CONVERT_TZ(date,'UTC','" + \
                    timezone + "')) = " + str(hour)
            # print(sqlString)
            cursor.execute(sqlString)
            status = [c[0] for c in cursor.fetchall()]
            if len(status) == 0:
                ###
                # there is no data here
                pass
            print("status of selected data is", status)
            if 1 in status:
                status = 0
            else:
                status = 1
            sqlString = f" update {DB_NAME}_observation set status = " + \
                str(status)
            sqlString += " where location_id='" + str(
                loc.id) + "' and DATE(CONVERT_TZ(date,'UTC','" + timezone + "')) = '" + str(date.date()) + "'"
            if hour:
                sqlString += " and Hour(CONVERT_TZ(date,'UTC','" + \
                    timezone + "')) = " + str(hour)
            # print(sqlString)
            cursor.execute(sqlString)

    def toggle_remove_day(self, timezone="Europe/London", **kwargs):
        date = kwargs["date"]
        loc = kwargs["location"]
        with connections[DB_NAME].cursor() as cursor:
            sqlString = f" select distinct(removed) from {DB_NAME}_observation where location_id='" + str(
                loc.id) + "'"
            sqlString += " and DATE(CONVERT_TZ(date,'UTC','" + \
                timezone + "')) = '" + str(date.date()) + "'"
            # print(sqlString)
            cursor.execute(sqlString)
            status = [c[0] for c in cursor.fetchall()]
            if len(status) == 0:
                ###
                # there is no data here
                pass
            print("status of selected data is", status)
            if 1 in status:
                status = 0
            else:
                status = 1
            sqlString = f" update {DB_NAME}_observation set removed = " + \
                str(status)
            sqlString += " where location_id='" + str(
                loc.id) + "' and DATE(CONVERT_TZ(date,'UTC','" + timezone + "')) = '" + str(date.date()) + "'"
            # print(sqlString)
            cursor.execute(sqlString)

    def format_for_API(self):
        result = {}
        for item in self:
            d = item.date
            if (item.location_id, d, item.obsClass.obsClass_id) not in result:
                data = {"countIn": None, "countOut": None, "class": item.obsClass.obsClass.name,
                        "countLine": item.location.id, "from": d.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
                        "to": (d + datetime.timedelta(minutes=5)).strftime("%Y-%m-%dT%H:%M:%S.000Z")}
                result[(item.location_id, d, item.obsClass.obsClass_id)] = data
            print("directions are", item.directions.order)
            if item.direction.order == 1:
                result[(item.location_id, d, item.obsClass.obsClass_id)
                       ]["countIn"] = item.value
            if item.direction.order == 0:
                result[(item.location_id, d, item.obsClass.obsClass_id)
                       ]["countOut"] = item.value

        return [v for _, v in result.items()]


class ObservationManager(models.Manager):
    def get_queryset(self):
        return ObservationQuerySet(self.model, using=self._db)

    def format_for_API(self, counts):
        result = {}
        for item in counts:
            d = item.date
            if (item.location_id, d, item.obsClass.obsClass_id) not in result:
                data = {"countIn": None, "countOut": None, "class": item.obsClass.obsClass.name,
                        "countLine": item.location.id, "from": d.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
                        "to": (d + datetime.timedelta(minutes=5)).strftime("%Y-%m-%dT%H:%M:%S.000Z")}
                result[(item.location_id, d, item.obsClass.obsClass_id)] = data
            if item.direction.order == 1:
                result[(item.location_id, d, item.obsClass.obsClass_id)
                       ]["countIn"] = item.value
            if item.direction.order == 0:
                result[(item.location_id, d, item.obsClass.obsClass_id)
                       ]["countOut"] = item.value

        return [v for _, v in result.items()]


class Observation(models.Model):
    ###
    # model of observation that was taken by a device.
    ###

    ###
    # status of observation indicates whether data is good, bad
    ###
    # 0 = good , 1 =  bad data

    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    date = models.DateTimeField("Date")
    value = models.FloatField("Value")
    obsClass = models.ForeignKey(
        LocationObservationClass, on_delete=models.SET_NULL, null=True)
    direction = models.ForeignKey(
        LocationDirection, on_delete=models.SET_NULL, null=True)
    objects = ObservationManager()
    status = models.BooleanField(default=False)
    removed = models.BooleanField(default=False)
    weekday = models.IntegerField(blank=True, null=True)
    hr = models.IntegerField(blank=True, null=True)
    segment = models.IntegerField(blank=True, null=True)
    create_update_objects = BulkUpdateOrCreateQuerySet.as_manager()

    class Meta:
        db_table = "observation"


class LINKObservation(models.Model):
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    date = models.DateTimeField("Date")
    value = models.FloatField("Value")
    obsClass = models.ForeignKey(
        LocationObservationClass, on_delete=models.SET_NULL, null=True)
    direction = models.ForeignKey(
        LocationDirection, on_delete=models.SET_NULL, null=True)
    project = models.ForeignKey("Project", on_delete=models.CASCADE)
    obs_idx = models.IntegerField(default=None, blank=True, null=True)
    weather_code = models.IntegerField(default=None, blank=True, null=True)
    day_no = models.IntegerField(default=None, blank=True, null=True)
    time_15min = models.TimeField(default=None, blank=True, null=True)
    time_1hr = models.TimeField(default=None, blank=True, null=True)

    class Meta:
        db_table = "LINK_observation"


class ObservationSerializerForScatterChart(serializers.ModelSerializer):
    x = serializers.SerializerMethodField()
    y = serializers.FloatField(source="value")
    day = serializers.SerializerMethodField()
    color = serializers.SerializerMethodField()
    order = serializers.IntegerField(source="obsClass.order")
    direction = serializers.IntegerField(source="direction.order")
    obsClass = serializers.CharField(source="obsClass.obsClass.displayName")

    class Meta:
        model = Observation
        fields = ["x", "y", "day", "color", "order", "direction", "obsClass"]

    def get_color(self, obj):
        return classColors[obj.obsClass.order]

    def get_x(self, obj):
        t = obj.date.time()
        return (t.hour * 60 + t.minute) * 60 + t.second

    def get_day(self, obj):
        return obj.date.isoweekday()


class ObservationSerializer(serializers.ModelSerializer):
    ###
    # converts the date to the clients timezone if one is activated in the model method
    # also calculates the correct time segment for the converted date
    ###

    direction = serializers.SerializerMethodField()
    directionorder = serializers.SerializerMethodField()
    classorder = serializers.SerializerMethodField()
    seg = serializers.SerializerMethodField()
    day = serializers.SerializerMethodField()

    class Meta:
        model = Observation
        fields = ["location", "day", "seg", "direction",
                  "directionorder", "classorder", "value"]

    def get_directionorder(self, obj):
        return obj.direction.order

    def get_classorder(self, obj):
        return obj.obsClass.order

    def get_seg(self, obj):
        d = timezone.localtime(obj.date)
        return (d.hour * 12) + (d.minute // 5)

    def get_day(self, obj):
        return timezone.localtime(obj.date).isoweekday()

    def get_direction(self, obj):
        return obj.direction.direction.id

    def get_total(self, obj):
        # print("obj is",obj)
        return obj.total


class Project(models.Model):
    project_no = models.CharField(max_length=50)
    name = models.CharField(max_length=100)
    survey_type = models.CharField(max_length=50)
    client_id = models.CharField(max_length=50)
    scheme = models.CharField(max_length=100)

    class Meta:
        db_table = "project"

    def format_for_sidebar(self, style=None):
        if style == "crt":
            result = self.get_project_locations_by_obstype()
            for obsType, locations in result.items():
                obsType.areas = {}
                obsType.nameNoSpaces = obsType.name.replace(" ", "_").replace("'", "").replace("/", "_").replace("(",
                                                                                                                 "_").replace(
                    ")", "_")
                for loc in locations:
                    area = loc.area if loc.area else Area(
                        name="Unknown Area", id=0)
                    area.nameNoSpaces = area.name.replace(" ", "_").replace("'", "").replace("/", "_").replace("(",
                                                                                                               "_").replace(
                        ")", "_")
                    if area not in obsType.areas:
                        obsType.areas[area] = []
                    obsType.areas[area].append(loc)
                # print("areas for",obsType.name,"are",obsType.areas)
            # print("result is",result)
            print("from project")
            html = loader.render_to_string(
                f"{BASE_URL}/crt-style-sidebar.html", {"proj": result})
        else:
            html = ""
        return html

    def get_project_locations_by_obstype(self):
        result = {}
        obsTypes = ObservationType.objects.using(
            DB_NAME).filter(location__project=self)
        for t in obsTypes:
            t.nameWithoutSpaces = t.name.replace(" ", "_")
            # print("processing",t)
            result[t] = self.locations.filter(observationType__id=t.id)
        return result


class Messages(models.Model):
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    date = models.DateTimeField("Date")
    text = models.TextField(blank=True, null=True)
    type = models.IntegerField(blank=True, null=True)
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, blank=True, null=True)
    project = models.IntegerField(blank=True, null=True, db_column="project_id")

    class Meta:
        db_table = 'messages'


class BordersAggregatedData(models.Model):
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    day = models.IntegerField()  # 5day=0, 7day=1
    phase = models.IntegerField()  # before=0, after=1, 3rd survey  = 2
    direction = models.ForeignKey(
        LocationDirection, on_delete=models.SET_NULL, null=True)
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, db_column='project_id')
    avg = models.FloatField()
    perc_85th = models.FloatField()
    perc_95th = models.FloatField()
    timeval = models.IntegerField()
    counts = models.FloatField()

    #
    # The data is already aggregated and contains values for hourly periods, and also time periods eg 0700-1900
    # rather than store varied time periods, I am just assigning an index. 0-23 is hourly, 24 = 0700 - 1900
    # 25 = 0600-2200 26 = 0600 - 0000 27 = all day
    #
    timeval = models.IntegerField()

    class Meta:
        db_table = "borders_aggregated_data"


##################################################################
#
#
# Project
#
#
######################################################################

class ProjectQuerySet(models.QuerySet):
    def format_for_sidebar(self, style=None):
        if style == "crt":
            result = {}
            for loc in self.prefetch_related("area"):
                areaName = loc.area.name if loc.area else "Unknown Area"
                print("area name is", areaName)
                if areaName not in result:
                    result[areaName] = []
                result[areaName].append(loc)
            # print("result is",result)
            print("from project query set")
            html = loader.render_to_string(f"{BASE_URL}/crt-style-sidebar.html",
                                           {"sensors": {"Classified Counts": result}})
        else:
            html = "<ul>"
            for proj in self.order_by("name"):
                html += "<li id='" + str(
                    proj.id) + "'  onclick='viewProject(this);'><div class='sidebar-chevron' data-toggle='popover' " \
                               "data-content='" + str(proj.name) + "'>"
                html += "<div class='sidebar-item'>"
                html += "<div class='sidebar-item-icon'></div>"
                html += "<div class='sidebar-item-details'><div class='sidebar-item-details-title' " \
                        ">" + str(proj.id) + " " + \
                    str(proj.name) + "</div></div>"
                html += "</div></div></li>"
            html += "</ul>"
        return html


class ProjectManager(models.Manager):
    def get_queryset(self):
        return ProjectQuerySet(self.model, using=self._db)


class ProjectLocations(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    location = models.ForeignKey("Location", on_delete=models.CASCADE)
    speed_limit = models.CharField(max_length=50, blank=True, null=True)
    startDate = models.DateField(null=True, blank=True)
    endDate = models.DateField(null=True, blank=True)

    class Meta:
        db_table = "project_locations"


######################################################################
#
#
# Client
#
#
######################################################################


class ClientView(models.Model):
    client = models.ForeignKey("Client", on_delete=models.CASCADE)
    view = models.ForeignKey("View", on_delete=models.CASCADE)
    order = models.IntegerField("Order")
    display = models.BooleanField(default=True)

    class Meta:
        db_table = "clientview"


class Client(models.Model):
    name = models.CharField(max_length=100)
    locations = models.ManyToManyField(Location)
    users = models.ManyToManyField(User)
    nameForUrl = models.CharField(max_length=20, blank=True, null=True)
    logonBackground = models.FilePathField(path=os.path.join(
        BASE_DIR, 'aecon/static/aecon'))
    views = models.ManyToManyField("View", through="ClientView")
    timezone = models.CharField(max_length=255, default="Europe/London")
    mapCode = models.CharField(
        max_length=255, default="cjwgah7js2kbb1cp9aztbp6vm")
    apiKey = models.CharField(max_length=16, null=True, blank=True)

    class Meta:
        db_table = "client"

    def get_admin_stats(self):
        d = datetime.datetime.now().date()
        monday = d - datetime.timedelta(days=d.weekday())
        # print("correct start of calc period is", monday - datetime.timedelta(days=56))
        locs = self.locations.filter(
            temp=0, observationType_id=1, virtual=0, vivacityapi__in=[1, 2])
        obs = DailyClassedTotals.objects.using(DB_NAME).filter(date__gte=monday - datetime.timedelta(days=56),
                                                               date__lt=monday,
                                                               location_id=OuterRef("id"))
        #
        # get the average of the last 8 days that are the same day as yesterday, eg last 8 mondays
        #   so we subtract 1 day from todays isoweekday
        #
        q1 = obs.filter(date__iso_week_day=d.isoweekday() - 1).values("location_id").annotate(
            total=Coalesce(Sum("value") / 8, Value(0)))
        #
        # get the average week over the last 8 weeks
        #
        q2 = obs.values("location_id").annotate(weekly_avg=Sum("value") / 8)
        #
        # get the total counts from today so far
        #
        today = DailyClassedTotals.objects.using(DB_NAME).filter(
            date__contains=d, location_id=OuterRef("id"))
        today = today.values("location_id").annotate(today=Sum("value"))
        #
        # get the total counts from yesterday
        #
        yesterday = DailyClassedTotals.objects.using(DB_NAME).filter(date__contains=d - datetime.timedelta(days=1),
                                                                     location_id=OuterRef("id"))
        yesterday = yesterday.values(
            "location_id").annotate(yesterday=Sum("value"))
        #
        # get the total counts from last week
        #
        lastWeek = DailyClassedTotals.objects.using(DB_NAME).filter(date__gte=monday - datetime.timedelta(days=7),
                                                                    date__lt=monday, location_id=OuterRef("id"))
        lastWeek = lastWeek.values(
            "location_id").annotate(last_week=Sum("value"))

        locs = locs.annotate(weekday_avg=Subquery(q1.values("total")), weekly_avg=Subquery(q2.values("weekly_avg")),
                             weekly_total=Subquery(
                                 lastWeek.values("last_week")),
                             today_total=Subquery(today.values("today")),
                             yesterday_total=Subquery(
                                 yesterday.values("yesterday")),
                             api_name=F("vivacityapi__name"), area_name=F("area__name"),
                             project_name=Value(self.name, models.CharField()))

        locs = locs.values("project_name", "api_name", "id", "name", "area_name", "lastDataReceived",
                           "lastNonZeroDataReceived", "weekly_total",
                           "yesterday_total", "weekday_avg", "weekly_avg", "today_total", "api_identifier",
                           "vivacity_sensor_id")

        return locs

    def get_admin_weekly_stats(self):
        locs = self.locations.filter(temp=0, observationType_id=1, vivacityapi__in=[1, 2]).annotate(
            area_name=F("area__name"), project_name=Value(self.name, models.CharField()))
        d = datetime.datetime.now().date()
        monday = d - datetime.timedelta(days=d.weekday())
        locsDict = {loc.id: loc for loc in locs}
        # print("locs dict is", locsDict)
        data = locs.filter(
            dailyclassedtotals__date__gte=monday - datetime.timedelta(days=14),
            dailyclassedtotals__date__lt=monday,
            observationType_id=1, temp=0)
        data = data.values("dailyclassedtotals__date").annotate(
            total=Sum("dailyclassedtotals__value"))
        data = data.annotate(duration=Func(monday, F('dailyclassedtotals__date'), function="DateDiff",
                                           output_field=models.IntegerField()),
                             area_name=F("area__name"),
                             project_name=Value(self.name, models.CharField()))
        data = data.values("id", "name", "lastDataReceived", "dailyclassedtotals__date", "total", "duration",
                           "project_name", "area_name", "api_identifier")

        # print("data is", data)

        for loc in locs:
            for day in ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]:
                setattr(loc, day + "_0", 0)
                setattr(loc, day + "_1", 0)
                setattr(loc, day + "_perc", 0)
        for item in data:
            try:
                day = item["dailyclassedtotals__date"].strftime("%a").lower()
                weekday = item["dailyclassedtotals__date"].isoweekday()
                # print(item["dailyclassedtotals__date"], day, weekday)
                if item["duration"] < 8:
                    string = day + "_0"
                else:
                    string = day + "_1"
                setattr(locsDict[item["id"]], "area_name", item["area_name"])
                setattr(locsDict[item["id"]],
                        "project_name", item["project_name"])
                setattr(locsDict[item["id"]], string, item["total"])
            except Exception as e:
                print("failed to assign", e)
                setattr(locsDict[item["id"]], string, 0)
        # print(query_count_all())
        # print("num items", len(data))
        # for item in locs:
        #    print(item.name,item.id, item.mon_0, item.project_name)
        return locs

    def format_for_sidebar(self, style="crt"):

        if style == "crt":
            result = self.get_project_locations_by_obstype()
            for obsType, locations in result.items():
                obsType.areas = {}
                obsType.nameNoSpaces = obsType.name.replace(
                    " ", "_").replace("'", "").replace("/", "_")
                for loc in locations:
                    if loc.virtual:
                        locs = [loc] + list(loc.associatedLocations.all().annotate(
                            associated=Value("yes", output_field=CharField())).order_by("area", "name"))
                    else:
                        locs = [loc]

                    area = loc.area if loc.area else Area(
                        name="Unknown Area", id=0)
                    area.nameNoSpaces = area.name.replace(" ", "_").replace("'", "").replace("/", "_").replace("(",
                                                                                                               "_").replace(
                        ")", "_")
                    if area not in obsType.areas:
                        obsType.areas[area] = []
                    for item in locs:
                        obsType.areas[area].append(item)
                print("areas for", obsType.name, "are", obsType.areas)
                for key, val in obsType.areas.items():
                    # print("list for", key, "is", obsType.areas[key])
                    obsType.areas[key] = sorted(val, key=lambda x: x.name)
                    # print("list for",key,"is now",obsType.areas[key])
                # print("areas list is now", obsType.areas)
                obsType.areas = OrderedDict(sorted(obsType.areas.items(), key=lambda x: x[
                    0].nameNoSpaces))  # {k: v for k, v in sorted(obsType.areas.items(), key=lambda item: item[1].nameNoSpaces)}
                print("areas list is", obsType.areas)
            print("result is", result)
            return result
            html = loader.render_to_string(
                f"{BASE_URL}/crt-style-sidebar.html", {"proj": result, "request": request})
        else:
            html = ""
        return html

    def get_project_locations_by_obstype(self):
        result = {}
        obsTypes = ObservationType.objects.using(DB_NAME).filter(
            location__in=self.locations.all()).distinct()
        result = {o: [] for o in obsTypes}
        # print("obstypes are",obsTypes)
        for t in obsTypes:
            t.nameWithoutSpaces = t.name.replace(" ", "_")
            # print("processing",t)
            for item in self.locations.all():
                # print("processing", item, item.observationType_id, t, t.id)
                if item.observationType_id == t.id:
                    result[t].append(item)
        return result

    def get_views_as_popup_list(self, loc=None):
        html = "<ul>"
        views = ClientView.objects.using(DB_NAME).filter(client=self, display=True).order_by("order").select_related(
            "view")
        print("views are", views)
        for view in views:
            html += "<li id='view_0' class='menu-item popup-item'>"
            html += f"<a href='/{BASE_URL}/redirect?view=" + str(view.id)
            if loc:
                html += "&location_id=" + str(loc.id)
            html += "' class='selectable-menu-item'>"
            html += "<i ></i><span >" + \
                str(view.view.displayName) + "</span></a></li>"
        html += "</ul>"
        return html

    def get_occupancy_zones(self):
        zones = self.locations.filter(virtual=1)
        print("zone are", zones)
        html = "<ul>"
        for zone in zones:
            html += "<li id='zone_" + \
                str(zone.id) + "' class='menu-item popup-item'>"
            html += "<a href='#' class='selectable-menu-item'>"
            html += "<i ></i><span >" + str(zone.name) + "</span></a></li>"
        html += "</ul>"
        return html

    def clustering_as_table(self, tempSite):
        try:
            tempSite = self.locations.prefetch_related(
                "clustering_set").get(id=tempSite)
            prefetchClustermatch = Prefetch(
                'perm_site',
                queryset=ClusterMatch.objects.using(
                    DB_NAME).filter(temp=tempSite)
            )
            permSites = self.locations.filter(temp=False).prefetch_related(
                prefetchClustermatch, "clustering_set")
            html = ""
            for loc in permSites:
                html += "<tr data-site='" + str(loc.id) + "'>"
                html += "<td>" + str(loc.area.name) + "</td>"
                html += "<td>" + str(loc.name) + "</td>"
                for day in range(1, 4):
                    val = "-"
                    cellClass = "unmatched"
                    for c in loc.clustering_set.all():
                        if c.day == day:
                            val = c.value
                    for m in loc.perm_site.all():
                        if m.day == day:
                            cellClass = "matched"
                    html += "<td class='" + cellClass + \
                        "' onclick='toggleCluster(this);'>" + \
                        str(val) + "</td>"
                html += "</tr>"
            # print("html is",html)
            return html
        except Location.DoesNotExist as e:
            raise django.core.exceptions.ValidationError(
                {"Temp site": "You do not have access to the data for this site"})


######################################################################
#
#
# Views
#
#
######################################################################


class View(models.Model):
    html_file_name = models.CharField(max_length=255)
    displayName = models.CharField(max_length=255)
    redirect = models.BooleanField(default=False)

    class Meta:
        db_table = "view"


######################################################################
#
#
# Events
#
#
######################################################################

class EventQuerySet(models.QuerySet):

    def as_html(self, style=None):
        html = ""
        for event in self:
            html += "<div class='conduit-notification' id='event_" + str(
                event.id) + "'><div class='conduit-notification-icon' >"
            html += "<i class='" + event.icon + \
                "' style='color:green;'></i></div><div class='conduit-notification-details'>"
            html += "<div class='conduit-notification-details-title'>" + \
                str(event.desc) + "</div>"
            html += "<div class='conduit-notification-details-date'>" + event.date.strftime(
                "%d/%m/%Y") + "</div></div></div>"
        return html


class EventManager(models.Manager):
    def get_queryset(self):
        return EventQuerySet(self.model, using=self._db)

    @classmethod
    def create(self, *args, **kwargs):
        event = Event(desc=kwargs["desc"],
                      date=kwargs["date"], icon="flaticon-edit-1")
        if "location_id" in kwargs:
            event.location_id = kwargs["location_id"]
        event.full_clean()
        event.save(using=DB_NAME)
        return event


class Event(models.Model):
    desc = models.CharField(max_length=255, blank=True, null=True)
    date = models.DateField()
    icon = models.CharField(max_length=50, blank=True, null=True)
    addedBy = models.ForeignKey(
        User, on_delete=models.SET_NULL, blank=True, null=True, db_column="addedBy")
    location = models.ForeignKey(
        Location, on_delete=models.SET_NULL, blank=True, null=True)
    objects = EventManager()

    class Meta:
        db_table = "event"

    def clean_fields(self, *args, **kwargs):
        self.desc = clean_text(self.desc)
        self.desc = self.desc.replace("/n", " ")
        if self.desc == "":
            raise ValidationError("comment can not be blank")
        if self.date == "":
            raise ValidationError("Date can not be blank")


class DailyTotals(models.Model):
    location = models.ForeignKey(
        Location, on_delete=models.SET_NULL, null=True)
    # date is first day in month for total, eg jun total date would be 1/6/2020
    date = models.DateField()
    value = models.IntegerField(null=True)

    class Meta:
        db_table = "daily_totals"


class DailyClassedTotals(models.Model):
    location = models.ForeignKey(
        Location, on_delete=models.SET_NULL, null=True)
    # date is first day in month for total, eg jun total date would be 1/6/2020
    date = models.DateField()
    value = models.IntegerField(null=True)
    obsClass = models.ForeignKey(
        ObservationClass, on_delete=models.SET_NULL, null=True)

    class Meta:
        db_table = "daily_classed_totals"


######################################################################
#
#
# Clustering
#
#
######################################################################

class Clustering(models.Model):
    location = models.ForeignKey(
        Location, on_delete=models.SET_NULL, null=True)
    value = models.IntegerField(default=1)
    day = models.IntegerField()


class ClusterMatchQuerySet(models.QuerySet):

    def match(self, **kwargs):
        pass

    def get_perm_days_dict(self):
        #
        # we need a dict of the permanent sites that are matched with a temp site
        # and the days on which those matches apply , eg it may apply sat and sun, but not weekdays
        #
        result = {}
        for item in self:
            if item.perm_id not in result:
                result[item.perm_id] = []
            if item.day == 1:
                result[item.perm_id] += [0, 1, 2, 3, 4]
            if item.day == 2:
                result[item.perm_id] += [5]
            if item.day == 3:
                result[item.perm_id] += [6]
        print(result)
        return result


class ClusterMatchManager(models.Manager):
    def get_queryset(self):
        return ClusterMatchQuerySet(self.model, using=self._db)


class ClusterMatch(models.Model):
    temp = models.ForeignKey(
        Location, on_delete=models.SET_NULL, related_name="temp_site", null=True)
    perm = models.ForeignKey(
        Location, on_delete=models.SET_NULL, related_name="perm_site", null=True)
    day = models.IntegerField()
    objects = ClusterMatchManager()


######################################################################
#
#
# Factoring
#
#
######################################################################
class FactoringEventQuerySet(models.QuerySet):

    def match(self, **kwargs):
        pass


class FactoringEventManager(models.Manager):

    def get_queryset(self):
        return FactoringEventQuerySet(self.model, using=self._db)

    def get_current_event(self):
        currentEvent = FactoringEvent.objects.using(
            DB_NAME).filter(endDate__isnull=True)
        if currentEvent.count():
            return currentEvent[0]
        return None

    def create(self, **obj_data):
        print("in custom create", threading.current_thread().name)
        with lock("create_event_lock"):
            print("aquired lock")
            currentEvent = FactoringEvent.objects.using(
                DB_NAME).filter(endDate__isnull=True)
            print("current event is", currentEvent)
            if currentEvent.count() == 0:
                obj = FactoringEvent.objects.using(DB_NAME).create(**obj_data)
                print("creating event")
                return obj
            else:
                raise django.db.IntegrityError


class FactoringEvent(models.Model):
    startDate = models.DateTimeField()
    endDate = models.DateTimeField(blank=True, null=True)
    factoredFrom = models.DateTimeField(blank=True, null=True)
    factoredTo = models.DateTimeField(blank=True, null=True)
    numLocations = models.IntegerField(blank=True, null=True)
    msg = models.TextField(blank=True, null=True)
    eventType = models.CharField(max_length=100)
    objects = FactoringEventManager()


class ThreadSafe(models.Model):
    key = models.CharField(max_length=80, unique=True, primary_key=True)


######################################################################
#
#
# Weather codes from the open weather API
#
#
######################################################################

class WeatherCode(models.Model):
    main = models.CharField(max_length=100)
    description = models.CharField(max_length=100)
    icon = models.CharField(max_length=10)


######################################################################
#
#
# Associated 0bservation table holds meta data for a location, eg weather
#
#
######################################################################


class AssociatedObservation(models.Model):
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    date = models.DateTimeField("Date")
    value = models.FloatField("Value")
    obsClass = models.ForeignKey(
        LocationObservationClass, on_delete=models.SET_NULL, null=True)
    direction = models.ForeignKey(
        LocationDirection, on_delete=models.SET_NULL, null=True)
    objects = ObservationManager()
    status = models.BooleanField(default=False)
    removed = models.BooleanField(default=False)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    is_aggregated = models.BooleanField(default=False)
    obs_idx = models.IntegerField(default=None, blank=True, null=True)

    class Meta:
        db_table = "associatedobservation"


######################################################################
#
#
# models for importing data into the borders ATC database
#
#
######################################################################


class BordersLocation(models.Model):
    id = models.CharField(max_length=255, primary_key=True)
    lat = models.FloatField("Lat", null=True, blank=True)
    lon = models.FloatField("Lon", null=True, blank=True)
    name = models.CharField(max_length=100, blank=True, null=True)
    fileName = models.TextField()

    class Meta:
        db_table = "BordersLocation"


class BordersDirection(models.Model):
    id = models.CharField(max_length=2, primary_key=True)
    name = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        db_table = "BordersDirection"


class VehicleClass(models.Model):
    description = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        db_table = "vehicle_class"


class Data(models.Model):
    location = models.ForeignKey(BordersLocation, on_delete=models.CASCADE)
    date = models.DateField()
    time = models.TimeField()
    value = models.FloatField()
    obsClass = models.ForeignKey(
        VehicleClass, on_delete=models.SET_NULL, null=True, db_column="vehicle_class_id")
    direction = models.ForeignKey(
        BordersDirection, on_delete=models.SET_NULL, null=True)

    class Meta:
        db_table = "data"


class Otp(models.Model):
    # user_id = models.ManyToManyField(User)
    # id = models.CharField(max_length=2, primary_key=True)
    user_id = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, db_column="user_id")
    otp = models.CharField(max_length=6, null=False, blank=False)
    created_date_time = models.DateTimeField(null=False, blank=False)

    class Meta:
        db_table = "otp_table"


class Arms(models.Model):
    name = models.CharField(max_length=50)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    lat = models.FloatField("lat", null=True, blank=True)
    lon = models.FloatField("lon", null=True, blank=True)
    display_name = models.CharField(max_length=50)
    zone_id = models.CharField(max_length=50)

    class Meta:
        db_table = "arms"


class Jtc_Data(models.Model):
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    origin_arm = models.ForeignKey(
        Arms, on_delete=models.CASCADE, related_name='origin_arm')
    destination_arm = models.ForeignKey(
        Arms, on_delete=models.CASCADE, related_name='destination_arm')
    obsClass = models.ForeignKey(
        LocationObservationClass, on_delete=models.SET_NULL, null=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    start_time = models.TimeField()
    end_time = models.TimeField()
    count = models.FloatField()
    pcu = models.FloatField()
    peak_hour = models.CharField(max_length=10, default='No')
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    objects = ObservationManager()
    create_update_objects = BulkUpdateOrCreateQuerySet.as_manager()

    class Meta:
        db_table = "jtc_data"
