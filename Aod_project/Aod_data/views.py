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
        base_nc_folder_path = os.path.join(settings.BASE_DIR, 'Aod_data/aod-file')

        if not os.path.exists(base_nc_folder_path):
            return Response(
                {"error": f"Folder {base_nc_folder_path} tidak ditemukan."},
                status=status.HTTP_404_NOT_FOUND
            )

        geotiff_folder = os.path.join(settings.MEDIA_ROOT, 'geotiff_files')
        if not os.path.exists(geotiff_folder):
            os.makedirs(geotiff_folder)

        processed_files = []
        errors = []

        # Pisahkan pemrosesan untuk VIIRS
        for satellite_folder_name in os.listdir(base_nc_folder_path):
            satellite_folder_path = os.path.join(base_nc_folder_path, satellite_folder_name)

            if not os.path.isdir(satellite_folder_path):
                continue  # Skip kalau bukan folder

            try:
                sattellite, _ = Sattellite.objects.get_or_create(sattelite_name=satellite_folder_name)

                # Hanya untuk VIIRS
                if "VIIRS" in satellite_folder_name:
                    for nc_file_name in os.listdir(satellite_folder_path):
                        if nc_file_name.endswith('.nc'):
                            nc_file_path = os.path.join(satellite_folder_path, nc_file_name)
                            geotiff_file_path = os.path.join(geotiff_folder, f"{satellite_folder_name}_{nc_file_name.replace('.nc', '.tif')}")

                            try:
                                latitude, longitude, aod_values = convert_to_geoTiFF_input_data(nc_file_path, geotiff_file_path)
                                print(f"Longitude shape (VIIRS): {longitude.shape}")
                                print(f"Latitude shape (VIIRS): {latitude.shape}")
                                
                                dataraster = []

                                # Proses data VIIRS
                                for i in range(latitude.shape[0]):
                                    for j in range(longitude.shape[1]):  # Memperbaiki akses dimensi longitude
                                        # Mengambil elemen tunggal dari array untuk latitude, longitude, dan aod_values
                                        lat_value = float(latitude[i, j]) if latitude.ndim == 2 else float(latitude[i])
                                        lon_value = float(longitude[i, j]) if longitude.ndim == 2 else float(longitude[i])
                                        aod_value = float(aod_values[i, j]) if aod_values.ndim == 2 else float(aod_values[i])

                                        dataraster.append({
                                            "latitude": lat_value,
                                            "longitude": lon_value,
                                            "aod_values": aod_value
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

                                if os.path.exists(geotiff_file_path):
                                    os.remove(geotiff_file_path)
                                    print(f"File {geotiff_file_path} berhasil dihapus.")

                                processed_files.append(f"{satellite_folder_name}/{nc_file_name}")

                            except Exception as e:
                                errors.append({f"{satellite_folder_name}/{nc_file_name}": str(e)})

                # Pemrosesan untuk Himawari
                elif "Himawari" in satellite_folder_name:
                    for nc_file_name in os.listdir(satellite_folder_path):
                        if nc_file_name.endswith('.nc'):
                            nc_file_path = os.path.join(satellite_folder_path, nc_file_name)
                            geotiff_file_path = os.path.join(geotiff_folder, f"{satellite_folder_name}_{nc_file_name.replace('.nc', '.tif')}")

                            try:
                                latitude, longitude, aod_values = convert_to_geoTiFF_input_data(nc_file_path, geotiff_file_path)
                                print(f"Longitude shape (Himawari): {longitude.shape}")
                                print(f"Latitude shape (Himawari): {latitude.shape}")

                                dataraster = []

                                # Proses data Himawari
                                for i in range(latitude.shape[0]):
                                    for j in range(longitude.shape[0]):  # Memperbaiki akses dimensi longitude
                                        # Mengambil elemen tunggal dari array untuk latitude, longitude, dan aod_values
                                        lat_value = float(latitude[i, j]) if latitude.ndim == 2 else float(latitude[i])
                                        lon_value = float(longitude[i, j]) if longitude.ndim == 2 else float(longitude[i])
                                        aod_value = float(aod_values[i, j]) if aod_values.ndim == 2 else float(aod_values[i])

                                        dataraster.append({
                                            "latitude": lat_value,
                                            "longitude": lon_value,
                                            "aod_values": aod_value
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

                                if os.path.exists(geotiff_file_path):
                                    os.remove(geotiff_file_path)
                                    print(f"File {geotiff_file_path} berhasil dihapus.")

                                processed_files.append(f"{satellite_folder_name}/{nc_file_name}")

                            except Exception as e:
                                errors.append({f"{satellite_folder_name}/{nc_file_name}": str(e)})

            except Exception as e:
                errors.append({satellite_folder_name: str(e)})

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

            file_buffer.seek(0)
            response = HttpResponse(file_buffer, content_type='image/tiff')
            response['Content-Disposition'] = 'attachment; filename="raster_latest.tif"'

            return response

        except RasterData.DoesNotExist:
            return HttpResponse("Data raster tidak ditemukan.", status=404)
        except Exception as e:
            return HttpResponse(f"Error: {str(e)}", status=500)