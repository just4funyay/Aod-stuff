import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import os

def download_ispu_hari_ini(output_folder="data_ispu", urls=None):
    if urls is None:
        urls = [
            {"url": "https://rendahemisi.jakarta.go.id/ispu-detail/2/us-embassy-2/", "nama_tempat": "us-embassy-2"},
            {"url": "https://rendahemisi.jakarta.go.id/ispu-detail/3/jakarta-gbk/", "nama_tempat": "jakarta-gbk"},
            {"url": "https://rendahemisi.jakarta.go.id/ispu-detail/8/dki5-kebun-jeruk/", "nama_tempat": "dki5-kebun-jeruk"},
            {"url": "https://rendahemisi.jakarta.go.id/ispu-detail/7/dki4-lubang-buaya/", "nama_tempat": "dki4-lubang-buaya"},
            {"url": "https://rendahemisi.jakarta.go.id/ispu-detail/6/dki3-jagakarsa/", "nama_tempat": "dki3-jagakarsa"}
        ]

    os.makedirs(output_folder, exist_ok=True)

    # Ambil tanggal hari ini
    today = datetime.today()
    yesterday = datetime.today() - timedelta(days=1)
    formatted_date = yesterday.strftime("%d-%m-%Y")

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

            filename = os.path.join(output_folder, f"{nama_tempat}_{formatted_date.replace('-', '')}.csv")
            with open(filename, "wb") as f:
                f.write(res_download.content)
            print(f"[✓] Berhasil disimpan: {filename}")

        except Exception as e:
            print(f"[!] Gagal memproses {nama_tempat} {formatted_date}: {e}")

# Contoh pemanggilan
if __name__ == "__main__":
    download_ispu_hari_ini()
