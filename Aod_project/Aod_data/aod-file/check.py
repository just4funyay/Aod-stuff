import xarray as xr

# Buka file .nc
ds = xr.open_dataset('Himawari/H09_20250427_0000_1DARP031_FLDK.02401_02401.nc')

# Tampilkan informasi dataset
print(ds['Latitude'])