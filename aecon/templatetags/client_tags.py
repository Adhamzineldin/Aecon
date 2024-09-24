from django import template
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe
import pandas as pd
import datetime
register = template.Library()
from aecon.models import *
from django.utils.safestring import mark_safe
from django.conf import settings

DB_NAME = settings.DB_NAME


@register.simple_tag(takes_context=True)
def views_as_popup_list(context):
    #print("in client tags view as popup list, context is", context)
    client = context["client"]
    return mark_safe(client.get_views_as_popup_list(loc=context.get("location")))


@register.simple_tag(takes_context=True)
def format_borders_data(context):
    #print("in client tags view as popup list, context is", context)
    data = context["data"]
    result = []



    return mark_safe(client.get_views_as_popup_list(loc=context.get("location")))


@register.simple_tag(takes_context=True)
def clustering_as_table(context, temp=False):
    client = context["client"]
    print("temp is",temp)
    locs = client.locations.filter(temp=temp).prefetch_related("clustering_set")
    print("locs are",locs)
    html = ""
    for loc in locs:
        html += "<tr data-site='" + str(loc.id) + "'>"
        html += "<td onclick='selectTempSite(this);'>" + loc.area.name + "</td>"
        html += "<td onclick='selectTempSite(this);'><div class='d-flex h-100'>"
        html += "<div class='edited'>"
        if loc.factoringEdited:
            html += "*"
        html += "</div>"
        html += "<div class='processing'>"
        if loc.processingFactoring:
            html += "P"
        html += "</div>"
        html += "<div style='margin-left:auto'>" + loc.name + "</div></div></td>"
        if len(loc.clustering_set.all()) == 0:
            html += "<td>-</td><td>-</td><td>-</td>"
        else:
            for cluster in loc.clustering_set.all():
                html += "<td>" + str(cluster.value) + "</td>"
        html += "</tr>"
    return mark_safe(html)


@register.simple_tag(takes_context=True)
def distinct_client_classes(context, temp=False):
    client = context["client"]
    locs = client.locations.all()
    classes = ObservationClass.objects.using(DB_NAME).filter(locationobservationclass__location__in=locs).distinct()
    return mark_safe(classes.as_dashboard_class_list())


@register.simple_tag()
def factoring_status():
    if FactoringEvent.objects.get_current_event():
        numLocs = Location.objects.using(DB_NAME).filter(factoringEdited=True).count()
        return "Factoring Currently In Progress - " + str(numLocs) + " remaining"
    return "Start Factoring Process"


@register.simple_tag()
def regional_areas():
    regions = list(Area.objects.using(DB_NAME).filter(region__isnull=False).values_list("region", flat=True).distinct().order_by("region"))
    print(regions)
    html = ""
    for item in regions:
        print("item is",item)
        html += "<option value='" + item + "'>" + item + "</option>"
    return mark_safe(html)

@register.filter
def order_by(queryset, args):
    args = [x.strip() for x in args.split(',')]
    return queryset.order_by(*args)
