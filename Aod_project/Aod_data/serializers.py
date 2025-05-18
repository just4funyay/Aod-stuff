from rest_framework_gis.serializers import GeoFeatureModelSerializer
from .models import RasterData,pm25DataEstimate,Polygondata
from rest_framework import serializers


class DateInputSerializer(serializers.Serializer):
    tanggal = serializers.DateField(format='%Y-%m-%d', input_formats=['%Y-%m-%d'])