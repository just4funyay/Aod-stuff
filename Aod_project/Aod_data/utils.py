import os
import xarray as xr
import rasterio
from rasterio.transform import from_bounds
import numpy as np
from django.contrib.gis.gdal import GDALRaster 

def convert_to_geoTiFF_input_data(nc_file_path, geotiff_file_path):
    ds = xr.open_dataset(nc_file_path,decode_timedelta=False)

    # Ambil variabel data
    latitude = ds['Latitude'].values
    longitude = ds['Longitude'].values
    aod = ds['Aerosol_Optical_Thickness_550_Land_Ocean_Best_Estimate'].values

    # Ganti NaN dengan 0 untuk validasi nilai AOD
    aod = np.where(np.isnan(aod), -9999, aod)

    # Mask untuk memilih data dalam batas region
    #lat_min, lat_max, lon_min, lon_max = -6.5, -6.08, 106.6, 107.0
    #mask_region = (latitude >= lat_min) & (latitude <= lat_max) & (longitude >= lon_min) & (longitude <= lon_max)
    #aod_filtered = np.full(aod.shape, 0, dtype=np.float32)
    #aod_filtered[mask_region] = aod_valid[mask_region]

    
    # Pastikan bounding box sesuai transform
    transform_region = from_bounds(
        longitude.min(), latitude.min(),  # xmin, ymin
        longitude.max(), latitude.max(),  # xmax, ymax
        longitude.shape[1], latitude.shape[0]
    )
    aod = np.flipud(aod)
    aod = np.fliplr(aod)

    # Simpan ke GeoTIFF
    with rasterio.open(
        geotiff_file_path, 'w', driver='GTiff',
        height=latitude.shape[0], width=longitude.shape[1],
        count=1, dtype=rasterio.float32,
        crs="EPSG:4326", transform=transform_region,
        nodata=0
    ) as dst:
        dst.write(aod, 1)

    return latitude,longitude,aod