from django.urls import path
from .views import WeatherView, WeatherDataListView

urlpatterns = [
    path('weather/fetch/', WeatherView.as_view(), name='fetch_weather'),
    path('weather/data/', WeatherDataListView.as_view(), name='weather_data'),
]
