import requests
from datetime import datetime
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.contrib.gis.geos import Point
from .models import WeatherData,WeatherStation,pm25DataActual,pm25DataPrediction
from .serializers import WeatherDataSerializer,pm25DataActualSerializer,WeatherDateInputSerializer,PM25DateInputSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class LatestWeatherData(APIView):
    @swagger_auto_schema(
        operation_summary="Ambil Data Cuaca Hari Ini",
        operation_description="Mengembalikan data cuaca berdasarkan tanggal hari ini.",
        responses={
            200: WeatherDataSerializer(many=True),
            404: openapi.Response(description="Tidak ada data cuaca untuk tanggal hari ini."),
        }
    )
    def get(self, request):
        today = date.today()
        weather_data = WeatherData.objects.filter(date=today)
        if not weather_data.exists():
            return Response(
                {"message": f"Tidak ada data cuaca untuk tanggal {today}."},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = WeatherDataSerializer(weather_data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class WeatherDataByDate(APIView):
    @swagger_auto_schema(
        operation_summary="Ambil Data Cuaca Berdasarkan Tanggal",
        operation_description="Mengembalikan data cuaca berdasarkan tanggal yang diberikan dalam format YYYY-MM-DD.",
        request_body=WeatherDateInputSerializer,
        responses={
            200: WeatherDataSerializer(many=True),
            400: openapi.Response(description="Input tanggal tidak valid."),
            404: openapi.Response(description="Tidak ada data cuaca untuk tanggal yang diminta."),
        }
    )
    def post(self, request):
        serializer = WeatherDateInputSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        input_date = serializer.validated_data['date']
        weather_data = WeatherData.objects.filter(date=input_date)
        if not weather_data.exists():
            return Response(
                {"message": f"Tidak ada data cuaca untuk tanggal {input_date}."},
                status=status.HTTP_404_NOT_FOUND
            )

        result_serializer = WeatherDataSerializer(weather_data, many=True)
        return Response(result_serializer.data, status=status.HTTP_200_OK)


class LatestPM25ActualView(APIView):
    @swagger_auto_schema(
        operation_summary="Ambil Data PM2.5 Aktual Hari Ini",
        operation_description="Mengembalikan data PM2.5 aktual dari seluruh stasiun untuk tanggal hari ini.",
        responses={
            200: pm25DataActualSerializer(many=True),
            404: openapi.Response(description="Tidak ada data PM2.5 untuk tanggal hari ini."),
        }
    )
    def get(self, request):
        today = date.today()
        data_today = pm25DataActual.objects.select_related('station').filter(date=today)
        if not data_today.exists():
            return Response(
                {"message": f"Tidak ada data PM2.5 untuk tanggal {today}."},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = pm25DataActualSerializer(data_today, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class PM25ActualByDate(APIView):
    @swagger_auto_schema(
        operation_summary="Ambil Data PM2.5 Aktual Berdasarkan Tanggal",
        operation_description="Mengembalikan data PM2.5 aktual berdasarkan tanggal yang diberikan dalam format YYYY-MM-DD.",
        request_body=PM25DateInputSerializer,
        responses={
            200: pm25DataActualSerializer(many=True),
            400: openapi.Response(description="Input tanggal tidak valid."),
            404: openapi.Response(description="Tidak ada data PM2.5 untuk tanggal yang diminta."),
        }
    )
    def post(self, request):
        serializer = PM25DateInputSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        input_date = serializer.validated_data['date']
        data = pm25DataActual.objects.select_related('station').filter(date=input_date)

        if not data.exists():
            return Response(
                {"message": f"Tidak ada data PM2.5 untuk tanggal {input_date}."},
                status=status.HTTP_404_NOT_FOUND
            )

        result_serializer = pm25DataActualSerializer(data, many=True)
        return Response(result_serializer.data, status=status.HTTP_200_OK)

class AddWeatherStations(APIView):
    def get(self, request, *args, **kwargs):
        locations = {
            'us_embassy_1': (-6.1811056, 106.8279877),
            'us_embassy_2': (-6.236658728205383, 106.79319751533286),
            'jakarta_gbk': (-6.2155, 106.803),
            'bundaran_hi': (-6.19466, 106.8235),
            'kelapa_gading': (-6.1535777, 106.910887),
            'jagakarsa': (-6.35693, 106.80367),
            'lubang_buaya': (-6.28889, 106.90919),
            'kebun_jeruk': (-6.20737, 106.7525)
        }

        # Menambahkan stasiun cuaca
        for station_name, coords in locations.items():
            lat, lon = coords
            point = Point(lon, lat)  

            # Menyimpan data ke model WeatherStation
            WeatherStation.objects.create(name=station_name, location=point)

        return Response({"message": "Weather stations added successfully!"}, status=status.HTTP_201_CREATED)
    
from datetime import date, timedelta, datetime

class WeatherFetchViewRange(APIView):
    def get(self, request):
        results = []
        stations = WeatherStation.objects.all()

        end_date = date.today()
        start_date = end_date - timedelta(days=7) 

        for station in stations:
            lat = station.location.y
            lon = station.location.x
            name = station.name

            url = f"{BASE_URL}{lat},{lon}/{start_date}/{end_date}?unitGroup=metric&key={API_KEY}&include=days"
            response = requests.get(url)

            if response.status_code == 200:
                data = response.json()
                days = data.get('days', [])

                for day_data in days:
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
                                "status": "Created"
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
                    "error": f"Failed to fetch: {response.status_code}"
                })

        return Response(results, status=status.HTTP_200_OK)
