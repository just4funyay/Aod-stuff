import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import csv

# Daftar URL lokasi
urls = [
    {"url": "https://rendahemisi.jakarta.go.id/ispu-detail/2/us-embassy-2/", "nama_tempat": "us-embassy-2"},
    {"url": "https://rendahemisi.jakarta.go.id/ispu-detail/3/jakarta-gbk/", "nama_tempat": "jakarta-gbk"},
    {"url": "https://rendahemisi.jakarta.go.id/ispu-detail/8/dki5-kebun-jeruk/", "nama_tempat": "dki5-kebun-jeruk"},
    {"url": "https://rendahemisi.jakarta.go.id/ispu-detail/7/dki4-lubang-buaya/", "nama_tempat": "dki4-lubang-buaya"},
    {"url": "https://rendahemisi.jakarta.go.id/ispu-detail/6/dki3-jagakarsa/", "nama_tempat": "dki3-jagakarsa"}
]

download_url = "https://rendahemisi.jakarta.go.id/Page/ExportIspuData"

# Rentang tanggal
tanggal_awal = "10-04-2025"
tanggal_akhir = "24-04-2025"

# Mengonversi string tanggal menjadi objek datetime
start_date = datetime.strptime(tanggal_awal, "%d-%m-%Y")
end_date = datetime.strptime(tanggal_akhir, "%d-%m-%Y")

# Step 1: Ambil halaman dan ekstrak CSRF token
session = requests.Session()

# Loop untuk setiap tanggal dalam rentang
current_date = start_date
while current_date <= end_date:
    formatted_date = current_date.strftime("%d-%m-%Y")
    
    for tempat in urls:
        url = tempat["url"]
        nama_tempat = tempat["nama_tempat"]
        
        response = session.get(url, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(response.text, "html.parser")
        csrf_token = soup.find("input", {"name": "csrf_binari"})["value"]
        
        # Step 2: Kirim POST request untuk download
        payload = {
            "csrf_binari": csrf_token,
            "id_location": url.split('/')[4],  # ID location dari URL
            "historical_date": formatted_date
        }

        headers = {
            "User-Agent": "Mozilla/5.0",
            "Referer": url
        }

        res_download = session.post(download_url, data=payload, headers=headers)

        # Step 3: Simpan file dalam format CSV
        filename = f"{nama_tempat}_{formatted_date.replace('-', '')}.csv"
        
        with open(filename, "wb") as f:
            f.write(res_download.content)

        print(f"Berhasil diunduh: {filename}")
    
    # Pindah ke tanggal berikutnya
    current_date += timedelta(days=1)
