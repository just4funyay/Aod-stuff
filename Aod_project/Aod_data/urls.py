from django.urls import path
from .views import InputDatabase,GetRasterDataView,PM25GeoTIFFLatestDownloadView

urlpatterns = [
    path('inpudatabase/', InputDatabase.as_view(), name='InputDatabase'),
    path('get-data-aod/', GetRasterDataView.as_view(), name='raster_tile'),
    path('get-data-pm25/', PM25GeoTIFFLatestDownloadView.as_view(), name='raster_tile'),
]
