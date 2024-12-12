"""
    Parse the sensor data into a csv file.

"""

import json
import csv
from datetime import datetime, timezone

def format_date_time(unix_timestamp):
    """
        Converts a unix timestamp to yyyy-mm-dd hh:mm:ss format
    """
    # Convert the Unix timestamp to a datetime object
    datetime_obj = datetime.fromtimestamp(unix_timestamp, tz=timezone.utc)
    
    # Format the datetime object 
    formatted_datetime = datetime_obj.strftime('%Y-%m-%d %H:%M:%S')
    
    return formatted_datetime



# The input JSON file and output CSV file
input_file = "temp-hum-logger.json"  
output_file = "raw_sensor_data.csv"


# Load the JSON file and extract sensor data
with open(input_file, 'r') as file:
    data = json.load(file)

sensor_data = data['sensorData']


# Write to CSV
with open(output_file, mode='w', newline='') as csv_file:
    writer = csv.writer(csv_file)
    
    # Write header
    writer.writerow(["ID", "Humidity", "Temperature", "Timestamp", "Unix_timestamp"])
    
    # Write rows
    for key, value in sensor_data.items():
        writer.writerow([key, value["humidity"], value["temperature"], format_date_time(value["timestamp"]), value["timestamp"]])


print(f"Data successfully written to {output_file}")
