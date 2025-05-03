import os
import sys
import django
import pandas as pd
import csv
import joblib

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
sys.path.append(PROJECT_ROOT)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Aod_project.settings")
django.setup()

from Aod_data.models import RasterData
from Weather_data.models import WeatherData

rasterdata = RasterData.objects.latest('pk')
aod_value = rasterdata.data
aod_date = rasterdata.time_retrieve
weather_on_date = WeatherData.objects.filter(date=aod_date)

merged_rows = []

for aod in aod_value:
    aod_longitude = aod['longitude']
    aod_latitude = aod['latitude']
    aod_value = aod['aod_values']

    for weather_data in weather_on_date:

        station_longitude = weather_data.station.location.x
        station_latitude = weather_data.station.location.y
        station_temperature = weather_data.temperature
        station_humidity = weather_data.humidity
        station_windspeed = weather_data.wind_speed
        station_precipitation = weather_data.precipitation
        station_barometicPressure = weather_data.barometric_pressure
        station_tempMax = weather_data.temp_max
        station_tempMin = weather_data.temp_min
        station_feelsLikeMax = weather_data.feels_like_max
        station_feelsLikeMin = weather_data.feels_like_min
        station_feelsLike = weather_data.feels_like
        station_dewPoint = weather_data.dew_point
        station_windGust = weather_data.wind_gust
        station_cloudCover = weather_data.cloud_cover
        station_uvIndex = weather_data.uv_index
        station_solarRadiation = weather_data.solar_radiation
        station_solarEnergy = weather_data.solar_energy
        station_precipCover = weather_data.precip_cover
        station_windDir = weather_data.wind_dir
        station_seaLevelPressure = weather_data.sea_level_pressure
        station_visibility = weather_data.visibility


    merged_rows.append({
        'datetime': aod_date,
        'aod_longitude': aod_longitude,
        'aod_latitude': aod_latitude,
        'station_longitude': station_longitude,
        'station_latitude': station_latitude,
        'AOD': aod_value,
        'tempmax': station_tempMax,
        'tempmin': station_tempMin,
        'temp':station_temperature,
        'feelslikemax': station_feelsLikeMax,
        'feelslikemin': station_feelsLikeMin,
        'feelslike': station_feelsLike,
        'dew': station_dewPoint,
        'humidity': station_humidity,
        'precip': station_precipitation,
        'precipcover': station_precipCover,
        'windgust': station_windGust,
        'windspeed': station_windspeed,
        'winddir': station_windDir,
        'sealevelpressure': station_seaLevelPressure,
        'cloudcover': station_cloudCover,
        'visibilty': station_visibility,
        'solarradiation': station_solarRadiation,
        'solarenery': station_solarEnergy,
        'uvindex': station_uvIndex,
    })

folderpath = 'Aod_data/model'
file_name = os.path.join(folderpath, 'aod_data.csv')
fieldnames = merged_rows[0].keys()
with open(file_name, mode='w', newline='') as file:
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    
    # Menulis header ke CSV
    writer.writeheader()
    
    # Menulis data AOD ke CSV
    writer.writerows(merged_rows)

print(f'Data AOD berhasil disimpan ke dalam file {file_name}')