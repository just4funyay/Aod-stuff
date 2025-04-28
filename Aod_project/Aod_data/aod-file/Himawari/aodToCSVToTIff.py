import xarray as xr
import rioxarray  # <<< Tambahkan ini!

# 1. Buka file
ds = xr.open_dataset('H09_20250426_0000_1DARP031_FLDK.02401_02401.nc')

# 2. Tentukan batas Jakarta
min_lon, max_lon = 95.0, 141.0
min_lat, max_lat = -11.0, 6.0

# 3. Cari nama lon/lat
lon_name = [name for name in ds.coords if 'lon' in name.lower()][0]
lat_name = [name for name in ds.coords if 'lat' in name.lower()][0]

# 4. Subset data Jakarta
jakarta_data = ds.where(
    (ds[lon_name] >= min_lon) & (ds[lon_name] <= max_lon) & 
    (ds[lat_name] >= min_lat) & (ds[lat_name] <= max_lat),
    drop=True
)

# 5. Simpan ke CSV
df = jakarta_data.to_dataframe().reset_index()
df.to_csv('data_jakarta.csv', index=False)

aod = jakarta_data['AOT_L2_Mean']

# 6. Assign CRS ke DataArray
aod = aod.rio.write_crs("EPSG:4326")  # << Ini WAJIB, karena .nc kadang belum ada CRS

# 7. Simpan jadi GeoTIFF
aod.rio.to_raster('data_jakarta.tif')
