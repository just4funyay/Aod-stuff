from django.urls import path
from .views import GetDataPolygon

urlpatterns = [
    #path('input-himawari/', InputHimawariView.as_view(), name='InputDatabase'),
    #path('input-viirs/', InputVIIRSView.as_view(), name='InputDatabase'),
    path('get-data-aod/', GetDataPolygon.as_view(), name='raster_tile'),
    #path('get-data-pm25/', PM25GeoTIFFLatestDownloadView.as_view(), name='raster_tile'),
    
]
