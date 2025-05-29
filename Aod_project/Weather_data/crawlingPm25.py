import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import os
from .pm25ToDatabase import pm25ToDatabase

def download_ispu_now():
    urls =  [
        {"url": "https://rendahemisi.jakarta.go.id/ispu-detail/1/us-embassy-1/", "nama_tempat": "us_embassy_1"},
        {"url": "https://rendahemisi.jakarta.go.id/ispu-detail/2/us-embassy-2/", "nama_tempat": "us_embassy_2"},
        {"url": "https://rendahemisi.jakarta.go.id/ispu-detail/3/jakarta-gbk/", "nama_tempat": "jakarta_gbk"},
        {"url": "https://rendahemisi.jakarta.go.id/ispu-detail/4/dki1-bundaran-hi/", "nama_tempat": "bundaran_hi"},
        {"url": "https://rendahemisi.jakarta.go.id/ispu-detail/5/dki2-kelapa-gading/", "nama_tempat": "kelapa_gading"},
        {"url": "https://rendahemisi.jakarta.go.id/ispu-detail/6/dki3-jagakarsa/", "nama_tempat": "jagakarsa"},
        {"url": "https://rendahemisi.jakarta.go.id/ispu-detail/7/dki4-lubang-buaya/", "nama_tempat": "lubang_buaya"},
        {"url": "https://rendahemisi.jakarta.go.id/ispu-detail/8/dki5-kebun-jeruk/", "nama_tempat": "kebun_jeruk"},
    ]
    output_folder="Weather_data/data_ispu"
    os.makedirs(output_folder, exist_ok=True)

    # Ambil tanggal hari ini
    today = datetime.today()
    yesterday = datetime.today() - timedelta(days=1)
    formatted_date = today.strftime("%d-%m-%Y")

    download_url = "https://rendahemisi.jakarta.go.id/Page/ExportIspuData"
    session = requests.Session()

    for tempat in urls:
        url = tempat["url"]
        nama_tempat = tempat["nama_tempat"]

        try:
            response = session.get(url, headers={"User-Agent": "Mozilla/5.0"})
            soup = BeautifulSoup(response.text, "html.parser")
            csrf_token = soup.find("input", {"name": "csrf_binari"})["value"]
            id_location = url.split('/')[4]

            payload = {
                "csrf_binari": csrf_token,
                "id_location": id_location,
                "historical_date": formatted_date
            }

            headers = {
                "User-Agent": "Mozilla/5.0",
                "Referer": url
            }

            res_download = session.post(download_url, data=payload, headers=headers)
            res_download.raise_for_status()

            filename = os.path.join(output_folder, f"{nama_tempat}_{formatted_date.replace('-', '')}.xls")
            with open(filename, "wb") as f:
                f.write(res_download.content)
            print(f"Berhasil disimpan: {filename}")

        except Exception as e:
            print(f"Gagal memproses {nama_tempat} {formatted_date}: {e}")
    print(output_folder)
    pm25ToDatabase(output_folder,"ISPU PM2.5")

import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import os
from .pm25ToDatabase import pm25ToDatabase

def download_ispu_last_40_days():
    urls = [
        {"url": "https://rendahemisi.jakarta.go.id/ispu-detail/1/us-embassy-1/", "nama_tempat": "us_embassy_1"},
        {"url": "https://rendahemisi.jakarta.go.id/ispu-detail/2/us-embassy-2/", "nama_tempat": "us_embassy_2"},
        {"url": "https://rendahemisi.jakarta.go.id/ispu-detail/3/jakarta-gbk/", "nama_tempat": "jakarta_gbk"},
        {"url": "https://rendahemisi.jakarta.go.id/ispu-detail/4/dki1-bundaran-hi/", "nama_tempat": "bundaran_hi"},
        {"url": "https://rendahemisi.jakarta.go.id/ispu-detail/5/dki2-kelapa-gading/", "nama_tempat": "kelapa_gading"},
        {"url": "https://rendahemisi.jakarta.go.id/ispu-detail/6/dki3-jagakarsa/", "nama_tempat": "jagakarsa"},
        {"url": "https://rendahemisi.jakarta.go.id/ispu-detail/7/dki4-lubang-buaya/", "nama_tempat": "lubang_buaya"},
        {"url": "https://rendahemisi.jakarta.go.id/ispu-detail/8/dki5-kebun-jeruk/", "nama_tempat": "kebun_jeruk"},
    ]

    output_folder = "Weather_data/data_ispu"
    os.makedirs(output_folder, exist_ok=True)
    download_url = "https://rendahemisi.jakarta.go.id/Page/ExportIspuData"

    session = requests.Session()
    headers = {"User-Agent": "Mozilla/5.0"}

    for tempat in urls:
        url = tempat["url"]
        nama_tempat = tempat["nama_tempat"]

        # Ambil CSRF token dari halaman tempat
        response = session.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")
        csrf_token = soup.find("input", {"name": "csrf_binari"})["value"]
        id_location = url.split('/')[4]

        for day in range(30):
            date = datetime.today() - timedelta(days=day)
            formatted_date = date.strftime("%d-%m-%Y")
            file_date = date.strftime("%Y%m%d")
            filename = os.path.join(output_folder, f"{nama_tempat}_{file_date}.xls")

                
            if os.path.exists(filename):
                print(f"[=] Lewati (sudah ada): {filename}")
                continue

            payload = {
                "csrf_binari": csrf_token,
                "id_location": id_location,
                "historical_date": formatted_date
            }

            headers["Referer"] = url
            res_download = session.post(download_url, data=payload, headers=headers)
            res_download.raise_for_status()

            with open(filename, "wb") as f:
                f.write(res_download.content)

            print(f"Berhasil: {filename}")


    pm25ToDatabase(output_folder, "ISPU PM2.5")
