import earthaccess
import pathlib

cwd = pathlib.Path.cwd()

# 1. Login
earthaccess.login()

# 2. Search
results = earthaccess.search_data(
    short_name='AERDB_L2_VIIRS_SNPP',  # ATLAS/ICESat-2 L3A Land Ice Height
    bounding_box=(106, -7, 107, -6),  # Only include files in area of interest...
    temporal=("2024-09-10", "2024-09-13"),  # ...and time period of interest.
    count=5
)

folder_name = 'data-aod'
download_path = cwd / folder_name
# 3. Access
files = earthaccess.download(results, download_path)