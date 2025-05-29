from datetime import date, timedelta
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Polygondata,PolygondataPM25
from django.core.serializers import serialize
import json
from datetime import datetime
from .serializers import DateInputSerializer
from drf_yasg.utils import swagger_auto_schema

class GetDataPolygon(APIView):
    @swagger_auto_schema(
        operation_description="Mengambil data polygon AOD (Aerosol Optical Depth) untuk hari ini.",
        responses={200: "Berhasil", 404: "Data tidak ditemukan", 500: "Kesalahan server"}
    )
    def get(self, request):
        try:
            yesterday = date.today() - timedelta(days=1)
            polygons = Polygondata.objects.filter(date=yesterday)
            if not polygons.exists():
                return Response(
                    {"message": "Tidak ada data polygon untuk tanggal kemarin."},
                    status=status.HTTP_404_NOT_FOUND
                )

            serializer = serialize("geojson", polygons, geometry_field="geom", fields=["aod_value"])
            data = json.loads(serializer)
            return Response(data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PolygonByDateAPIView(APIView):
   
    @swagger_auto_schema(
        request_body=DateInputSerializer,
        operation_description="Mengambil data polygon AOD berdasarkan tanggal tertentu yang dikirim dalam request body.",
        responses={200: "Berhasil", 404: "Data tidak ditemukan", 400: "Input tidak valid"}
    )
    def post(self, request):
        serializer = DateInputSerializer(data=request.data)
        if serializer.is_valid():
            tanggal = serializer.validated_data['tanggal']
            polygons = Polygondata.objects.filter(date=tanggal)
            if not polygons.exists():
                return Response(
                    {"message": "Tidak ada data polygon untuk tanggal tersebut."},
                    status=status.HTTP_404_NOT_FOUND
                )
            geojson_data = serialize("geojson", polygons, geometry_field="geom", fields=["aod_value"])
            data = json.loads(geojson_data)
            return Response(data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
class GetDataPolygonPM25(APIView):
    @swagger_auto_schema(
        operation_description="Mengambil data polygon PM2.5 untuk hari ini.",
        responses={200: "Berhasil", 404: "Data tidak ditemukan", 500: "Kesalahan server"}
    )
    def get(self, request):
        try:
            yesterday = date.today() - timedelta(days=1)
            polygons = PolygondataPM25.objects.filter(date=yesterday)
            if not polygons.exists():
                return Response(
                    {"message": "Tidak ada data polygon untuk tanggal kemarin."},
                    status=status.HTTP_404_NOT_FOUND
                )

            serializer = serialize("geojson", polygons, geometry_field="geom", fields=["pm25_value"])
            data = json.loads(serializer)
            return Response(data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class PolygonPM25ByDateAPIView(APIView):
    @swagger_auto_schema(
        request_body=DateInputSerializer,
        operation_description="Mengambil data polygon PM2.5 berdasarkan tanggal tertentu yang dikirim dalam request body.",
        responses={200: "Berhasil", 404: "Data tidak ditemukan", 400: "Input tidak valid"}
    )
    def post(self, request):
        serializer = DateInputSerializer(data=request.data)
        if serializer.is_valid():
            tanggal = serializer.validated_data['tanggal']
            polygons = PolygondataPM25.objects.filter(date=tanggal)
            if not polygons.exists():
                return Response(
                    {"message": "Tidak ada data polygon untuk tanggal tersebut."},
                    status=status.HTTP_404_NOT_FOUND
                )
            geojson_data = serialize("geojson", polygons, geometry_field="geom", fields=["pm25_value"])
            data = json.loads(geojson_data)
            return Response(data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
