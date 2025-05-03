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

class WeatherFetchView(APIView):
    def get(self, request):
        results = []
        stations = WeatherStation.objects.all()

        for station in stations:
            lat = station.location.y
            lon = station.location.x
            name = station.name

            url = f"{BASE_URL}{lat},{lon}?unitGroup=metric&key={API_KEY}&include=days"
            response = requests.get(url)

            if response.status_code == 200:
                data = response.json()
                days = data.get('days', [])

                if days:
                    day_data = days[0]
                    date_str = day_data.get('datetime')
                    if date_str:
                        date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()

                        if not WeatherData.objects.filter(station=station, date=date_obj).exists():
                            weather = WeatherData.objects.create(
                                station=station,
                                date=date_obj,
                                temperature=day_data.get('temp'),
                                temp_max=day_data.get('tempmax'),
                                temp_min=day_data.get('tempmin'),
                                feels_like=day_data.get('feelslike'),
                                feels_like_max=day_data.get('feelslikemax'),
                                feels_like_min=day_data.get('feelslikemin'),
                                dew_point=day_data.get('dew'),
                                humidity=day_data.get('humidity'),
                                wind_speed=day_data.get('windspeed'),
                                wind_gust=day_data.get('windgust'),
                                wind_dir=day_data.get('winddir'),
                                precipitation=day_data.get('precip'),
                                precip_cover=day_data.get('precipcover'),
                                barometric_pressure=day_data.get('pressure'),
                                sea_level_pressure=day_data.get('sealevelpressure'),
                                cloud_cover=day_data.get('cloudcover'),
                                visibility=day_data.get('visibility'),
                                uv_index=day_data.get('uvindex'),
                                solar_radiation=day_data.get('solarradiation'),
                                solar_energy=day_data.get('solarenergy')
                            )

                            results.append({
                                "station": name,
                                "date": date_obj,
                                "status": "Created",
                                "temperature": weather.temperature,
                                "temp_max": weather.temp_max,
                                "temp_min": weather.temp_min,
                                "feels_like": weather.feels_like,
                                "feels_like_max": weather.feels_like_max,
                                "feels_like_min": weather.feels_like_min,
                                "dew_point": weather.dew_point,
                                "humidity": weather.humidity,
                                "wind_speed": weather.wind_speed,
                                "wind_gust": weather.wind_gust,
                                "wind_dir": weather.wind_dir,
                                "precipitation": weather.precipitation,
                                "precip_cover": weather.precip_cover,
                                "barometric_pressure": weather.barometric_pressure,
                                "sea_level_pressure": weather.sea_level_pressure,
                                "cloud_cover": weather.cloud_cover,
                                "visibility": weather.visibility,
                                "uv_index": weather.uv_index,
                                "solar_radiation": weather.solar_radiation,
                                "solar_energy": weather.solar_energy
                            })
                        else:
                            results.append({
                                "station": name,
                                "date": date_obj,
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
                        "status": "No daily data available"
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
