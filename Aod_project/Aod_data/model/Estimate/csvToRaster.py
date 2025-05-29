import numpy as np
import xarray as xr
import rasterio
from rasterio.transform import from_origin
import geopandas as gpd
from shapely.geometry import box
import os
import sys
import django
import pandas as pd
import csv
import joblib

# Setup Django environment
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
sys.path.append(PROJECT_ROOT)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Aod_project.settings")
django.setup()

def csv_to_geotiff(dataframe, output_path):
    
    latitudes = dataframe['aod_latitude'].values
    longitudes = dataframe['aod_longitude'].values
    pm25_values = dataframe['PM2.5'].values

    latitudes_unique = np.unique(latitudes)[::-1]
    longitudes_unique = np.unique(longitudes)

    
    pm25_grid = np.full((len(latitudes_unique), len(longitudes_unique)), np.nan)

    
    for lat, lon, pm25 in zip(latitudes, longitudes, pm25_values):
        lat_idx = np.where(latitudes_unique == lat)[0][0]
        lon_idx = np.where(longitudes_unique == lon)[0][0]
        pm25_grid[lat_idx, lon_idx] = pm25

    
    data_array = xr.DataArray(
        pm25_grid,
        coords={
            'latitude': latitudes_unique,
            'longitude': longitudes_unique
        },
        dims=['latitude', 'longitude']
    )

    
    res_lat = abs(latitudes_unique[1] - latitudes_unique[0])
    res_lon = abs(longitudes_unique[1] - longitudes_unique[0])

    
    transform = from_origin(
        west=longitudes_unique.min(),
        north=latitudes_unique.max(),
        xsize=res_lon,
        ysize=res_lat
    )

    # Simpan ke GeoTIFF
    with rasterio.open(
        output_path,
        'w',
        driver='GTiff',
        height=pm25_grid.shape[0],
        width=pm25_grid.shape[1],
        count=1,
        dtype=pm25_grid.dtype,
        crs='EPSG:4326',
        transform=transform
    ) as dst:
        dst.write(pm25_grid, 1)

    print(f"GeoTIFF berhasil disimpan ke: {output_path}")
    return output_path

# csv -> polygon
def csvToPolygon(dataframe, jakarta_geojson):
    lat_res = 0.05
    lon_res = 0.05
    records = []
    for _,row in dataframe.iterrows():
        lat = row["aod_latitude"]
        lon = row["aod_longitude"]
        pm25 = row["PM2.5"]
        
        grid_cell = box(
            lon - lon_res / 2, lat - lat_res / 2,
            lon + lon_res / 2, lat + lat_res / 2
        )
        records.append({
        'geometry': grid_cell,
        'pm25': pm25
    })
    jakarta = gpd.read_file(jakarta_geojson)    
    gdf = gpd.GeoDataFrame(records, crs="EPSG:4326")
    clipped_gdf = gpd.clip(gdf, jakarta)
    print(clipped_gdf)

    return clipped_gdf
    # disini
