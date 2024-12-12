"""
    Match the two data logs files (the sensor data and the API data)

"""

import pandas as pd

# Clean weather data
# remove the lines with the same values (i.e., where last_updated is the same) 

api_df = pd.read_csv("raw_weather_data.csv")
api_df.drop_duplicates(subset=['last_updated'], inplace=True)

# Convert the timestamps to 15-minute timeframes
# E.g., instead of 2024-11-25 10:30, we get 2024-11-25 [10:30, 10:45)
api_df['time_range'] = api_df['last_updated'].apply(lambda x: f"{pd.to_datetime(x).strftime('%Y-%m-%d')} [{pd.to_datetime(x).strftime('%H:%M')}, {(pd.to_datetime(x) + pd.Timedelta(minutes=15)).strftime('%H:%M')})")


# Clean sensor data 
# Check the maximum difference between successive Unix timestamps
sensor_df = pd.read_csv("raw_sensor_data.csv")
sensor_df['Time_Diff'] = sensor_df['Unix_timestamp'].diff()

# Find the index of the maximum difference
max_diff_index = sensor_df['Time_Diff'].idxmax()

# Print the result
print(f"The maximum time difference occurs at index: {max_diff_index}")
print(f"Difference: {sensor_df.loc[max_diff_index, 'Time_Diff']} seconds")


# Change the frequency to 15 minutes - Temperature and humidity do not change in 5 minutes
# Initialize the filtered DataFrame with the first row
filtered_df = sensor_df.iloc[:1]

# Iterate through the DataFrame and keep only rows with a timestamp difference >= 900 seconds (15 minutes)
for i in range(1, len(sensor_df)):
    if sensor_df.loc[i, 'Unix_timestamp'] - filtered_df.iloc[-1]['Unix_timestamp'] >= 900:
        filtered_df = pd.concat([filtered_df, sensor_df.iloc[[i]]])


# Put the sensor data timestamps into ranges that match the API data
# E.g., instead of 00:16, we say [00:15, 00:30)
# Convert the 'Timestamp' column to datetime
filtered_df['Timestamp'] = pd.to_datetime(filtered_df['Timestamp'])

# Round down each timestamp to the nearest 15-minute interval
def round_to_nearest_15min(timestamp):
    # Round down to nearest 15-minute
    rounded_time = timestamp - pd.Timedelta(minutes=timestamp.minute % 15,
                                             seconds=timestamp.second,
                                             microseconds=timestamp.microsecond)
    end_time = rounded_time + pd.Timedelta(minutes=15)
    return f"{rounded_time.strftime('%Y-%m-%d')} [{rounded_time.strftime('%H:%M')}, {end_time.strftime('%H:%M')})"

# Apply the function to the Timestamp column to create the time range
filtered_df['time_range'] = filtered_df['Timestamp'].apply(round_to_nearest_15min)


# ************************ Merge the 2 datasets ************************
# Merge the datasets on 'Time_Range'
# Every column from API preceed it by outdoor and every column in sensor data preceed it by indoor 
api_df.drop(columns=['last_updated','timestamp'], inplace=True)
filtered_df.drop(columns=['ID','Timestamp','Unix_timestamp','Time_Diff'], inplace=True)

filtered_df.columns = list(map(lambda x: f"indoor_{x.lower()}" if x != "time_range" else x, filtered_df.columns))
api_df.columns = list(map(lambda x: f"outdoor_{x.lower()}" if x not in ["time_range", "city"] else x, api_df.columns))

merged_df = pd.merge(api_df, filtered_df, on='time_range', how='inner')   

# Move 'time_range' to the first column
merged_df = merged_df[['time_range'] + [col for col in merged_df.columns if col != 'time_range']]


merged_df.to_csv("merged_data.csv", index=False)

 