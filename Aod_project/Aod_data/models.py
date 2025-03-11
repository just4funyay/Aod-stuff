from django.contrib.gis.db import models

class Sattellite(models.Model):
    id = models.AutoField(primary_key=True)
    sattelite_name = models.CharField(max_length=255)  

    def __str__(self):
        return self.sattelite_name

class RasterData(models.Model):
    id = models.AutoField(primary_key=True)
    sattellite = models.ForeignKey(Sattellite, on_delete=models.CASCADE, null=True, blank=True, related_name="raster_data")
    data = models.JSONField()
    raster = models.RasterField(help_text="Data raster GeoTIFF yang disimpan dalam PostGIS")
    time_retrieve = models.DateField()

    def __str__(self):
        return f"{self.sattellite.sattelite_name} - {self.time_retrieve}"
