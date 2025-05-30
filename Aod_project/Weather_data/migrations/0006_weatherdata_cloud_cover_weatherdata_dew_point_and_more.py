# Generated by Django 5.1.6 on 2025-05-02 06:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Weather_data', '0005_pm25dataactual_datetime'),
    ]

    operations = [
        migrations.AddField(
            model_name='weatherdata',
            name='cloud_cover',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='weatherdata',
            name='dew_point',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='weatherdata',
            name='feels_like',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='weatherdata',
            name='feels_like_max',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='weatherdata',
            name='feels_like_min',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='weatherdata',
            name='temp_max',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='weatherdata',
            name='temp_min',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='weatherdata',
            name='uv_index',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='weatherdata',
            name='wind_gust',
            field=models.FloatField(blank=True, null=True),
        ),
    ]
