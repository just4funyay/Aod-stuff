import requests
from datetime import datetime
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.contrib.gis.geos import Point
from .models import WeatherData,WeatherStation,pm25DataActual,pm25DataPrediction
from .serializers import WeatherDataSerializer,pm25DataActualSerializer,pm25DataPredictionSerializer


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

class WeatherFetchView(APIView):
    def get(self, request):
        results = []
        stations = WeatherStation.objects.all()

        for station in stations:
            lat = station.location.y
            lon = station.location.x
            name = station.name

            url = f"{BASE_URL}{lat},{lon}?unitGroup=metric&key={API_KEY}&include=current"
            response = requests.get(url)

            if response.status_code == 200:
                data = response.json()
                current = data.get('currentConditions', {})
                date_str = data.get('days', [{}])[0].get('datetime')  # Format: '2024-05-01'

                if date_str:
                    date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()

                    # Cek apakah data ini sudah ada
                    if not WeatherData.objects.filter(station=station, date=date_obj).exists():
                        weather = WeatherData.objects.create(
                            station=station,
                            date=date_obj,
                            temperature=current.get('temp'),
                            humidity=current.get('humidity'),
                            wind_speed=current.get('windspeed'),
                            precipitation=current.get('precip'),
                            barometric_pressure=current.get('pressure')
                        )

                        results.append({
                            "station": name,
                            "date": date_obj,
                            "temperature": weather.temperature,
                            "humidity": weather.humidity,
                            "wind_speed": weather.wind_speed,
                            "precipitation": weather.precipitation,
                            "barometric_pressure": weather.barometric_pressure
                        })
                    else:
                        results.append({
                            "station": name,
                            "status": "Skipped - already exists"
                        })
                else:
                    results.append({
                        "station": name,
                        "status": "Missing date"
                    })
            else:
                results.append({
                    "station": name,
                    "error": f"Failed to fetch: {response.status_code}"
                })

        return Response(results, status=status.HTTP_200_OK)



class WeatherDataListView(APIView):
    def get(self, request):
        weather_data = WeatherData.objects.all()
        serializer = WeatherDataSerializer(weather_data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class LatestPM25ActualView(APIView):
    def get(self, request):
        latest_data = (
            pm25DataActual.objects
            .order_by('-id')  # atau gunakan '-pk' jika tidak ada timestamp
            .distinct('station')
        )
        serializer = pm25DataActualSerializer(latest_data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class LatestPM25PredictionView(APIView):
    def get(self, request):
        latest_by_station = []
        stations = set(pm25DataPrediction.objects.values_list('station_id', flat=True))
        for station_id in stations:
            latest = (
                pm25DataPrediction.objects
                .filter(station_id=station_id)
                .order_by('-date')
                .first()
            )
            if latest:
                latest_by_station.append(latest)

        serializer = pm25DataPredictionSerializer(latest_by_station, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
