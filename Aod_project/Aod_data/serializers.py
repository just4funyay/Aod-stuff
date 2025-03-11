from rest_framework_gis.serializers import GeoFeatureModelSerializer
from .models import RasterData

class RasterDataSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = RasterData
        fields = '__all__'
