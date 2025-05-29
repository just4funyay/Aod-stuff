import os
import sys
import django
import pandas as pd
import csv
import joblib

# Setup Django environment
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
sys.path.append(PROJECT_ROOT)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Aod_project.settings")
django.setup()


from .predict import predict_model
from Aod_data.models import RasterData, pm25DataEstimate, PolygondataPM25
from Weather_data.models import WeatherData
from django.contrib.gis.gdal import GDALRaster
from django.conf import settings
from django.contrib.gis.geos import GEOSGeometry
from .csvToRaster import csv_to_geotiff,csvToPolygon

folderpath = 'Aod_data/model/Estimate'
os.makedirs(folderpath, exist_ok=True)

def estimatePm25():
    rasterdata_all = RasterData.objects.all()

    for rasterdata in rasterdata_all:
        aod_value = rasterdata.data
        print(aod_value)
        aod_date = rasterdata.time_retrieve

        # Cek apakah sudah diproses sebelumnya
        if pm25DataEstimate.objects.filter(aodid=rasterdata).exists():
            print(f"[SKIP] Data PM2.5 untuk RasterData ID {rasterdata.id} sudah ada.")
            continue

        weather_on_date = WeatherData.objects.filter(date=aod_date)
        if not weather_on_date.exists():
            print(f"[WARNING] Tidak ada data cuaca untuk tanggal {aod_date}, lewati ID {rasterdata.id}.")
            continue

        merged_rows = []

        for aod in aod_value:
            aod_longitude = aod['longitude']
            aod_latitude = aod['latitude']
            aod_val = aod['aod_values']
            print(aod_latitude,aod_longitude)

            for weather_data in weather_on_date:
                merged_rows.append({
                    'datetime': aod_date,
                    'aod_longitude': aod_longitude,
                    'aod_latitude': aod_latitude,
                    'station_longitude': weather_data.station.location.x,
                    'station_latitude': weather_data.station.location.y,
                    'AOD': aod_val,
                    'tempmax': weather_data.temp_max,
                    'tempmin': weather_data.temp_min,
                    'temp': weather_data.temperature,
                    'feelslikemax': weather_data.feels_like_max,
                    'feelslikemin': weather_data.feels_like_min,
                    'feelslike': weather_data.feels_like,
                    'dew': weather_data.dew_point,
                    'humidity': weather_data.humidity,
                    'precip': weather_data.precipitation,
                    'precipcover': weather_data.precip_cover,
                    'windgust': weather_data.wind_gust,
                    'windspeed': weather_data.wind_speed,
                    'winddir': weather_data.wind_dir,
                    'sealevelpressure': weather_data.sea_level_pressure,
                    'cloudcover': weather_data.cloud_cover,
                    'visibility': weather_data.visibility,
                    'solarradiation': weather_data.solar_radiation,
                    'solarenergy': weather_data.solar_energy,
                    'uvindex': weather_data.uv_index,
                })

        if not merged_rows:
            print(f"[WARNING] Tidak ada data gabungan untuk ID {rasterdata.id}, lewati.")
            continue

        # Simpan ke CSV
        file_name = os.path.join(folderpath, f'aod_data_{rasterdata.id}.csv')
        with open(file_name, mode='w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=merged_rows[0].keys())
            writer.writeheader()
            writer.writerows(merged_rows)

        print(f"[INFO] Data AOD ID {rasterdata.id} disimpan ke {file_name}")

        
        df = predict_model(file_name)
        
        tiff_file = os.path.join(folderpath, f'predicted_{rasterdata.id}.tif')
        # diganti csv to polygon
        #tiff_file = csv_to_geotiff(df, tiff_file) 

        #raster = GDALRaster(tiff_file, write=True)
        data = df.to_dict(orient="records")
        jakarta_geojson = os.path.join(settings.BASE_DIR, 'id-jk.geojson')
        polygondata = csvToPolygon(df, jakarta_geojson)
        pm25data = pm25DataEstimate.objects.create(
            aodid=rasterdata,
            valuepm25=data,
        #    raster=raster,
            time=rasterdata.time_retrieve
        )
        for _, row in polygondata.iterrows():
            geom = row.geometry
            if geom.geom_type == 'MultiPolygon':
                for poly in geom.geoms:
                    polygon = GEOSGeometry(poly.wkt, srid=4326)
                                    
                    PolygondataPM25.objects.create(
                        pm25id=pm25data,
                        geom=polygon,
                        pm25_value=row['pm25'],
                        date=pm25data.time
                    )
            else:
                polygon = GEOSGeometry(geom.wkt, srid=4326)
                                
                PolygondataPM25.objects.create(
                    pm25id=pm25data,
                    geom=polygon,
                    pm25_value=row['pm25'],
                    date=pm25data.time
                )

        print(f"[SUCCESS] Prediksi PM2.5 untuk ID {rasterdata.id} disimpan ke database.\n")
        file_name = os.path.join(folderpath, f'aod_data_{rasterdata.id}.csv')

        if os.path.exists(file_name):
            os.remove(file_name)
            print(f"File {file_name} berhasil dihapus.")
        else:
            print(f"File {file_name} tidak ditemukan.")
        
estimatePm25()