import sys
import os
import django
import numpy as np
import pandas as pd
from datetime import timedelta
from django.utils import timezone
from tensorflow.keras.models import load_model
from sklearn.preprocessing import MinMaxScaler

# Setup Django project
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
sys.path.append(PROJECT_ROOT)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Aod_project.settings")
django.setup()

# Import Django models
from Aod_data.models import RasterData
from Weather_data.models import WeatherData, pm25DataActual, WeatherStation, pm25DataPrediction


def predict_pm25_for_all_stations():
    import numpy as np
    from datetime import timedelta
    from django.utils import timezone
    from sklearn.preprocessing import MinMaxScaler
    from tensorflow.keras.models import load_model
    import os
    import pandas as pd

    def find_nearest_point(lat_target, lon_target, latitudes, longitudes):
        points = np.array(list(zip(latitudes, longitudes)))
        target = np.array([lat_target, lon_target])
        distances = np.linalg.norm(points - target, axis=1)
        print(distances)
        idx_min = distances.argmin()
        return idx_min

    # Rentang tanggal prediksi
    end_date = timezone.now().date()
    yesterday = end_date - timedelta(days=10)
    start_date = yesterday - timedelta(days=30)

    # Ambil semua stasiun cuaca
    stations = WeatherStation.objects.all()

    for station in stations:
        print(f"Memproses stasiun: {station.name} (ID: {station.id})")
        lon, lat = station.location.x, station.location.y
        aod_all = RasterData.objects.filter(time_retrieve__range=(start_date, yesterday)).order_by("time_retrieve")
        weather_all = WeatherData.objects.filter(date__range=(start_date, yesterday), station=station)
        pm25_all = pm25DataActual.objects.filter(date__range=(start_date, yesterday), station=station)
        records = []
        for aod in aod_all:
            date = aod.time_retrieve
            latitudes = [entry['latitude'] for entry in aod.data]
            longitudes = [entry['longitude'] for entry in aod.data]
            values = [entry['aod_values'] for entry in aod.data]
            print(latitudes)
            print(longitudes)

            try:
                idx_terdekat = find_nearest_point(lat, lon, latitudes, longitudes)
                aod_value = values[idx_terdekat]
            except Exception:
                aod_value = None

            weather = weather_all.filter(date=date).first()
            temp = weather.temperature if weather else None
            dew = weather.dew_point if weather else None
            humidity = weather.humidity if weather else None
            windspeed = weather.wind_speed if weather else None
            precip = weather.precipitation if weather else None

            pm25 = pm25_all.filter(date=date).first()
            pm25_value = pm25.pm25_value if pm25 else None

            records.append({
                'tanggal': date,
                'ISPU PM2.5': pm25_value,
                'temp': temp,
                'dew': dew,
                'humidity': humidity,
                'precip': precip,
                'windspeed': windspeed,
                'AOD': aod_value,
            })

        df = pd.DataFrame(records)

        if df.empty:
            print(f"Tidak ada data untuk stasiun {station.name}. Lewati.")
            continue

        for col in ['ISPU PM2.5', 'temp', 'dew', 'humidity', 'windspeed', 'precip', 'AOD']:
            df[col] = df[col].interpolate(method='linear')
        df = df.dropna()

        if len(df) < 30:
            print(f"Data kurang dari 30 hari untuk stasiun {station.name}. Lewati.")
            continue

        features = ["temp", "dew", "humidity", "precip", "windspeed", "AOD", "ISPU PM2.5"]
        scaler = MinMaxScaler()
        scaler.fit(df[features])

        sequence_raw = df[features].iloc[-30:].values
        sequence_scaled = scaler.transform(sequence_raw)
        x_manual = sequence_scaled[np.newaxis, ...]

        # Path model untuk stasiun
        model_path = os.path.join(PROJECT_ROOT, f"Aod_data/model/Prediction/{station.name}.keras")
        if not os.path.exists(model_path):
            print(f"Model tidak ditemukan untuk stasiun {station.name}. Path: {model_path}")
            continue

        try:
            model = load_model(model_path)
        except Exception as e:
            print(f"Gagal load model untuk stasiun {station.name}: {e}")
            continue

        y_pred_norm = model.predict(x_manual)[0][0]

        dummy = np.zeros((1, 7))
        dummy[0, 6] = y_pred_norm
        y_pred_real = scaler.inverse_transform(dummy)[0, 6]

        print(f"Prediksi PM2.5 untuk stasiun {station.name}: {y_pred_real:.2f}")

        # Simpan prediksi ke DB kalau perlu
        # pm25DataPrediction.objects.update_or_create(
        #     station=station,
        #     date=yesterday,
        #     defaults={'pm25_value': y_pred_real}
        # )


predict_pm25_for_all_stations()