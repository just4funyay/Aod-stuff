import xarray as xr
import rioxarray  # <<< Tambahkan ini!

# 1. Buka file
ds = xr.open_dataset('Aod_data/aod-file/Himawari/H09_20250519_0000_1DARP031_FLDK.02401_02401.nc', engine="netcdf4")

