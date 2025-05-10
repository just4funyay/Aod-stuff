import os
import xarray as xr
import rasterio
from rasterio.transform import from_bounds
import numpy as np
from django.contrib.gis.gdal import GDALRaster 
import rioxarray

#NC file -> TIFF file

def convert_to_geoTiFF_input_data(nc_file_path, geotiff_file_path):
    ds = xr.open_dataset(nc_file_path, decode_timedelta=False)
    folder_name = os.path.basename(os.path.dirname(nc_file_path))

    # Batas wilayah Jakarta
    lat_min, lat_max = -6.5, -6.08
    lon_min, lon_max = 106.6, 107.0

    if folder_name == 'VIIRS':
        # Ambil data koordinat dan AOD
        lat = ds['Latitude']
        lon = ds['Longitude']
        aod = ds['Aerosol_Optical_Thickness_550_Land_Ocean_Best_Estimate']

        # Masking wilayah Jakarta
        mask = (
            (lat >= lat_min) & (lat <= lat_max) &
            (lon >= lon_min) & (lon <= lon_max)
        )
        aod_filtered = aod.where(mask)
        aod_filtered = aod_filtered.fillna(-9999)

        # Set koordinat eksplisit agar bisa diubah ke raster
        aod_filtered.coords['latitude'] = (('y', 'x'), lat.values)
        aod_filtered.coords['longitude'] = (('y', 'x'), lon.values)

        # Tulis CRS dan simpan sebagai GeoTIFF
        aod_filtered = aod_filtered.rio.write_crs("EPSG:4326", inplace=False)
        aod_filtered.rio.to_raster(geotiff_file_path)

        return lat.values, lon.values, aod_filtered

    elif folder_name == 'Himawari':
        # Subset data Jakarta
        ds_subset = ds.sel(
            latitude=slice(lat_max, lat_min),
            longitude=slice(lon_min, lon_max)
        )

        if 'AOT_L2_Mean' not in ds_subset:
            raise ValueError("Data 'AOT_L2_Mean' tidak ditemukan dalam file.")

        aod = ds_subset['AOT_L2_Mean']
        aod = aod.rio.write_crs("EPSG:4326")

        # Simpan sebagai GeoTIFF
        aod.rio.to_raster(geotiff_file_path)

        return ds_subset['latitude'].values, ds_subset['longitude'].values, aod

    else:
        raise ValueError(f"Folder '{folder_name}' tidak dikenali sebagai 'VIIRS' atau 'Himawari'.")