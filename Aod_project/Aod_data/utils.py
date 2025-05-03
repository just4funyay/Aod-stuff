import os
import xarray as xr
import rasterio
from rasterio.transform import from_bounds
import numpy as np
from django.contrib.gis.gdal import GDALRaster 
import rioxarray

#NC file -> TIFF file

def convert_to_geoTiFF_input_data(nc_file_path, geotiff_file_path):
    ds = xr.open_dataset(nc_file_path,decode_timedelta=False)

    # logic Viirs
    folder_name = os.path.basename(os.path.dirname(nc_file_path))
    if folder_name == 'VIIRS':
        
        latitude = ds['Latitude'].values
        longitude = ds['Longitude'].values
        aod = ds['Aerosol_Optical_Thickness_550_Land_Ocean_Best_Estimate'].values

        
        aod_valid = np.where(np.isnan(aod), -9999, aod)

        
        lat_min, lat_max, lon_min, lon_max = -6.5, -6.08, 106.6, 107.0
        mask_region = (latitude >= lat_min) & (latitude <= lat_max) & (longitude >= lon_min) & (longitude <= lon_max)
        aod_filtered = np.full(aod.shape, 0, dtype=np.float32)
        aod_filtered[mask_region] = aod_valid[mask_region]

        
        # Pastikan bounding box sesuai transform
        transform_region = from_bounds(
            longitude.min(), latitude.min(),  # xmin, ymin
            longitude.max(), latitude.max(),  # xmax, ymax
            longitude.shape[1], latitude.shape[0]
        )
        aod = np.flipud(aod_filtered)
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

    elif folder_name == 'Himawari':
        ds = xr.open_dataset(nc_file_path, decode_timedelta=False)

        # batas Jakarta
        lat_min, lat_max, lon_min, lon_max = -6.5, -6.08, 106.6, 107.0

        # Ambil nama koordinat latitude dan longitude
        lon_name = 'longitude'  # Berdasarkan struktur dataset Anda
        lat_name = 'latitude'   # Berdasarkan struktur dataset Anda

        # Subset data Jakarta
        jakarta_data = ds.sel(
            latitude=slice(lat_max, lat_min),  
            longitude=slice(lon_min, lon_max)  
        )

        # Ambil data AOT
        if 'AOT_L2_Mean' not in jakarta_data:
            raise ValueError("Data AOT_L2_Mean tidak ditemukan dalam file.")

        aod = jakarta_data['AOT_L2_Mean']

        
        latitude = jakarta_data[lat_name].values  
        longitude = jakarta_data[lon_name].values 
        
        aod = aod.rio.write_crs("EPSG:4326") 

        
        tiff_output_path = os.path.join(geotiff_file_path)
        aod.rio.to_raster(tiff_output_path)

    return latitude,longitude,aod

