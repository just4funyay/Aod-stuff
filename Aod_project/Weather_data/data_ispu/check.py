import pandas as pd

# Ganti 'file_anda.csv' dengan nama file CSV Anda
data = pd.read_excel('bundaran_hi_08052025.xls')
pm25Value = data['ISPU PM2.5']

# Menampilkan beberapa baris pertama dari data untuk pengecekan
print(pm25Value)
