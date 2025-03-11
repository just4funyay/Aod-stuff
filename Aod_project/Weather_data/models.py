from django.contrib.gis.db import models

class WeatherData(models.Model):
    name_location = models.CharField(max_length=255)
    geom = models.PointField()
    datetime = models.DateTimeField()
    temperature = models.FloatField(null=True, blank=True)  
    humidity = models.FloatField(null=True, blank=True)  
    wind_speed = models.FloatField(null=True, blank=True)  
    precipitation = models.FloatField(null=True, blank=True)  
    barometric_pressure = models.FloatField(null=True, blank=True) 
    def __str__(self):
        return f"Weather in {self.location} at {self.datetime}"
