"""
    Plot the data for analysis.

"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Read data from the file
df = pd.read_csv("merged_data.csv")   

print("Range indoor temp: ", df['indoor_temperature'].min(), df['indoor_temperature'].max())
print("Range indoor hum: ", df['indoor_humidity'].min(), df['indoor_humidity'].max())
print("Range outdoor temp: ", df['outdoor_temperature'].min(), df['outdoor_temperature'].max())
print("Range outdoor hum: ", df['outdoor_humidity'].min(), df['outdoor_humidity'].max())
print("Range PM2.5: ", df['outdoor_pm2_5'].mean(), df['outdoor_pm2_5'].max())
 
df_new = df.copy()
# Exclude the time from time_range only keep data
df_new['day'] = list(map(lambda x: x.split(" ")[0], df['time_range']))

# Get the average PM2.5 per day
avg_pm2_5 = df_new.groupby("day")['outdoor_pm2_5'].mean()
print(avg_pm2_5)
overall_avg_pm2_5 = df['outdoor_pm2_5'].mean()

# Plot the daily PM2.5 levels
plt.figure(figsize=(10, 6))
colours = colours = sns.color_palette("Set1", len(avg_pm2_5))
sns.barplot(x=list(avg_pm2_5.index), y=list(avg_pm2_5), palette=colours) 
# Show the overall mean line for reference
plt.axhline(y=overall_avg_pm2_5, color='r', linestyle='--', label=f'Mean PM2.5 = {round(overall_avg_pm2_5)}µg/m³')
plt.title('The Daily Average PM2.5 Levels')
plt.xlabel('Day')
plt.ylabel('Average PM2.5 Level')
plt.legend()
plt.show()


# *************************** Create subplots of outdoor data 
# Define custom colors for each plot in both figures
colors_figure1 = ['#4E79A7',  # Blue
                  '#F28E2B',  # Orange
                  '#76B7B2',  # Teal
                  '#E15759']  # Red

colors_figure2 = ['#59A14F',  # Green
                  '#EDC948',  # Yellow
                  '#AF7AA1',  # Purple
                  '#FF9DA7']  # Pink

plt.figure(2)
# Create first figure with 4 plots (outdoor data)
fig1, axes1 = plt.subplots(4, 1, figsize=(16, 16), sharex=True)

# Plot outdoor temperature
sns.lineplot(x='time_range', y='outdoor_temperature', data=df, label='Outdoor Temperature', linewidth=2.5, ax=axes1[0], color=colors_figure1[0])
axes1[0].set_ylabel('Temperature (°C)', fontweight='bold', fontsize=10)
axes1[0].legend(loc='upper left', fontsize=12)

# Plot outdoor humidity
sns.lineplot(x='time_range', y='outdoor_humidity', data=df, label='Outdoor Humidity', linewidth=2.5, ax=axes1[1], color=colors_figure1[1])
axes1[1].set_ylabel('Humidity (%)', fontweight='bold', fontsize=10)
axes1[1].legend(loc='upper left', fontsize=12)

# Plot outdoor PM2.5
sns.lineplot(x='time_range', y='outdoor_pm2_5', data=df, label='Outdoor PM2.5', linewidth=2.5, ax=axes1[2], color=colors_figure1[2])
axes1[2].set_ylabel('PM2.5 (µg/m³)', fontweight='bold', fontsize=10)
axes1[2].legend(loc='upper left', fontsize=12)

# Plot outdoor PM10
sns.lineplot(x='time_range', y='outdoor_pm10', data=df, label='Outdoor PM10', linewidth=2.5, ax=axes1[3], color=colors_figure1[3])
axes1[3].set_ylabel('PM10 (µg/m³)', fontweight='bold', fontsize=10)
axes1[3].legend(loc='upper left', fontsize=12)

# Customize legends
for i in range(4):
    legend = axes1[i].legend(loc='upper left', fontsize=12)
    for text in legend.get_texts():
        text.set_fontweight('bold')

# Set common labels and title
plt.xlabel('Time', fontsize=14)
# Adjust x-ticks to show every 90th value
plt.xticks(ticks=range(0, len(df), 90), labels=[x.split(" ")[0] for x in df['time_range'][::90]], rotation=45, fontweight='bold')

# Adjust layout to prevent cutting off x-labels
plt.tight_layout(pad=3.0)  # Increase padding
fig1.subplots_adjust(bottom=0.15)  # Allocate more space at the bottom

# Show the first figure
plt.show()

plt.figure(3)
# Create second figure with 4 plots  
fig2, axes2 = plt.subplots(4, 1, figsize=(16, 16), sharex=True)

# Plot outdoor no2
sns.lineplot(x='time_range', y='outdoor_no2', data=df, label='Outdoor NO2', linewidth=2.5, ax=axes2[0], color=colors_figure2[0])
axes2[0].set_ylabel('NO2 (µg/m³)', fontweight='bold', fontsize=10)
axes2[0].legend(loc='upper left', fontsize=12)

# Plot outdoor o3
sns.lineplot(x='time_range', y='outdoor_o3', data=df, label='Outdoor O3', linewidth=2.5, ax=axes2[1], color=colors_figure2[1])
axes2[1].set_ylabel('O3 (µg/m³)', fontweight='bold', fontsize=10)
axes2[1].legend(loc='upper left', fontsize=12)

# Plot outdoor CO2
sns.lineplot(x='time_range', y='outdoor_co', data=df, label='Outdoor CO2', linewidth=2.5, ax=axes2[3], color=colors_figure2[3])
axes2[2].set_ylabel('CO2 (µg/m³)', fontweight='bold', fontsize=10)
axes2[2].legend(loc='upper left', fontsize=12)


# Plot outdoor wind speed
sns.lineplot(x='time_range', y='outdoor_wind_speed', data=df, label='Outdoor Wind Speed', linewidth=2.5, ax=axes2[2], color=colors_figure2[2])
axes2[3].set_ylabel('Wind Speed (k/h)', fontweight='bold', fontsize=10)
axes2[3].legend(loc='upper left', fontsize=12)


# Customize legends
for i in range(4):
    legend = axes2[i].legend(loc='upper left', fontsize=12)
    for text in legend.get_texts():
        text.set_fontweight('bold')

# Set common labels and title
plt.xlabel('Time', fontsize=14)
# Adjust x-ticks to show every 90th value
plt.xticks(ticks=range(0, len(df), 90), labels=[x.split(" ")[0] for x in df['time_range'][::90]], rotation=45, fontweight='bold')

# Adjust layout to prevent cutting off x-labels
plt.tight_layout(pad=3.0)  # Increase padding
fig2.subplots_adjust(bottom=0.15)  # Allocate more space at the bottom

# Show the second figure
plt.show()




# ***************** Correlation matrix
plt.figure(4)
# Select relevant columns (exclude 'time_range' and 'city')
relevant_columns = [
    'outdoor_temperature', 'outdoor_humidity', 'outdoor_wind_speed',
    'outdoor_pm2_5', 'outdoor_pm10', 'outdoor_co', 'outdoor_no2',
    'outdoor_o3', 'indoor_humidity', 'indoor_temperature'
]

# Extract the relevant data
data_for_corr = df[relevant_columns]

# Compute the correlation matrix
corr_matrix = data_for_corr.corr()

# Display the correlation matrix
print(corr_matrix)

# Set the size of the plot
plt.figure(figsize=(11, 9))

# Generate a custom diverging colormap
cmap = sns.diverging_palette(220, 10, as_cmap=True)

# Create the heatmap
sns.heatmap(
    corr_matrix, 
    annot=True,        # Annotate cells with correlation coefficients
    fmt=".2f",         # Format the annotations to two decimal places
    cmap=cmap, 
    center=0,          # Center the colormap at zero
    square=True,       # Make each cell square-shaped
    linewidths=.5,     # Width of the lines that will divide each cell
    cbar_kws={"shrink": .75}  # Shrink the color bar
)

# Customize the plot
plt.title('Correlation Matrix of Environmental Variables', fontsize=16)
plt.xticks(rotation=90, ha='right')  # Rotate x-axis labels for better readability
plt.yticks(rotation=0)  # Keep y-axis labels horizontal

# Show the plot
plt.tight_layout()
# plt.show()




# **************** Plot the outdoor and indoor temperatire and humidity 
# Plot temperature
plt.figure(5)
plt.figure(figsize=(2, 2))
plt.plot(df['time_range'], df['indoor_temperature'], label='Indoor Temperature', color='#4E79A7')
plt.plot(df['time_range'], df['outdoor_temperature'], label='Outdoor Temperature', color='#59A14F')
plt.ylabel('Temperature (°C)')
plt.title('Indoor vs Outdoor Temperature')
plt.legend()
plt.grid(True)

# Adjust layout and show plot
plt.tight_layout()
plt.xlabel('Time')
plt.xticks(ticks=range(0, len(df), 90), labels=[x.split(" ")[0] for x in df['time_range'][::90]], rotation=45, fontweight='bold')
plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.2)  # Adjust margins
plt.show()

# Plot humidity
plt.figure(6)
plt.figure(figsize=(2, 2))
plt.plot(df['time_range'], df['indoor_humidity'], label='Indoor Humidity', color='#EDC948')
plt.plot(df['time_range'], df['outdoor_humidity'], label='Outdoor Humidity', color='#F28E2B')
plt.ylabel('Humidity (%)')
plt.title('Indoor vs Outdoor Humidity')
plt.legend()
plt.grid(True)

# Adjust layout and show plot
plt.tight_layout()
plt.xlabel('Time')
plt.xticks(ticks=range(0, len(df), 90), labels=[x.split(" ")[0] for x in df['time_range'][::90]], rotation=45, fontweight='bold')
plt.show()
 