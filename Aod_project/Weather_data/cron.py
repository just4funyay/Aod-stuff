import requests

def fetch_weather_data():
    """Fungsi ini akan memanggil endpoint API weather"""
    url = "http://127.0.0.1:8000/api2/weather/fetch/"  # URL API kamu
    try:
        response = requests.get(url)

        if response.status_code == 200:
            print("Weather data fetched successfully")
        else:
            print(f"Failed to fetch weather data: {response.status_code}")
    
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
