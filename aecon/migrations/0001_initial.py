# Generated by Django 3.1.2 on 2024-09-20 14:37

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='APIDirection',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.IntegerField(verbose_name='Order')),
            ],
            options={
                'db_table': 'APIDirection',
            },
        ),
        migrations.CreateModel(
            name='Area',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('region', models.CharField(max_length=100)),
            ],
            options={
                'db_table': 'area',
            },
        ),
        migrations.CreateModel(
            name='Arms',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('lat', models.FloatField(blank=True, null=True, verbose_name='lat')),
                ('lon', models.FloatField(blank=True, null=True, verbose_name='lon')),
                ('display_name', models.CharField(max_length=50)),
                ('zone_id', models.CharField(max_length=50)),
            ],
            options={
                'db_table': 'arms',
            },
        ),
        migrations.CreateModel(
            name='BordersDirection',
            fields=[
                ('id', models.CharField(max_length=2, primary_key=True, serialize=False)),
                ('name', models.CharField(blank=True, max_length=100, null=True)),
            ],
            options={
                'db_table': 'BordersDirection',
            },
        ),
        migrations.CreateModel(
            name='BordersLocation',
            fields=[
                ('id', models.CharField(max_length=255, primary_key=True, serialize=False)),
                ('lat', models.FloatField(blank=True, null=True, verbose_name='Lat')),
                ('lon', models.FloatField(blank=True, null=True, verbose_name='Lon')),
                ('name', models.CharField(blank=True, max_length=100, null=True)),
                ('fileName', models.TextField()),
            ],
            options={
                'db_table': 'BordersLocation',
            },
        ),
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('nameForUrl', models.CharField(blank=True, max_length=20, null=True)),
                ('logonBackground', models.FilePathField(path='C:\\Users\\awsom\\Desktop\\Work\\Tracsis\\Sites\\AECON\\aecon/static/aecon')),
                ('timezone', models.CharField(default='Europe/London', max_length=255)),
                ('mapCode', models.CharField(default='cjwgah7js2kbb1cp9aztbp6vm', max_length=255)),
                ('apiKey', models.CharField(blank=True, max_length=16, null=True)),
            ],
            options={
                'db_table': 'client',
            },
        ),
        migrations.CreateModel(
            name='Direction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20, verbose_name='class')),
                ('descriptive', models.CharField(max_length=50, verbose_name='descriptive name')),
                ('abbrev', models.CharField(max_length=10, verbose_name='abbreviated name , eg NE for north east')),
            ],
            options={
                'db_table': 'direction',
            },
        ),
        migrations.CreateModel(
            name='FactoringEvent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('startDate', models.DateTimeField()),
                ('endDate', models.DateTimeField(blank=True, null=True)),
                ('factoredFrom', models.DateTimeField(blank=True, null=True)),
                ('factoredTo', models.DateTimeField(blank=True, null=True)),
                ('numLocations', models.IntegerField(blank=True, null=True)),
                ('msg', models.TextField(blank=True, null=True)),
                ('eventType', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='GroupObservationClass',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.IntegerField(verbose_name='Order')),
            ],
        ),
        migrations.CreateModel(
            name='JSONFile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file_name', models.CharField(max_length=255)),
                ('file_content', models.JSONField()),
            ],
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('geometry', models.BinaryField(blank=True, null=True)),
                ('lat', models.FloatField(blank=True, null=True, verbose_name='Lat')),
                ('lon', models.FloatField(blank=True, null=True, verbose_name='Lon')),
                ('name', models.CharField(blank=True, max_length=100, null=True)),
                ('device', models.IntegerField(blank=True, null=True)),
                ('imgURL', models.FilePathField(blank=True, null=True, path='C:\\Users\\awsom\\Desktop\\Work\\Tracsis\\Sites\\AECON\\staticfiles')),
                ('numDays', models.IntegerField(blank=True, default=0, null=True, verbose_name='number of days data')),
                ('validationDate', models.DateField(blank=True, null=True, verbose_name='validationDate')),
                ('lastDataReceived', models.DateTimeField(blank=True, null=True, verbose_name='Last Data Received At')),
                ('lastNonZeroDataReceived', models.DateTimeField(blank=True, db_column='last_non_zero_data', null=True, verbose_name='Last Non Zero Data Received At')),
                ('installDate', models.DateField(blank=True, null=True, verbose_name='Install Date')),
                ('startRecievingDate', models.DateField(blank=True, null=True, verbose_name='startRecievingDate')),
                ('speedLimit', models.IntegerField(blank=True, null=True, verbose_name='Posted Speed Limit')),
                ('speedLimit2', models.IntegerField(blank=True, default=20, null=True, verbose_name='Posted Speed Limit')),
                ('speedLimit3', models.IntegerField(blank=True, default=20, null=True, verbose_name='Posted Speed Limit')),
                ('status', models.CharField(blank=True, default='Good', max_length=20, null=True)),
                ('virtual', models.IntegerField(default=0)),
                ('temp', models.IntegerField(default=0)),
                ('factoringEdited', models.BooleanField(default=False)),
                ('processingFactoring', models.BooleanField(default=False)),
                ('api_identifier', models.CharField(db_column='api_identifier', max_length=255)),
                ('vivacity_sensor_id', models.CharField(db_column='vivacity_sensor_id', max_length=20)),
                ('sensorcheck', models.IntegerField(choices=[(1, 'Live'), (2, 'Under Review'), (3, 'No Longer In Use')], db_column='sensorcheck_status', default=1)),
                ('area', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='aecon.area')),
                ('associatedLocations', models.ManyToManyField(to='aecon.Location')),
            ],
            options={
                'db_table': 'location',
            },
        ),
        migrations.CreateModel(
            name='LocationDirection',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.IntegerField(verbose_name='Order')),
                ('line', models.BinaryField(blank=True, null=True, verbose_name='Line string')),
                ('direction', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='aecon.direction')),
                ('location', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='aecon.location')),
            ],
            options={
                'db_table': 'locationdirection',
            },
        ),
        migrations.CreateModel(
            name='LocationObservationClass',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.IntegerField(verbose_name='Order')),
                ('location', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='aecon.location')),
            ],
            options={
                'db_table': 'locationobservationclass',
            },
        ),
        migrations.CreateModel(
            name='ObservationClass',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='class')),
                ('units', models.CharField(blank=True, max_length=20, null=True, verbose_name='class')),
                ('displayName', models.CharField(blank=True, max_length=50, null=True, verbose_name='Display name')),
                ('description', models.CharField(blank=True, max_length=255, null=True, verbose_name='Extended Description')),
            ],
            options={
                'db_table': 'observationclass',
            },
        ),
        migrations.CreateModel(
            name='ObservationType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('iconURL', models.TextField(blank=True, null=True)),
            ],
            options={
                'db_table': 'observationtype',
            },
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('project_no', models.CharField(max_length=50)),
                ('name', models.CharField(max_length=100)),
                ('survey_type', models.CharField(max_length=50)),
                ('client_id', models.CharField(max_length=50)),
                ('scheme', models.CharField(max_length=100)),
            ],
            options={
                'db_table': 'project',
            },
        ),
        migrations.CreateModel(
            name='ThreadSafe',
            fields=[
                ('key', models.CharField(max_length=80, primary_key=True, serialize=False, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='UploadedFile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file_name', models.CharField(max_length=255)),
                ('file_content', models.BinaryField()),
            ],
        ),
        migrations.CreateModel(
            name='UploadLogging',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file_name', models.CharField(max_length=255)),
                ('uploaded_date', models.DateTimeField(auto_now_add=True)),
                ('converstion_to_CSV_start', models.DateTimeField(null=True)),
                ('converstion_to_CSV_end', models.DateTimeField(null=True)),
                ('observation_upload_start', models.DateTimeField(null=True)),
                ('observation_upload_end', models.DateTimeField(null=True)),
                ('existing_data_delete_start', models.DateTimeField(null=True)),
                ('existing_data_delete_end', models.DateTimeField(null=True)),
                ('aggregation_start', models.DateTimeField(null=True)),
                ('aggregation_end', models.DateTimeField(null=True)),
                ('process_end', models.DateTimeField(null=True)),
                ('error_txt', models.TextField(null=True)),
            ],
            options={
                'db_table': 'upload_logging',
            },
        ),
        migrations.CreateModel(
            name='VehicleClass',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(blank=True, max_length=100, null=True)),
            ],
            options={
                'db_table': 'vehicle_class',
            },
        ),
        migrations.CreateModel(
            name='View',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('html_file_name', models.CharField(max_length=255)),
                ('displayName', models.CharField(max_length=255)),
                ('redirect', models.BooleanField(default=False)),
            ],
            options={
                'db_table': 'view',
            },
        ),
        migrations.CreateModel(
            name='WeatherCode',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('main', models.CharField(max_length=100)),
                ('description', models.CharField(max_length=100)),
                ('icon', models.CharField(max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='VivacityAPI',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=255, null=True)),
                ('APIKey', models.CharField(blank=True, max_length=255, null=True)),
                ('baseUrl', models.CharField(blank=True, max_length=255, null=True)),
                ('record', models.BooleanField(default=False)),
                ('type', models.CharField(blank=True, max_length=50, null=True)),
                ('username', models.CharField(blank=True, max_length=255, null=True)),
                ('password', models.CharField(blank=True, max_length=255, null=True)),
                ('period', models.CharField(blank=True, max_length=255, null=True)),
                ('classes', models.ManyToManyField(to='aecon.ObservationClass')),
                ('directions', models.ManyToManyField(through='aecon.APIDirection', to='aecon.Direction')),
                ('locations', models.ManyToManyField(to='aecon.Location')),
            ],
            options={
                'db_table': 'vivacityapi',
            },
        ),
        migrations.CreateModel(
            name='ProjectLocations',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('speed_limit', models.CharField(blank=True, max_length=50, null=True)),
                ('startDate', models.DateField(blank=True, null=True)),
                ('endDate', models.DateField(blank=True, null=True)),
                ('location', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='aecon.location')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='aecon.project')),
            ],
            options={
                'db_table': 'project_locations',
            },
        ),
        migrations.CreateModel(
            name='Otp',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('otp', models.CharField(max_length=6)),
                ('created_date_time', models.DateTimeField()),
                ('user_id', models.ForeignKey(db_column='user_id', null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'otp_table',
            },
        ),
        migrations.CreateModel(
            name='ObservationClassGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20, verbose_name='Group Name')),
                ('displayName', models.CharField(blank=True, max_length=20, null=True, verbose_name='Display name')),
                ('description', models.CharField(blank=True, max_length=255, null=True, verbose_name='Extended Description')),
                ('classes', models.ManyToManyField(through='aecon.GroupObservationClass', to='aecon.ObservationClass')),
            ],
        ),
        migrations.CreateModel(
            name='Observation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(verbose_name='Date')),
                ('value', models.FloatField(verbose_name='Value')),
                ('status', models.BooleanField(default=False)),
                ('removed', models.BooleanField(default=False)),
                ('weekday', models.IntegerField(blank=True, null=True)),
                ('hr', models.IntegerField(blank=True, null=True)),
                ('segment', models.IntegerField(blank=True, null=True)),
                ('direction', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='aecon.locationdirection')),
                ('location', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='aecon.location')),
                ('obsClass', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='aecon.locationobservationclass')),
            ],
            options={
                'db_table': 'observation',
            },
        ),
        migrations.CreateModel(
            name='Messages',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(verbose_name='Date')),
                ('text', models.TextField(blank=True, null=True)),
                ('type', models.IntegerField(blank=True, null=True)),
                ('project', models.IntegerField(blank=True, db_column='project_id', null=True)),
                ('location', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='aecon.location')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'messages',
            },
        ),
        migrations.AddField(
            model_name='locationobservationclass',
            name='obsClass',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='aecon.observationclass'),
        ),
        migrations.AddField(
            model_name='location',
            name='classes',
            field=models.ManyToManyField(through='aecon.LocationObservationClass', to='aecon.ObservationClass'),
        ),
        migrations.AddField(
            model_name='location',
            name='directions',
            field=models.ManyToManyField(through='aecon.LocationDirection', to='aecon.Direction'),
        ),
        migrations.AddField(
            model_name='location',
            name='observationType',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='aecon.observationtype'),
        ),
        migrations.AddField(
            model_name='location',
            name='projects',
            field=models.ManyToManyField(through='aecon.ProjectLocations', to='aecon.Project'),
        ),
        migrations.CreateModel(
            name='LINKObservation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(verbose_name='Date')),
                ('value', models.FloatField(verbose_name='Value')),
                ('obs_idx', models.IntegerField(blank=True, default=None, null=True)),
                ('weather_code', models.IntegerField(blank=True, default=None, null=True)),
                ('day_no', models.IntegerField(blank=True, default=None, null=True)),
                ('time_15min', models.TimeField(blank=True, default=None, null=True)),
                ('time_1hr', models.TimeField(blank=True, default=None, null=True)),
                ('direction', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='aecon.locationdirection')),
                ('location', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='aecon.location')),
                ('obsClass', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='aecon.locationobservationclass')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='aecon.project')),
            ],
            options={
                'db_table': 'LINK_observation',
            },
        ),
        migrations.CreateModel(
            name='Jtc_Data',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_date', models.DateField(blank=True, null=True)),
                ('end_date', models.DateField(blank=True, null=True)),
                ('start_time', models.TimeField()),
                ('end_time', models.TimeField()),
                ('count', models.FloatField()),
                ('pcu', models.FloatField()),
                ('peak_hour', models.CharField(default='No', max_length=10)),
                ('destination_arm', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='destination_arm', to='aecon.arms')),
                ('location', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='aecon.location')),
                ('obsClass', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='aecon.locationobservationclass')),
                ('origin_arm', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='origin_arm', to='aecon.arms')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='aecon.project')),
            ],
            options={
                'db_table': 'jtc_data',
            },
        ),
        migrations.AddField(
            model_name='groupobservationclass',
            name='group',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='aecon.observationclassgroup'),
        ),
        migrations.AddField(
            model_name='groupobservationclass',
            name='obsClass',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='aecon.observationclass'),
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('desc', models.CharField(blank=True, max_length=255, null=True)),
                ('date', models.DateField()),
                ('icon', models.CharField(blank=True, max_length=50, null=True)),
                ('addedBy', models.ForeignKey(blank=True, db_column='addedBy', null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('location', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='aecon.location')),
            ],
            options={
                'db_table': 'event',
            },
        ),
        migrations.CreateModel(
            name='Data',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('time', models.TimeField()),
                ('value', models.FloatField()),
                ('direction', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='aecon.bordersdirection')),
                ('location', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='aecon.borderslocation')),
                ('obsClass', models.ForeignKey(db_column='vehicle_class_id', null=True, on_delete=django.db.models.deletion.SET_NULL, to='aecon.vehicleclass')),
            ],
            options={
                'db_table': 'data',
            },
        ),
        migrations.CreateModel(
            name='DailyTotals',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('value', models.IntegerField(null=True)),
                ('location', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='aecon.location')),
            ],
            options={
                'db_table': 'daily_totals',
            },
        ),
        migrations.CreateModel(
            name='DailyClassedTotals',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('value', models.IntegerField(null=True)),
                ('location', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='aecon.location')),
                ('obsClass', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='aecon.observationclass')),
            ],
            options={
                'db_table': 'daily_classed_totals',
            },
        ),
        migrations.CreateModel(
            name='ClusterMatch',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('day', models.IntegerField()),
                ('perm', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='perm_site', to='aecon.location')),
                ('temp', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='temp_site', to='aecon.location')),
            ],
        ),
        migrations.CreateModel(
            name='Clustering',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.IntegerField(default=1)),
                ('day', models.IntegerField()),
                ('location', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='aecon.location')),
            ],
        ),
        migrations.CreateModel(
            name='ClientView',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.IntegerField(verbose_name='Order')),
                ('display', models.BooleanField(default=True)),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='aecon.client')),
                ('view', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='aecon.view')),
            ],
            options={
                'db_table': 'clientview',
            },
        ),
        migrations.AddField(
            model_name='client',
            name='locations',
            field=models.ManyToManyField(to='aecon.Location'),
        ),
        migrations.AddField(
            model_name='client',
            name='users',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='client',
            name='views',
            field=models.ManyToManyField(through='aecon.ClientView', to='aecon.View'),
        ),
        migrations.CreateModel(
            name='BordersAggregatedData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('day', models.IntegerField()),
                ('phase', models.IntegerField()),
                ('avg', models.FloatField()),
                ('perc_85th', models.FloatField()),
                ('perc_95th', models.FloatField()),
                ('counts', models.FloatField()),
                ('timeval', models.IntegerField()),
                ('direction', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='aecon.locationdirection')),
                ('location', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='aecon.location')),
                ('project', models.ForeignKey(db_column='project_id', on_delete=django.db.models.deletion.CASCADE, to='aecon.project')),
            ],
            options={
                'db_table': 'borders_aggregated_data',
            },
        ),
        migrations.CreateModel(
            name='AssociatedObservation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(verbose_name='Date')),
                ('value', models.FloatField(verbose_name='Value')),
                ('status', models.BooleanField(default=False)),
                ('removed', models.BooleanField(default=False)),
                ('is_aggregated', models.BooleanField(default=False)),
                ('obs_idx', models.IntegerField(blank=True, default=None, null=True)),
                ('direction', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='aecon.locationdirection')),
                ('location', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='aecon.location')),
                ('obsClass', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='aecon.locationobservationclass')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='aecon.project')),
            ],
            options={
                'db_table': 'associatedobservation',
            },
        ),
        migrations.AddField(
            model_name='arms',
            name='location',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='aecon.location'),
        ),
        migrations.AddField(
            model_name='arms',
            name='project',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='aecon.project'),
        ),
        migrations.AddField(
            model_name='apidirection',
            name='api',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='aecon.vivacityapi'),
        ),
        migrations.AddField(
            model_name='apidirection',
            name='direction',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='aecon.direction'),
        ),
    ]
