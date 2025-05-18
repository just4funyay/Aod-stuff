from django.urls import path
from .views import GetDataPolygon,GetDataPolygonPM25,PolygonByDateAPIView,PolygonPM25ByDateAPIView

urlpatterns = [
    path('get-data-aod/', GetDataPolygon.as_view(http_method_names=['get']), name='aod-polygon'),
    path('get-data-pm25/', GetDataPolygonPM25.as_view(http_method_names=['get']), name='pm25-polygon'),
    path('get-data-aodbydate/', PolygonByDateAPIView.as_view(http_method_names=['post']), name="aodbydate"),
    path('get-data-pm25bydate/', PolygonPM25ByDateAPIView.as_view(http_method_names=['post']), name="pm25bydate")
]
