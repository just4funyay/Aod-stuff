from django.urls import path
from .views import InputDatabase,GetRasterDataView

urlpatterns = [
    path('inpudatabase/', InputDatabase.as_view(), name='InputDatabase'),
     path('get-data/', GetRasterDataView.as_view(), name='raster_tile'),
]
