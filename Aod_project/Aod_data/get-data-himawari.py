from ftplib import FTP
from datetime import datetime
import os

def getDataHimawari():
    ftpUser = "mahamaha_apps.ipb.ac.id"
    ftpPassword = "SP+wari8"
    today = datetime.utcnow()
    year = today.year
    month = today.month
    endyear = today.year
    dirData = f"pub/himawari/L3/ARP/031/{year}{month:02d}/daily"
    base_dir = os.path.dirname(os.path.abspath(__file__))
    folder_name = 'aod-file/Himawari'
    download_path = os.path.join(base_dir, folder_name)

    ftp = FTP("ftp.ptree.jaxa.jp")
    ftp.login(ftpUser, ftpPassword)
    print("Logged in to FTP server.")
    try:
        ftp.cwd(dirData)
        files = sorted(ftp.mlsd())
        print(f"Isi folder {dirData}:")
        
        for file_name, _ in files:
            print(file_name)  # Hanya nama file yang dicetak

        lastestFile = files[-1][0]
        local_file_path = os.path.join(download_path, lastestFile)
        if lastestFile.endswith('.nc'):
            with open(local_file_path, 'wb') as local_file:
                ftp.retrbinary(f"RETR {lastestFile}", local_file.write)
            print(f"File {lastestFile} berhasil didownload.")
        
    except Exception as e:
        print(f"Gagal mengakses {dirData}: {e}")
    ftp.quit()



