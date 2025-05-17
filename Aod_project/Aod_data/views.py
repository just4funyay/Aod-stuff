from datetime import date, timedelta
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Polygondata,PolygondataPM25
from .serializers import PolygondataGeoSerializer
from django.core.serializers import serialize
import json

class GetDataPolygon(APIView):
    def get(self, request):
        try:
            yesterday = date.today() - timedelta(days=1)
            polygons = Polygondata.objects.filter(date=yesterday)
            if not polygons.exists():
                return Response(
                    {"message": "Tidak ada data polygon untuk tanggal kemarin."},
                    status=status.HTTP_404_NOT_FOUND
                )

            serializer = serialize("geojson", polygons, geometry_field = "geom", fields = ["aod_value"])
            data = json.loads(serializer)
            return Response(data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class GetDataPolygonPM25(APIView):
    def get(self, request):
        try:
            yesterday = date.today() - timedelta(days=1)
            polygons = PolygondataPM25.objects.filter(date=yesterday)
            if not polygons.exists():
                return Response(
                    {"message": "Tidak ada data polygon untuk tanggal kemarin."},
                    status=status.HTTP_404_NOT_FOUND
                )

            serializer = serialize("geojson", polygons, geometry_field = "geom", fields = ["pm25_value"])
            data = json.loads(serializer)
            return Response(data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
