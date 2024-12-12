"""
    This module contains functions used by the backend.

    Author: Bouchra Mohamed Lemine

"""


import pandas as pd 
from datetime import datetime
import requests



def get_action(outdoor_temperature, outdoor_humidity, outdoor_pm2_5, predicted_pm2_5, indoor_temperature, indoor_humidity) -> int:
    """
    Determines the action to open or close the window based on environmental conditions.
    
    Parameters:
    - outdoor_temperature (float): Current outdoor temperature.
    - outdoor_humidity (float): Current outdoor humidity.
    - outdoor_pm2_5 (float): Current outdoor PM10 level.
    - predicted_pm2_5 (float): Predicted outdoor PM10 level after 15 minutes.
    - indoor_temperature (float): Current indoor temperature.
    - indoor_humidity (float): Current indoor humidity.
    
    Returns:
    - int: 1 to increase ventilation, -1 to to decrease it, or 0 to do nothing.
    """

    # Thresholds
    max_pm2_5_outdoor = 30  # Safe PM2.5 level for outdoor air (in µg/m³)
    comfort_temperature_range = (20, 25)  # Comfortable indoor temperature range (°C)
    outdoor_humidity_threshold = 80 

    # Conditions to close the window
    # If PM2.5 is high or predicted to be high, close window
    if outdoor_pm2_5 > max_pm2_5_outdoor:
        return -1, "reduce ventilation outdoor PM2.5 is high"   
    
    elif predicted_pm2_5 > max_pm2_5_outdoor:
        return -1, "reduce ventilation outdoor PM2.5 is predicted to rise"  

    # Temperature considerations 
    if indoor_temperature < comfort_temperature_range[0]:
        # If it's too cold inside, only open the window if outdoor temp is warmer
        if outdoor_temperature > indoor_temperature:
            return 1, "increase ventilation to warm indoor space"   
        else:
            return 0, "indoor conditions are good"  # Keep it closed to retain heat
    elif indoor_temperature > comfort_temperature_range[1]:
        # If it's too warm inside, only open the window if outdoor temp is cooler
        if outdoor_temperature < indoor_temperature:
            return 1, "increase ventilation to cool indoor space"   
        else:
            return 0, "indoor conditions are good"   

    # Humidity considerations
    if outdoor_humidity > outdoor_humidity_threshold:
        return -1, "reduce ventilation outdoor humidity is too high"

    # If none, do notheing 
    return 0, "indoor conditions are good"





def is_time_to_log(csv_file_path, current_timestamp):
    """
        Function to check if 15 minutes have passed since the last logged timestamp.
    """
    try:
        # Read the CSV to get the last timestamp
        df = pd.read_csv(csv_file_path)
        
        # Get the last timestamp from the file (last row)
        last_timestamp = df['timestamp'].iloc[-1] if not df.empty else None
        
        if last_timestamp:
            # Convert both timestamps to datetime objects
            last_timestamp_dt = datetime.strptime(last_timestamp, "%d/%m/%Y %H:%M")
            current_timestamp_dt = datetime.strptime(current_timestamp, "%d/%m/%Y %H:%M")
            
            # Calculate the time difference in minutes
            time_diff = (current_timestamp_dt - last_timestamp_dt).total_seconds() / 60.0
            
            # Check if the difference is at least 15 minutes
            return time_diff >= 15
        
        # If there is no last timestamp (first entry), allow logging
        return True
    
    except Exception as e:
        print(f"Error checking timestamp: {e}")
        return False
    




# Function to fetch weather data from the API
def fetch_weather_data(url):
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()

        # Extract relevant weather and air quality information
        weather_info = {
            'timestamp': datetime.now().strftime("%d/%m/%Y %H:%M"),
            'outdoor_temperature': data['current']['temp_c'],
            'outdoor_humidity': data['current']['humidity'],
            'wind_speed': data['current']['wind_kph'],
            'outdoor_pm2_5': data['current']['air_quality']['pm2_5'],
            'outdoor_pm10': data['current']['air_quality']['pm10'],
            'outdoor_co': data['current']['air_quality']['co'],
            'outdoor_no2': data['current']['air_quality']['no2'],
            'outdoor_o3': data['current']['air_quality']['o3']
        }

        return weather_info
    else:
        print(f"Error fetching data: {response.status_code}, {response.text}")
        return {
            'timestamp': datetime.now().strftime("%d/%m/%Y %H:%M"),
            'outdoor_temperature': "null",
            'outdoor_humidity': "null",
            'wind_speed': "null",
            'outdoor_pm2_5': "null",
            'outdoor_pm10': "null",
            'outdoor_co': "null",
            'outdoor_no2': "null",
            'outdoor_o3': "null"
        } 
