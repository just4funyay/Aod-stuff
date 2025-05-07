import numpy as np
import xarray as xr
import rasterio
from rasterio.transform import from_origin

def csv_to_geotiff(dataframe, output_path):
    # Ambil kolom latitude, longitude, dan PM2.5
    latitudes = dataframe['aod_latitude'].values
    longitudes = dataframe['aod_longitude'].values
    pm25_values = dataframe['PM2.5'].values

    # Ambil nilai unik dan balik latitude agar dari utara ke selatan
    latitudes_unique = np.unique(latitudes)[::-1]
    longitudes_unique = np.unique(longitudes)

    # Buat grid kosong
    pm25_grid = np.full((len(latitudes_unique), len(longitudes_unique)), np.nan)

    # Isi grid
    for lat, lon, pm25 in zip(latitudes, longitudes, pm25_values):
        lat_idx = np.where(latitudes_unique == lat)[0][0]
        lon_idx = np.where(longitudes_unique == lon)[0][0]
        pm25_grid[lat_idx, lon_idx] = pm25

    # Buat DataArray
    data_array = xr.DataArray(
        pm25_grid,
        coords={
            'latitude': latitudes_unique,
            'longitude': longitudes_unique
        },
        dims=['latitude', 'longitude']
    )

    # Hitung resolusi grid
    res_lat = abs(latitudes_unique[1] - latitudes_unique[0])
    res_lon = abs(longitudes_unique[1] - longitudes_unique[0])

    # Transformasi raster
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

    print(f"✅ GeoTIFF berhasil disimpan ke: {output_path}")
