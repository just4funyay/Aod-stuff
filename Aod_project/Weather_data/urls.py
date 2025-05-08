from django.urls import path
from .views import WeatherDataListView, WeatherFetchView, AddWeatherStations

urlpatterns = [
    path('weather/fetch/', WeatherFetchView.as_view(), name='fetch_weather'),
    path('weather/data/', WeatherDataListView.as_view(), name='weather_data'),
    path('weather/add/', AddWeatherStations.as_view(), name='weather_data'),
]
