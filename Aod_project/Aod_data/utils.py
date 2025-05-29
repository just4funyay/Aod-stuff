import os
import math
import gc
from datetime import date, datetime

import numpy as np
import xarray as xr
import rasterio
from rasterio.transform import from_bounds
import rioxarray
import geopandas as gpd
from shapely.geometry import box, MultiPolygon
from shapely.ops import unary_union

from django.conf import settings
from django.contrib.gis.gdal import GDALRaster 
from django.contrib.gis.geos import GEOSGeometry

from rest_framework.response import Response
from rest_framework import status

from Aod_data.models import Sattellite, RasterData, Polygondata


def convert_to_geoTiFF_input_data(nc_file_path, geotiff_file_path, geojson_filepath):
    print(nc_file_path)
    ds = xr.open_dataset(nc_file_path, decode_timedelta=False)
    folder_name = os.path.basename(os.path.dirname(nc_file_path))
    print(folder_name)
    # Batas wilayah Jakarta
    lat_min, lat_max = -6.5, -6.08
    lon_min, lon_max = 106.6, 107.0

    if folder_name == 'VIIRS':
        # Ambil data koordinat dan AOD
        lat = ds['Latitude'].values
        lon = ds['Longitude'].values
        aod = ds['Aerosol_Optical_Thickness_550_Land_Ocean_Best_Estimate'].values
        
        aod = np.where(np.isnan(aod), -9999, aod)
        # Masking wilayah Jakarta
        mask = (
            (lat >= lat_min) & (lat <= lat_max) &
            (lon >= lon_min) & (lon <= lon_max)
        )
        aod_filtered = np.full(aod.shape, 0, dtype=np.float32)
        aod_filtered[mask] = aod[mask]
        #print(aod_filtered)

        transform_region = from_bounds(
        lon.min(), lat.min(),  # xmin, ymin
        lon.max(), lat.max(),  # xmax, ymax
        lon.shape[1], lat.shape[0]
    )
        aod = np.flipud(aod_filtered)
        aod = np.fliplr(aod)

        # Tulis CRS dan simpan sebagai GeoTIFF
        #aod_filtered = aod_filtered.rio.write_crs("EPSG:4326", inplace=False)
        #aod_filtered.rio.to_raster(geotiff_file_path)

        return lat, lon, aod

    elif folder_name == 'Himawari':
        # Subset data Jakarta
        # Batas wilayah Jakarta
        lat_min, lat_max = -6.5, -6.08
        lon_min, lon_max = 106.6, 107.0
        ds_subset = ds.sel(
            latitude=slice(lat_max, lat_min),
            longitude=slice(lon_min, lon_max)
        )
        print(ds_subset)
        if 'AOT_L2_Mean' not in ds_subset:
            raise ValueError("Data 'AOT_L2_Mean' tidak ditemukan dalam file.")
        
        aod = ds_subset['AOT_L2_Mean']
        latitude = ds_subset['latitude'].values
        longitude = ds_subset['longitude'].values
        aod_vals = aod.values

        jakarta = gpd.read_file(geojson_filepath).to_crs("EPSG:4326")

        lat_res = 0.05
        lon_res = 0.05

        records = []
        for i, lat in enumerate(latitude):
            for j, lon in enumerate(longitude):
                val = aod_vals[i, j]
                if not np.isnan(val):
                    grid_cell = box(
                        lon - lon_res / 2, lat - lat_res / 2,
                        lon + lon_res / 2, lat + lon_res / 2
                    )
                    records.append({'geometry': grid_cell, 'aod': float(val)})
        
        
        gdf = gpd.GeoDataFrame(records, crs="EPSG:4326")
        clipped_gdf = gpd.clip(gdf, jakarta)
        
        # Simpan sebagai GeoTIFF
        #aod_raster = aod.rio.write_crs("EPSG:4326")
        #aod_raster.rio.to_raster(geotiff_file_path)

        return latitude, longitude, aod_vals, clipped_gdf

    else:
        raise ValueError(f"Folder '{folder_name}' tidak dikenali sebagai 'VIIRS' atau 'Himawari'.")
    
"""
UNTUK PROCESSING SATELIT HIMAWARI

"""

def process_himawari_data():
    base_nc_folder_path = os.path.join(settings.BASE_DIR, 'Aod_data/aod-file/Himawari')

    if not os.path.exists(base_nc_folder_path):
        return {"error": f"Folder {base_nc_folder_path} tidak ditemukan."}, status.HTTP_404_NOT_FOUND

    jakarta_geojson = os.path.join(settings.BASE_DIR, 'id-jk.geojson')
    geotiff_folder = os.path.join(settings.MEDIA_ROOT, 'geotiff_files')
    if not os.path.exists(geotiff_folder):
        os.makedirs(geotiff_folder)

    processed_files = []
    errors = []

    try:
        sattellite, _ = Sattellite.objects.get_or_create(sattelite_name='Himawari')

        for nc_file_name in os.listdir(base_nc_folder_path):
            if nc_file_name.endswith('.nc'):
                nc_file_path = os.path.join(base_nc_folder_path, nc_file_name)
                filename_parts = nc_file_name.split('_')
                date_str = filename_parts[1]
                file_date = datetime.strptime(date_str, "%Y%m%d").date()
                geotiff_file_path = os.path.join(geotiff_folder, f"Himawari_{nc_file_name.replace('.nc', '.tif')}")

                try:
                    latitude, longitude, aod_values, clipped_gdf = convert_to_geoTiFF_input_data(nc_file_path, geotiff_file_path, jakarta_geojson)
                    dataraster = []
                    for i in range(latitude.shape[0]):
                        for j in range(longitude.shape[0]):
                            lat_value = float(latitude[i])
                            lon_value = float(longitude[j])
                            aod_value = float(aod_values[i, j])
                            if math.isnan(aod_value):
                                aod_value = 0.0

                            dataraster.append({
                                "latitude": lat_value,
                                "longitude": lon_value,
                                "aod_values": aod_value
                            })
                    print(dataraster)
                    raster_data = RasterData.objects.create(
                        sattellite=sattellite,
                        data=dataraster,
                        time_retrieve=file_date,
                    )

                    for _, row in clipped_gdf.iterrows():
                        geom = row.geometry
                        if geom.geom_type == 'MultiPolygon':
                            for poly in geom.geoms:
                                polygon = GEOSGeometry(poly.wkt, srid=4326)
                                
                                Polygondata.objects.create(
                                    aodid=raster_data,
                                    geom=polygon,
                                    aod_value=row['aod'],
                                    date=raster_data.time_retrieve
                                )
                        else:
                            polygon = GEOSGeometry(geom.wkt, srid=4326)
                            
                            Polygondata.objects.create(
                                aodid=raster_data,
                                geom=polygon,
                                aod_value=row['aod'],
                                date=raster_data.time_retrieve
                            )

                    if os.path.exists(geotiff_file_path):
                        os.remove(geotiff_file_path)

                    if os.path.exists(nc_file_path):
                       os.remove(nc_file_path)

                    processed_files.append(nc_file_name)

                except Exception as e:
                    errors.append({nc_file_name: str(e)})

    except Exception as e:
        errors.append({"Himawari": str(e)})

    return {"processed_files": processed_files, "errors": errors if errors else "Semua file Himawari berhasil diproses."}, \
           status.HTTP_200_OK if not errors else status.HTTP_206_PARTIAL_CONTENT


"""
UNTUK PROCESSING SATELIT VIIRS, BELUM ADA FITUR POLIGON

"""


def process_viirs_files():
    today = date.today()
    base_nc_folder_path = os.path.join(settings.BASE_DIR, 'Aod_data/aod-file/VIIRS')
    jakarta_geojson = os.path.join(settings.BASE_DIR, 'id-jk.geojson')
    geotiff_folder = os.path.join(settings.MEDIA_ROOT, 'geotiff_files')

    if not os.path.exists(base_nc_folder_path):
        return {
            "processed_files": [],
            "errors": [f"Folder {base_nc_folder_path} tidak ditemukan."]
        }

    if not os.path.exists(geotiff_folder):
        os.makedirs(geotiff_folder)

    processed_files = []
    errors = []

    try:
        sattellite, _ = Sattellite.objects.get_or_create(sattelite_name='VIIRS')

        for nc_file_name in os.listdir(base_nc_folder_path):
            if nc_file_name.endswith('.nc'):
                nc_file_path = os.path.join(base_nc_folder_path, nc_file_name)
                geotiff_file_path = os.path.join(geotiff_folder, f"VIIRS_{nc_file_name.replace('.nc', '.tif')}")

                try:
                    latitude, longitude, aod_values = convert_to_geoTiFF_input_data(
                        nc_file_path, geotiff_file_path, jakarta_geojson
                    )
                    print(f"Longitude shape (VIIRS): {longitude.shape}")
                    print(f"Latitude shape (VIIRS): {latitude.shape}")

                    dataraster = []
                    for i in range(latitude.shape[0]):
                        for j in range(latitude.shape[1]):
                            lat_value = float(latitude[i, j])
                            lon_value = float(longitude[i, j])
                            aod_value = float(aod_values[i, j])
                            if math.isnan(aod_value):
                                aod_value = 0.0
                            dataraster.append({
                                "latitude": lat_value,
                                "longitude": lon_value,
                                "aod_values": aod_value
                            })

                    raster_data = RasterData(
                        sattellite=sattellite,
                        data=dataraster,
                        time_retrieve=today
                    )
                    raster_data.save()

                    gc.collect()

                    if os.path.exists(geotiff_file_path):
                        os.remove(geotiff_file_path)
                        print(f"File {geotiff_file_path} berhasil dihapus.")

                    if os.path.exists(nc_file_path):
                        os.remove(nc_file_path)
                        print(f"File {nc_file_path} berhasil dihapus.")

                    processed_files.append(nc_file_name)

                except Exception as e:
                    errors.append({nc_file_name: str(e)})

    except Exception as e:
        errors.append({"VIIRS": str(e)})

    return {
        "processed_files": processed_files,
        "errors": errors if errors else "Semua file VIIRS berhasil diproses."
    }