import os
import django
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
sys.path.append(PROJECT_ROOT)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Aod_project.settings")
django.setup()

import pandas as pd
from datetime import datetime
from Weather_data.models import WeatherStation, pm25DataActual

def pm25ToDatabase(folder_path, kolom_nilai='ISPU PM2.5'):
    for file in os.listdir(folder_path):
        if file.endswith('.xls') or file.endswith('.xlsx'):
            try:
                filename = os.path.splitext(file)[0]
                parts = filename.split('_')
                nama_stasiun = '_'.join(parts[:-1])
                tanggal_str = parts[-1]
                print(tanggal_str)
                tanggal = datetime.strptime(tanggal_str, "%d%m%Y").date()
                
                print(tanggal)    
                full_path = os.path.join(folder_path, file)
                print(full_path)
                df = pd.read_excel(full_path)

                if kolom_nilai not in df.columns:
                    print(f"Kolom '{kolom_nilai}' tidak ditemukan di file {file}")
                    continue

                df[kolom_nilai] = pd.to_numeric(df[kolom_nilai], errors='coerce')
                rata2 = df[kolom_nilai].mean()

                try:
                    stasiun = WeatherStation.objects.get(name__iexact=nama_stasiun.strip())
                    pm25DataActual.objects.create(
                        station=stasiun,
                        date=tanggal,
                        pm25_value=rata2
                    )
                    print(f"Simpan {nama_stasiun} - {tanggal} - rata2: {rata2:.2f}")
                except WeatherStation.DoesNotExist:
                    print(f"Stasiun '{nama_stasiun}' tidak ditemukan di database.")

                try:
                    os.remove(full_path)
                    print(f"File {file} berhasil dihapus.")
                except Exception as e:
                    print(f"Gagal menghapus file {file}: {e}")

            except Exception as e:
                print(f"Gagal memproses file {file}: {e}")
