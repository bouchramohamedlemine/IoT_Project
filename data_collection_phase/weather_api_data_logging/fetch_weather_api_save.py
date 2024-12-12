"""
    Retreives and logs data from the weather API every 15 minutes.
"""

import requests
import pandas as pd
import time
from datetime import datetime

# The WeatherAPI key
api_key = 'e3b800eb3d6b4c90b6a142045242211'

# City for which to fetch weather data
city = 'London'

# API URL with AQI set to 'yes'
url = f"http://api.weatherapi.com/v1/current.json?key={api_key}&q={city}&aqi=yes"


def fetch_weather_data():
    """
        Function to fetch weather data from the API.
    """
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()

        # Extract relevant weather and air quality information
        weather_info = {
            'city': data['location']['name'],
            'temperature': data['current']['temp_c'],
            'humidity': data['current']['humidity'],
            'wind_speed': data['current']['wind_kph'],
            'pm2_5': data['current']['air_quality']['pm2_5'],
            'pm10': data['current']['air_quality']['pm10'],
            'co': data['current']['air_quality']['co'],
            'no2': data['current']['air_quality']['no2'],
            'o3': data['current']['air_quality']['o3'],
            'last_updated': data['current']['last_updated'],
            'timestamp': str(datetime.now()).split(".")[0].split(" ")[1]  # Timestamp for each data entry
        }
        return weather_info
    else:
        print(f"Error fetching data: {response.status_code}, {response.text}")
        return {
            'city': "null",
            'temperature': "null",
            'humidity': "null",
            'wind_speed': "null",
            'pm2_5': "null",
            'pm10': "null",
            'co': "null",
            'no2': "null",
            'o3': "null",
            'last_updated': "null",
            'timestamp': str(datetime.now()).split(".")[0].split(" ")[1]  # Timestamp for each data entry
        }


# Create or load the CSV file for storing weather data
csv_file = 'raw_weather_data.csv'

# Column headers for the CSV
columns = ['city', 'temperature', 'humidity', 'wind_speed', 'pm2_5', 'pm10', 'co', 'no2', 'o3', 'last_updated', 'timestamp']

# Check if the CSV file already exists, if not, create it and write the header
try:
    df = pd.read_csv(csv_file)
except FileNotFoundError:
    df = pd.DataFrame(columns=columns)
    df.to_csv(csv_file, index=False)

# Function to save data to CSV using pd.concat
def save_to_csv(data):
    df = pd.read_csv(csv_file)
    new_data = pd.DataFrame([data])
    # Use pd.concat to append the new data to the DataFrame
    new_data.to_csv(csv_file, mode='a', index=False, header=False)

# Fetch and save data every 10 minutes
try:
    while True:
        # Fetch the latest weather data
        new_data = fetch_weather_data()

        if new_data:
            # Save the fetched data to the CSV
            save_to_csv(new_data)

        # Wait for the next data retrieval interval (15 minutes)
        time.sleep(600)  # 10 minutes = 600 seconds

except KeyboardInterrupt:
    print("Data collection stopped.")
