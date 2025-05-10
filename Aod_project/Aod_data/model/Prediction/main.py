import sys
import os
import django
import numpy as np

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
sys.path.append(PROJECT_ROOT)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Aod_project.settings")
django.setup()

from Aod_data.models import RasterData
from Weather_data.models import WeatherData, pm25DataActual, WeatherStation
#ngambil data aod hari ini
#ngambil data pm2.5 hari ini
#ngambil data cuaca hari ini
data_aod = RasterData.objects.latest("pk")
aod_date = data_aod.time_retrieve
weather_on_date = WeatherData.objects.filter(date=aod_date)
pm25_on_date = pm25DataActual.objects.filter(date=aod_date)

# test data bundaran HI
bundaran_hi = WeatherStation.objects.get(id=4)
bundaran_hi_coordinateX = bundaran_hi.location.x
bundaran_hi_coordinateY = bundaran_hi.location.y
bundaran_hi_weather = weather_on_date.filter(station=4)
bundaran_hi_pm25 = pm25_on_date.filter(station=4)

latitudes = [entry['latitude'] for entry in data_aod.data]
longitudes = [entry['longitude'] for entry in data_aod.data]
data_values = [entry['aod_values'] for entry in data_aod.data]


def find_nearest(array, value):
    return (np.abs(array - value)).argmin()

# Mencari index terdekat
lat_idx = find_nearest(np.array(latitudes), bundaran_hi_coordinateY)
lon_idx = find_nearest(np.array(longitudes), bundaran_hi_coordinateX)

# Ambil nilai pada index tersebut
value = data_values[lat_idx]  # Sesuaikan dengan struktur data

print(f"Nilai data pada lat: {bundaran_hi_coordinateY}, lon: {bundaran_hi_coordinateX} = {value}")