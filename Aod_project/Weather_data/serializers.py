from rest_framework import serializers
from .models import WeatherStation,WeatherData,pm25DataActual,pm25DataPrediction

class WeatherDataSerializer(serializers.ModelSerializer):   
    class Meta:
        model = WeatherData
        fields = '__all__'  

class WeatherStationSerializer(serializers.ModelSerializer):   
    class Meta:
        model = WeatherStation
        fields = '__all__'

class pm25DataActualSerializer(serializers.ModelSerializer):   
    class Meta:
        model = pm25DataActual
        fields = '__all__'

class pm25DataPredictionSerializer(serializers.ModelSerializer):   
    class Meta:
        model = pm25DataPrediction
        fields = '__all__'