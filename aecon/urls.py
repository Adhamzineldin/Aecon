from django.conf.urls import url

from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

BASE_URL = settings.BASE_URL
schema_view = get_schema_view(
    openapi.Info(
        title="aecon API",
        default_version='v1',
        description="",
        url=f"/{BASE_URL}/api/v1",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="neil.watson@tracsis.com"),
        license=openapi.License(name="BSD License"),

    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [

    # used to authenticate user login credential
    url('aecon/logon(?P<client>.*)', views.logon, name='index'),


    # used to logout or to delete user session
    url('aecon/logoff', views.user_logout, name='index'),

    url('aecon/data-download/(?P<survey_type>\w{0,50})/$',
        views.data_download, name='data_download'),
    url('aecon/map-full-view', views.map_view, name='index'),
    path('aecon/atc-upload', views.atc_upload, name='atc_upload'),
    path('aecon/jtc-upload', views.jtc_upload, name='jtc_upload'),
    path('aecon/jtc-turning-count-upload', views.jtc_turning_count_upload, name='jtc_turning_count_upload'),
    path('aecon/jtc-download',
         views.jtc_download, name='jtc_download'),
    path('aecon/link-upload', views.link_upload, name='link_upload'),
    url('aecon/link-data-download',
        views.link_data_download, name='link_data_download'),

    url('aecon/radar-data(?P<tmpltext>.*)',
        views.radar_data, name="index"),
    url('aecon/radar-download',
        views.radar_download, name='radar_download'),

    url(r'^download-view', views.sensor_data_download, name='sensor_data_download'),
    url('aecon/sensor-data(?P<tmpltext>.*)',
        views.sensor_data, name='index'),

    url('aecon/radar-upload', views.radar_upload, name='radar_upload'),

    url('aecon/reset_password', views.reset_password, name='index'),
    url('aecon/welcome-page', views.welcome_page, name='index'),
    url('aecon/link-data(?P<tmpltext>.*)',
        views.link_data, name='index'),
    url('aecon/atc-data(?P<tmpltext>.*)', views.atc_data, name='index'),
    url('aecon/jtc-data(?P<tmpltext>.*)',
        views.jtc_data, name='jtc-data'),
    url('aecon/dashboard(?P<tmpltext>.*)',
        views.dashboard, name='index'),
    url('aecon/getAggregatedData',
        views.aggregated_data, name='index'),
    url('aecon/getAggregatedHeadlineData',
        views.aggregated_headline_data, name='index'),
    url('aecon/apiView', views.api_view, name='index'),
    url('aecon/getDirections',
        views.get_location_directions, name='index'),
    url('aecon/getATCcounts', views.get_atc_counts, name='getATCcounts'),
    url('aecon/getATCPSL', views.get_atc_psl, name='getATCPSL'),
    url('aecon/getLocationClasses',
        views.get_location_classes, name='index'),

    url('aecon/getLocations', views.get_locations, name='index'),
    url('aecon/getLocations2', views.get_locations, name='index'),
    url('aecon/getView', views.get_view, name='index'),
    url('aecon/getATCOverview', views.get_ATC_overview, name='index'),
    url('aecon/ATC', views.ATC_view, name='index'),
    url('aecon/getATCClassedVolumes',
        views.get_classed_volumes, name='index'),
    url('aecon/getATCClassedVolumes2',
        views.get_classed_volumes, name='index'),
    url('aecon/getCRTStyleData',
        views.get_crt_style_data, name='index'),
    url('aecon/getATCSpeedData', views.get_speed_data, name='index'),
    url('aecon/getATCScatterPlot',
        views.get_ATC_scatter_plot, name='index'),
    url('aecon/borders', views.borders_view, name='index'),
    url('aecon/east-lothian', views.borders_view, name='index'),
    url('aecon/admin/events', views.admin_events_view, name='index'),
    url('aecon/admin/allLocations',
        views.admin_all_locations, name='index'),
    url('aecon/admin/weekly-view',
        views.admin_all_locations_weekly, name='index'),
    url('aecon/admin/location',
        views.admin_location_view, name='index'),
    url('aecon/admin/saveLocation',
        views.save_location, name='index'),
    url('aecon/admin/backfillLocation',
        views.admin_backfill, name='index'),
    url('aecon/getWeather', views.get_weather_data, name='index'),
    url('aecon/getLocationDataCountsHourly',
        views.get_location_data_hourly_counts, name='index'),
    url('aecon/camden-speeds', views.camden_speed_view, name='index'),
    url('aecon/getLocationDataCounts',
        views.get_location_data_daily_counts, name='index'),
    url('aecon/viewLocation', views.view_location, name='index'),
    url('aecon/getClientLocations',
        views.get_client_locations, name='index'),
    url('aecon/speed-view', views.camden_speed_view, name='index'),
    url('aecon/camdenSpeeds', views.get_camden_speed_data, name='index'),
    url('aecon/redirect', views.redirect_to_view, name='index'),
    url('aecon/events', views.events, name='index'),
    url('aecon/startDownload',
        views.start_download_process, name='start_download'),
    url('aecon/checkFileReady',
        views.check_file_ready, name='start_download'),
    url('aecon/downloadFile',
        views.download_file, name='start_download'),
    url('aecon/saveClustering', views.save_clustering, name='index'),
    url('aecon/getClustering', views.get_clustering, name='index'),
    url('aecon/getPermClusteringForTempSite',
        views.get_perm_clustering_for_temp_site, name='index'),
    url('aecon/startFactoringProcess',
        views.start_factoring_thread, name='start_download'),
    url('aecon/get_jtc_data', views.get_jtc_data, name='GetJtcData'),
    url('aecon/add_update_jtc_Observation',
        views.add_update_jtc_Observation, name='add_update_jtc_Observation'),
    url('aecon/fetch_jtc_Observation',
        views.fetch_jtc_Observation, name='fetch_jtc_Observation'),

    # used to display the login page template for admin
    url('aecon/admin', views.admin_logon_view, name='index'),
    url('aecon/addUpdateObservation', views.addUpdateObservation, name='addUpdateObservation'),
    url('aecon/fetchObservation', views.fetchObservation, name='fetchObservation'),

    # used to display the login page template for user
    url(r'^(?P<client>.*)', views.logon_view, name='index'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
