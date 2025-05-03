import pandas as pd

# Ganti 'file_anda.csv' dengan nama file CSV Anda
data = pd.read_excel('dki5-kebun-jeruk_01052025.csv')
#pm25Value = data['ISPU PM2.5']

# Menampilkan beberapa baris pertama dari data untuk pengecekan
print(data)
