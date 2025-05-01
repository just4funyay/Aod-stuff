from django.urls import path
from .views import WeatherDataListView, WeatherFetchView

urlpatterns = [
    path('weather/fetch/', WeatherFetchView.as_view(), name='fetch_weather'),
    path('weather/data/', WeatherDataListView.as_view(), name='weather_data'),
]
