"""
    The Flask webapp that displays data.

    Author: Bouchra Mohamed Lemine

"""

from flask import Flask, render_template, jsonify
import pandas as pd
import time
import threading
import requests
import joblib
import  numpy as np
import paho.mqtt.client as mqtt
import json
from utils import get_action, is_time_to_log, fetch_weather_data
from datetime import datetime

app = Flask(__name__)


# The WeatherAPI key
api_key = 'e3b800eb3d6b4c90b6a142045242211'

# City for which to fetch weather data
city = 'London'

# API URL with AQI set to 'yes'
api_url = f"http://api.weatherapi.com/v1/current.json?key={api_key}&q={city}&aqi=yes"

# Loading the model using joblib
loaded_model = joblib.load("random_forest_model.joblib")


# MQTT configuration
mqtt_broker = "broker.hivemq.com"  # Same broker as the ESP32
mqtt_port = 1883
mqtt_topic_buzzer = "topic/buzzer"  # Topic to control the buzzer
mqtt_topic_temp_hum = "topic/temp_hum"  # Topic for temperature and humidity

# Global variables to store the latest temperature and humidity
indoor_temperature = None
indoor_humidity = None

# MQTT Client setup
mqtt_client = mqtt.Client()


def on_connect(client, userdata, flags, rc):
    """
        MQTT Callback for when the client connects.
    """
    print(f"Connected with result code {rc}")
    if rc == 0:
        print("Successfully connected to MQTT broker.")
        client.subscribe(mqtt_topic_temp_hum)  # Subscribe to temp_hum topic
    else:
        print(f"Failed to connect to MQTT broker. Return code: {rc}")




def on_message(client, userdata, message):
    """
        MQTT Callback for receiving messages.
    """
    global indoor_temperature
    global indoor_humidity
    print("Message received.")
    try:
        # Parse the received message
        payload = message.payload.decode()
        print(f"Received message: {payload}")

        # If the message is a valid JSON object
        data = json.loads(payload)
        indoor_temperature = data.get("temperature")
        indoor_humidity = data.get("humidity")

    except Exception as e:
        print(f"Error processing message: {e}")




def connect_mqtt():
    """
        Connect to MQTT broker.
    """
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    mqtt_client.connect(mqtt_broker, mqtt_port, 60)
    mqtt_client.loop_start()  # Start the MQTT loop to handle messages asynchronously




def get_all_data():
    """
        Function to retreive all weather data.
    """
    weather_info = fetch_weather_data(api_url)
    # Predict what the PM2.5 concentration will be after 15 minutes
    input = np.array(list(weather_info.values())[3:]).reshape(1, -1)
    predicted_pm2_5 = loaded_model.predict(input)[0]

    weather_info['predicted_pm2_5'] = round(float(predicted_pm2_5), 3)
    weather_info['indoor_temperature'] = indoor_temperature
    weather_info['indoor_humidity'] = indoor_humidity

    if indoor_humidity != None or indoor_temperature != None:
        action = get_action(weather_info['outdoor_temperature'], 
                                            weather_info['outdoor_humidity'], 
                                            weather_info['outdoor_pm2_5'], 
                                            predicted_pm2_5, 
                                            indoor_temperature, 
                                            indoor_humidity)
        
        weather_info['action_key']  = action[0]
        weather_info['action_text']  = action[1]

        return weather_info
    
    return None




def update_weather_data():
    """
        Function that periodically updates weather data.
    """
    while True:
        weather_info = get_all_data()  # Update weather data

        # Only log data when all values are aviable and this line has not been logged (we noticed that multithreading writes a line twice)
        if weather_info and is_time_to_log(csv_file_path, weather_info['timestamp'] ):
            
            # !!!!!!! log weather data 
            new_data = pd.DataFrame([weather_info])
            new_data.to_csv(csv_file_path, mode='a', index=False, header=False)

            # Publish the action to the ESP32 
            if weather_info['action_key'] == 1:
                mqtt_client.publish("topic/buzzer", "ON")
            if weather_info['action_key'] == -1:
                mqtt_client.publish("topic/buzzer", "OFF")

        else:
            print("!!!!!!!!!!! Some weather values are null")

        time.sleep(900)  # Wait for 15 minutes before updating again




def start_background_task():
    """
        Start the weather data updating in a background thread.
    """
    thread = threading.Thread(target=update_weather_data)
    thread.daemon = True  # Daemon thread will automatically exit when the main program exits
    thread.start()




# Route to render the main HTML page
@app.route('/')
def index():
    return render_template('index.html') 




# Route to return updated weather data as JSON
@app.route('/get_weather_data')
def get_weather_data(): 
    # Red the last 10 entries in the log file and show them
    df = pd.read_csv(csv_file_path)
    data = df.tail(10).to_dict(orient='records')
    return jsonify(data)



# Start the Flask app
if __name__ == '__main__':
    # Create or load the CSV file for storing weather data
    csv_file_path = 'data_logging.csv'

    # Column headers for the CSV
    columns = ['timestamp', 'outdoor_temperature', 'outdoor_humidity', 'wind_speed', 'outdoor_pm2_5', 'outdoor_pm10', 'outdoor_co', 'outdoor_no2', 'outdoor_o3', 'predicted_pm2_5', 'indoor_temperature', 'indoor_humidity', 'action_key', 'action_text']

    # Check if the CSV file already exists, if not, create it and write the header
    try:
        df = pd.read_csv(csv_file_path)
    except FileNotFoundError:
        df = pd.DataFrame(columns=columns)
        df.to_csv(csv_file_path, index=False)


    # Start MQTT connection
    connect_mqtt()

    start_background_task()  # Start the background task
    port = int(os.environ.get("PORT", 5000))  # Default to 5000 if PORT is not set
    app.run(host="0.0.0.0", port=port)
    
