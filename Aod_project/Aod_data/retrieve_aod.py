import earthaccess
import pathlib
from datetime import datetime, timedelta
import os
import requests
from Aod_data.utils import process_viirs_files

def retrieve_viirs_data():
    today = datetime.today()
    yesterday = today - timedelta(days=3)

    today = today.strftime("%Y-%m-%d")
    yesterday = yesterday.strftime("%Y-%m-%d")

    base_dir = os.path.dirname(os.path.abspath(__file__))
    folder_name = 'aod-file/VIIRS'
    download_path = os.path.join(base_dir, folder_name)
    if not os.path.exists(download_path):
        os.makedirs(download_path)

    auth = earthaccess.login(strategy="netrc") #update

    # 2. Search
    results = earthaccess.search_data(
        short_name='AERDB_L2_VIIRS_SNPP',  
        bounding_box=(106.66, -6.5, 107.1, -6.08),  
        temporal=(yesterday, today)
    )

    folder_name = 'Aod_data/aod-file/VIIRS'
    #download_path = cwd / folder_name
    print(download_path)
    # 3. Access
    files = earthaccess.download(results, download_path)
    process_viirs_files()