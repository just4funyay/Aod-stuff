import joblib
import pandas as pd
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

def predict_model(filename):
        model = joblib.load("Aod_data/model/Estimate/best_model.pkl")

        df = pd.read_csv(filename)
        X_pred = df[['AOD', 'tempmax', 'tempmin', 'temp', 'feelslikemax', 'feelslikemin', 'feelslike', 'dew', 'humidity',
                'precip', 'precipcover', 'windgust', 'windspeed', 'winddir', 'sealevelpressure',
                'cloudcover', 'visibility', 'solarradiation', 'solarenergy', 'uvindex']]
        df['PM2.5'] = model.predict(X_pred)
        output_df = df[['aod_latitude', 'aod_longitude','PM2.5']]

        print(output_df)
        return output_df
#output_df.to_csv('pm25_lat_lon_predictions.csv', index=False)
