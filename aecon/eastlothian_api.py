from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.response import Response
from rest_framework.renderers import BrowsableAPIRenderer
from  rest_framework.exceptions import server_error
from .models import *

from django.http import HttpResponse,JsonResponse,Http404,HttpResponseRedirect,HttpResponseForbidden,HttpResponseBadRequest
from rest_framework.exceptions import APIException,ParseError,NotFound
from rest_framework.renderers import JSONRenderer
import pymysql
import django
from django.conf import settings
import json
#import mysql.connector
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from django.contrib.auth.decorators import login_required
from django.template import loader, Context
from django.contrib.auth import authenticate,login,logout
from django.shortcuts import redirect
from django.db import connections
from django.db.models import Prefetch,Case, CharField, Value, When,DateField,TimeField,OuterRef, Subquery,F
from rest_framework.pagination import LimitOffsetPagination
from collections import OrderedDict
import datetime
from rest_framework.exceptions import APIException, ValidationError, NotFound as NotFoundError

BASE_URL = settings.BASE_URL
LOGIN_URL = settings.LOGIN_URL
DB_NAME = settings.DB_NAME
class ServiceUnavailable(APIException):
    status_code = 503
    default_detail = 'Service temporarily unavailable, try again later.'
    default_code = 'service_unavailable'


def query_count_all():
    query_total = 0
    for c in connections.all():
        #print(c)
        for item in c.queries:
            print(item)
        query_total += len(c.queries)
    return query_total


def api_key_required(func):
    def decorator(request, *args, **kwargs):
        print("request method is",request.method)
        print("wibble")
        try:
            if request.method == "POST":
                print("data is",request.POST)
                apiKey = request.POST["api_key"]
                clientId = request.POST["client"]
            elif request.method == "GET":
                print("data is", request.GET)
                apiKey = request.query_params["api_key"]
                clientId = request.query_params["client"]
            else:
                return HttpResponseBadRequest("invalid request method")
            client = Client.objects.using(DB_NAME).get(id=clientId)
            assert apiKey == client.apiKey
        except Client.DoesNotExist as e:
            raise ValidationError({"client": "No such client"})
        except KeyError as e:
            print(str(e))
            raise ValidationError({str(e): "This field is required"})
        except AssertionError as e:
            raise ValidationError({"Api key": "Invalid Api key"})
        return func(request,client, *args, **kwargs)
    return decorator


def catch_errors(func):
    def decorator(request, *args, **kwargs):
        try:
            return func(request, *args, **kwargs)
        except (django.db.utils.Error,pymysql.Error) as e:
            print("database error",e)
            raise ServiceUnavailable("Database error - database unavailable ")
        except KeyError as e:
            raise ValidationError({str(e): "This field is required"})
    return decorator


api_key = openapi.Parameter('api_key', openapi.IN_QUERY, description="api key", type=openapi.TYPE_STRING,required=True)
client = openapi.Parameter('client', openapi.IN_QUERY, description="client Id", type=openapi.TYPE_INTEGER,required=True)
date_from = openapi.Parameter('startDate', openapi.IN_QUERY, description="Date from (UTC) in format yyyy-mm-dd hh:mm:ss", type=openapi.TYPE_STRING,required=True)
date_to = openapi.Parameter('endDate', openapi.IN_QUERY, description="Date to (UTC) in format yyyy-mm-dd hh:mm:ss", type=openapi.TYPE_STRING,required=True)
page = openapi.Parameter('page', openapi.IN_QUERY, description="Page number", type=openapi.TYPE_INTEGER,required=True)
page_size = openapi.Parameter('page_size', openapi.IN_QUERY, description="Page number", type=openapi.TYPE_INTEGER,required=False)
countlineString = openapi.Parameter('countlines', openapi.IN_QUERY, description="comma separated list of countlines", type=openapi.TYPE_STRING,required=True)


class customPaginator(LimitOffsetPagination):

    def __init__(self):
        super().__init__()
        self.current_page = None

    def get_offset(self, request):
        try:
            self.current_page = int(request.query_params["page"])
            assert self.current_page > 0
        except (ValueError,AssertionError) as e:
            raise ValidationError({"page": "invalid page"})
        return (self.current_page - 1) * self.default_limit


    def get_paginated_response(self, data):
        self.count //= 2
        if self.default_limit and self.default_limit != 0:
            totalPages = int(self.count/self.default_limit) + 1
        else:
            totalPages = 0
        return Response(OrderedDict([
            ('count', self.count),
            ('current page', self.current_page),
            ('total pages', totalPages),
            ('results', data)
        ]))

    def paginate_queryset(self, queryset, request, view=None):
        self.count = self.get_count(queryset)
        self.limit = self.get_limit(request) * 2
        if self.limit is None:
            return None

        self.offset = self.get_offset(request) * 2
        print("offset is",self.offset)
        self.request = request
        if self.count > self.limit and self.template is not None:
            self.display_page_controls = True

        if self.count == 0 or self.offset > self.count:
            return []
        return list(queryset[self.offset:self.offset + self.limit])

def swagger_index(request):
    print("in swagger index)")
    template = loader.get_template(f'{BASE_URL}/swaggerLogonScreen.html')
    logo = "crt/crt_white.png"
    page = "crt/CRTLandingPage.jpg"
    context = {"background": page, "clientLogo": logo, "appLogo": "crt/Conduit Logo.png"}
    return HttpResponse(template.render(context, request))


def swagger_logon(request):
    print("in swagger logon")
    data = request.POST
    if "username" in data and "password" in data:
        username = data["username"]
        pw = data["password"]
        user = authenticate(request, username=username, password=pw)
        if user is None:
            print("authentication failed")
            return HttpResponseForbidden()
        login(request, user,backend=f'{BASE_URL}.myauthbackend.CustomAuthBackend')
    else:
        if hasattr(request, "user"):
            print("already logged in")
            user = request.user
        else:
            return HttpResponseForbidden()
    try:
        proj = request.user.client_set.all()[0]
    except Exception as e:
        return HttpResponseForbidden()
    return HttpResponseRedirect(f"/{BASE_URL}/swagger/")


@login_required(login_url="api/logon")
def swagger_view(request):
    from .urls import schema_view as sc
    return sc.with_ui('swagger', cache_timeout=0)(request)


@login_required(login_url="/api/logon")
def swagger_logout(request):
    logout(request)
    return HttpResponseRedirect("/api/logon")



@swagger_auto_schema(method="get",manual_parameters=[api_key, client])
@api_view(('GET',))
@api_key_required
@catch_errors
def get_countlines(request,client):
    print("in get countlines",client.locations.all().prefetch_related("area"))
    locs = LocationSerializerForAPI(client.locations.all().prefetch_related("area"),many=True).data
    print(query_count_all())
    return Response(locs)


@swagger_auto_schema(method="get",manual_parameters=[api_key, client, date_from, date_to, page, countlineString])
@api_view(('GET',))
@api_key_required
@catch_errors
def get_counts(request, client):
    print("client is",client)
    params = request.query_params
    if params["countlines"] == "all":
        countlines = list(client.locations.all().values_list("id",flat=True))
    else:
        countlines = params["countlines"].split(",")
        print("countlines are",countlines)
        countlines = client.locations.filter(id__in=countlines)
        print("countlines are", countlines)
    try:
        startDate = datetime.datetime.strptime(params["startDate"],"%Y-%m-%d %H:%M:%S")
        endDate = datetime.datetime.strptime(params["endDate"], "%Y-%m-%d %H:%M:%S")
        assert startDate + datetime.timedelta(days=1) >= endDate
    except ValueError as e:
        raise ValidationError({"date format": "Invalid date format, must be yyyy-mm-dd hh:mm:ss"})
    except AssertionError as e:
        raise ValidationError({"date range": "Date range limited to one day"})
    counts = Observation.objects.using(DB_NAME).filter(location__in=countlines,
                                               date__gte=startDate.date(),
                                               date__lt=endDate.date())
    print(counts.query)
    #counts = counts.exclude(date=startDate.date(), startTime__lt=startDate.time())
    #counts = counts.exclude(date=endDate.date(), startTime__gte=endDate.time())
    counts = counts.prefetch_related("obsClass__obsClass","direction__direction", "location").order_by("date")
    print("counts are", counts)
    custom = customPaginator()
    result = custom.paginate_queryset(counts, request)
    result = custom.get_paginated_response(Observation.objects.format_for_API(result))
    return result
