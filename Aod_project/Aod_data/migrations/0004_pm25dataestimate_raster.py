# Generated by Django 5.1.6 on 2025-05-10 06:33

import django.contrib.gis.db.models.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Aod_data', '0003_alter_pm25dataestimate_aodid'),
    ]

    operations = [
        migrations.AddField(
            model_name='pm25dataestimate',
            name='raster',
            field=django.contrib.gis.db.models.fields.RasterField(blank=True, null=True, srid=4326),
        ),
    ]
