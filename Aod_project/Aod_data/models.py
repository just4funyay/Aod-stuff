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
    #raster = models.RasterField(help_text="Data raster GeoTIFF yang disimpan dalam PostGIS")
    time_retrieve = models.DateField()

    def __str__(self):
        return f"{self.sattellite.sattelite_name} - {self.time_retrieve}"
    
class Polygondata(models.Model):
    aodid = models.ForeignKey(RasterData, on_delete=models.CASCADE, related_name='aod_polygon')
    geom = models.PolygonField()
    aod_value = models.FloatField()
    date = models.DateField()

    def __str__(self):
        return f"{self.aodid}"


class pm25DataEstimate(models.Model):
    aodid = models.ForeignKey(RasterData, on_delete=models.CASCADE, related_name='pm25data_estimate')
    valuepm25 = models.JSONField()
    #raster = models.RasterField(null=True, blank=True)
    time = models.DateField()

class PolygondataPM25(models.Model):
    pm25id = models.ForeignKey(pm25DataEstimate, on_delete=models.CASCADE, related_name='pm25_polygon')
    geom = models.PolygonField()
    pm25_value = models.FloatField()
    date = models.DateField()

    def __str__(self):
        return f"{self.pm25id}"
