from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import os
from django.conf import settings
from .utils import convert_to_geoTiFF_input_data
from .models import RasterData, Sattellite 
from django.contrib.gis.gdal import GDALRaster
from datetime import date
import gc
import json
from django.http import HttpResponse,FileResponse
import rasterio
from io import BytesIO
import psycopg2
from django.utils.timezone import now
from .serializers import RasterDataSerializer


class InputDatabase(APIView):
    def get(self, request):
        today = date.today()
        nc_folder_path = os.path.join(settings.BASE_DIR, 'Aod_data/aod-file')

        if not os.path.exists(nc_folder_path):
            return Response(
                {"error": f"Folder {nc_folder_path} tidak ditemukan."},
                status=status.HTTP_404_NOT_FOUND
            )

        geotiff_folder = os.path.join(settings.MEDIA_ROOT, 'geotiff_files')
        if not os.path.exists(geotiff_folder):
            os.makedirs(geotiff_folder)

        processed_files = []
        errors = []

        # Pastikan ada satelit sebelum menyimpan data raster
        sattellite_name = "VIIRS"  # Ganti sesuai kebutuhan
        sattellite, _ = Sattellite.objects.get_or_create(sattelite_name=sattellite_name)

        # Iterasi semua file .nc dalam folder
        for nc_file_name in os.listdir(nc_folder_path):
            if nc_file_name.endswith('.nc'):
                nc_file_path = os.path.join(nc_folder_path, nc_file_name)
                geotiff_file_path = os.path.join(geotiff_folder, nc_file_name.replace('.nc', '.tif'))

                try:
                    latitude, longitude, aod_values = convert_to_geoTiFF_input_data(nc_file_path, geotiff_file_path)
                    dataraster = []

                    for i in range(latitude.shape[0]):  
                        for j in range(latitude.shape[1]):  
                            dataraster.append({
                                "latitude": float(latitude[i, j]),   # Mengakses elemen (i, j)
                                "longitude": float(longitude[i, j]),
                                "aod_values": float(aod_values[i, j])
                            })

                    raster = GDALRaster(geotiff_file_path, write=True)
                    raster_data = RasterData(
                        sattellite=sattellite,  
                        raster=raster,
                        data=dataraster,
                        time_retrieve=today
                    )
                    raster_data.save()
                    raster = None

                    gc.collect()

                    # Hapus file setelah diproses
                    if os.path.exists(geotiff_file_path):
                        os.remove(geotiff_file_path)
                        print(f"File {geotiff_file_path} berhasil dihapus.")

                    processed_files.append(nc_file_name)
                except Exception as e:
                    errors.append({nc_file_name: str(e)})

        return Response(
            {
                "processed_files": processed_files,
                "errors": errors if errors else "Semua file berhasil diproses."
            },
            status=status.HTTP_200_OK if not errors else status.HTTP_206_PARTIAL_CONTENT
        )

class GetRasterDataView(APIView):
    def get(self, request):
        try:
            raster_data = RasterData.objects.latest('pk')
            gdal_raster = raster_data.raster
            file_buffer = BytesIO()
            transform = rasterio.transform.from_origin(
                gdal_raster.origin.x, gdal_raster.origin.y, gdal_raster.scale.x, gdal_raster.scale.y
            )

            with rasterio.open(
                file_buffer, 'w',
                driver='GTiff',
                width=gdal_raster.width,
                height=gdal_raster.height,
                count=1,
                dtype=gdal_raster.bands[0].data().dtype.name,
                crs=gdal_raster.srs.wkt,
                transform=transform
            ) as dst:
                dst.write(gdal_raster.bands[0].data(), 1)

            # Kembalikan file sebagai response download
            file_buffer.seek(0)
            response = HttpResponse(file_buffer, content_type='image/tiff')
            response['Content-Disposition'] = 'attachment; filename="raster_latest.tif"'

            return response

        except RasterData.DoesNotExist:
            return HttpResponse("Data raster tidak ditemukan.", status=404)
        except Exception as e:
            return HttpResponse(f"Error: {str(e)}", status=500)