from django.contrib.gis.db import models

class WeatherStation(models.Model):
    name = models.CharField(max_length=255)
    location = models.PointField()  # Menyimpan titik (latitude, longitude)

    def __str__(self):
        return self.name

class WeatherData(models.Model):
    station = models.ForeignKey(WeatherStation, on_delete=models.CASCADE, related_name='weather_data')
    date = models.DateField()
    temperature = models.FloatField(null=True, blank=True)  
    humidity = models.FloatField(null=True, blank=True)  
    wind_speed = models.FloatField(null=True, blank=True)  
    precipitation = models.FloatField(null=True, blank=True)  
    barometric_pressure = models.FloatField(null=True, blank=True) 
    def __str__(self):
        return f"{self.station.name} - {self.timestamp}"
    
class pm25DataActual(models.Model):
    station = models.ForeignKey(WeatherStation, on_delete=models.CASCADE, related_name='pm25data_actual')
    pm25_value = models.FloatField(null=True, blank=True)

class pm25DataPrediction(models.Model):
    station = models.ForeignKey(WeatherStation, on_delete=models.CASCADE, related_name='pm25data_prediction')
    date = models.DateField()
    pm25_value = models.FloatField(null=True, blank=True)

