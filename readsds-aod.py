import netCDF4
from netCDF4 import Dataset

from pathlib import Path

cwd = Path.cwd()
folder_name = 'data-aod'
folder_path = cwd / folder_name

for file in folder_path.iterdir():
    ds = Dataset(file)
    print(ds.variables['Latitude'][:][:])
    print("-----------------")