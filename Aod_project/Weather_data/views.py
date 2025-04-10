import requests
from datetime import datetime
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.contrib.gis.geos import Point
from .models import WeatherData
from .serializers import WeatherDataSerializer


API_KEY = "KTJ63YA3XS9PHPBWTWHKAR5D8"
BASE_URL = "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/"

lokasi = {
    'us_embassy_1': (-6.1811056, 106.8279877),
    'us_embassy_2': (-6.236658728205383, 106.79319751533286),
    'jakarta_gbk': (-6.2155, 106.803),
    'bundaran_hi': (-6.19466, 106.8235),
    'kelapa_gading': (-6.1535777, 106.910887),
    'jagakarsa': (-6.35693, 106.80367),
    'lubang_buaya': (-6.28889, 106.90919),
    'kebun_jeruk': (-6.20737, 106.7525)
}

class WeatherView(APIView):
    def get(self, request):
        results = []
        for nama, (lat, lon) in lokasi.items():
            api_url = f"{BASE_URL}{lat},{lon}?unitGroup=metric&key={API_KEY}&include=current"

            response = requests.get(api_url)
            if response.status_code == 200:
                data = response.json()
                current_data = data.get('currentConditions', {})

                
                date_part = data.get('days', [{}])[0].get('datetime', None)  
                time_part = current_data.get('datetime', None)  
                
                if date_part and time_part:
                    full_datetime_str = f"{date_part} {time_part}"
                    full_datetime = datetime.strptime(full_datetime_str, "%Y-%m-%d %H:%M:%S")
                else:
                    full_datetime = None  

                
                temperature = current_data.get('temp', None)
                humidity = current_data.get('humidity', None)
                wind_speed = current_data.get('windspeed', None)
                precipitation = current_data.get('precip', None)
                barometric_pressure = current_data.get('pressure', None)

               
                weather_entry = WeatherData.objects.create(
                    name_location=nama,
                    geom=Point(lon, lat),  
                    datetime=full_datetime,
                    temperature=temperature,
                    humidity=humidity,
                    wind_speed=wind_speed,
                    precipitation=precipitation,
                    barometric_pressure=barometric_pressure
                )

                results.append({
                    "name_location": nama,
                    "geom": {"type": "Point", "coordinates": [lon, lat]},
                    "datetime": full_datetime,
                    "temperature": temperature,
                    "humidity": humidity,
                    "wind_speed": wind_speed,
                    "precipitation": precipitation,
                    "barometric_pressure": barometric_pressure
                })
            else:
                results.append({
                    "name_location": nama,
                    "geom": {"type": "Point", "coordinates": [lon, lat]},
                    "error": f"Failed to fetch data: {response.status_code}"
                })

        return Response(results, status=status.HTTP_200_OK)



class WeatherDataListView(APIView):
    def get(self, request):
        weather_data = WeatherData.objects.all()
        serializer = WeatherDataSerializer(weather_data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
