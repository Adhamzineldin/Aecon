from django import template
from django.template import loader
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe
import pandas as pd
import datetime
from aecon.models import *
from django.conf import settings



register = template.Library()
DB_NAME = settings.DB_NAME


@register.simple_tag(takes_context=True)
def camden_data_matrix(context, style="crt"):
    locs = Location.objects.using(DB_NAME).filter(id__in=['15940', '15942', '15943', '15944', '15945', '16189', '16192', '16195', '16198', '16201', '16204', '16207', '16231'])
    locs = locs.order_by("name")

    num = Count(Case(
        When(value__gt=0, then=1),
        output_field=IntegerField(),
    ))

    sub = AssociatedObservation.objects.using(DB_NAME).filter(location__in=locs).values("location","date__date")
    sub = sub.annotate(num=Sum("value")).values("location", "date__date", "num")
    for loc in locs:
        loc.matrix = sorted([i for i in sub if i["location"] == loc.id], key=lambda x: x["date__date"])
    return locs
    print(locs)



@register.simple_tag(takes_context=True)
def format_for_sidebar(context, style="crt"):
    #print("here!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!",context["client"])
    #print("style is", style)

    if style == "crt":
        client = context["client"]
        result = client.format_for_sidebar()

        html = loader.render_to_string("aecon/crt-style-sidebar.html", {"proj":result, "request": context["request"]})
    elif style == "admin":
        html = ""
        clients = Client.objects.using(DB_NAME).all().exclude(id__in=[2, 4, 11]).prefetch_related("locations")
        obsTypes = ObservationType.objects.using(DB_NAME).filter(location__client__in=clients).distinct()
        #print(obsTypes)
        result = {o: [] for o in obsTypes}
        # print("obstypes are",obsTypes)
        for t in obsTypes:
            #print("processing", t, t.id)
            #print({c: [l for l in c.locations.all() if not l.temp and l.observationType_id == t.id] for c in clients})
            t.areas = {c: [l for l in c.locations.all() if (not l.temp) and (l.observationType_id == t.id)] for c in clients}
            t.nameNoSpaces = t.name.replace(" ","_").replace("(","_").replace(")","_")
            #print("name no spaces is", t.nameNoSpaces)
        for c in clients:
            c.nameNoSpaces = c.name.replace(" ", "_").replace("(","_").replace(")","_")
        #for key,val in result.items():
            #print("wibble", key.nameNoSpaces)

        html = loader.render_to_string("aecon/crt-style-sidebar.html", {"proj": result, "request": context["request"]})

    else:
        html = ""
    #print("in format for sidebar,style is",style , " returining", html)
    return html


@register.simple_tag
def time_range(r="15"):
    rng = pd.date_range('2011-03-01 00:00', '2011-03-02 00:00', freq=r + 'T',closed="left")
    return [r[:5] for r in rng.time.astype(str)]

@register.simple_tag
def time_range_5_mins():
    rng = pd.date_range('2011-03-01 00:00', '2011-03-02 00:00', freq='5T',closed="left")
    return [r[:5] for r in rng.time.astype(str)]


@register.filter(name='has_group')
def has_group(user, group_name):
    for group in user.groups.all():
        if group.name == group_name:
            return True
    return False

@register.filter()
def nameNoSpaces(value):
    return value.replace(" ", "_").replace("(","_").replace(")","_")

@register.filter()
def context_to_json(value):
    loc_dict = {}
    for key,value in value.items():
        loc_dict[key]  = [x.id for x in value]
    return json.dumps(loc_dict)
    


@register.filter(name='none_or_zero')
def none_or_zero(value):
    #print("in none_or_zero",value)
    return value or 0

@register.filter(name='percentage')
def percentage(num, denom):
    #print("inpercentage")
    try:
        return round(num * 100/denom, 2)
    except (ZeroDivisionError, TypeError) as e:
        return 0

@register.filter
def index(indexable, i):
    print("looking for index", i , "in", len(indexable))
    return indexable[i]["num"]