from rest_framework_gis.serializers import GeoFeatureModelSerializer
from .models import RasterData,pm25DataEstimate,Polygondata

class RasterDataSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = RasterData
        geo_field = 'geom'
        fields = ['geom']

class pm25DataEstimateSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = pm25DataEstimate
        fields = '__all__'
class PolygondataGeoSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = Polygondata
        geo_field = 'geom'
        fields = ('id', 'aodid', 'aod_value', 'date')