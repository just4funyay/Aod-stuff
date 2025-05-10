from django.urls import path
from .views import GetRasterDataView,PM25GeoTIFFLatestDownloadView,InputHimawariView,InputVIIRSView

urlpatterns = [
    path('input-himawari/', InputHimawariView.as_view(), name='InputDatabase'),
    path('input-viirs/', InputVIIRSView.as_view(), name='InputDatabase'),
    path('get-data-aod/', GetRasterDataView.as_view(), name='raster_tile'),
    path('get-data-pm25/', PM25GeoTIFFLatestDownloadView.as_view(), name='raster_tile'),
]
