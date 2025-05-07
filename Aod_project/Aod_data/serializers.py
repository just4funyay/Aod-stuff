from rest_framework_gis.serializers import GeoFeatureModelSerializer
from .models import RasterData,pm25DataEstimate

class RasterDataSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = RasterData
        fields = '__all__'

class pm25DataEstimateSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = pm25DataEstimate
        fields = '__all__'
