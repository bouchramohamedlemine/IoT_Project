"""
    Predict the PM2.5 concentration after 15 minutes.
"""

import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import GridSearchCV
import numpy as np 
from sklearn.model_selection import train_test_split
import joblib
import matplotlib.pyplot as plt

# Load the data from the CSV file
df = pd.read_csv('merged_data.csv')
print(f"Average PM2.5 = {df['outdoor_pm2_5'].mean()}")

X = []
y = []

# Iterate through the dataset, use the past observation for prediction
for i in range(1, len(df)):
    # Create a list with the previous values for each feature
    X.append(df.iloc[i-1:i][['outdoor_wind_speed', 'outdoor_pm2_5', 'outdoor_pm10', 'outdoor_co', 'outdoor_no2', 'outdoor_o3'
                             ]].values.flatten())
                             
    # Use the target value for prediction at index `i`
    y.append(df.iloc[i]['outdoor_pm2_5'])


# Convert X and y into numpy arrays
X = np.array(X)
y = np.array(y)

# Check the resulting arrays
print(X[6], y[6])

 
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)
print(X_train.shape, y_train.shape)


# ********** Train the Random Forest model
param_grid = {
    'n_estimators': [50, 100, 200],
    'min_samples_leaf': [1, 2, 4, 6]
}

# Set up GridSearchCV
grid_search = GridSearchCV(
    estimator=RandomForestRegressor(random_state=42),
    param_grid=param_grid,
    cv=5,  # 5-fold cross-validation
)

# Perform the grid search
grid_search.fit(X_train, y_train)
print(f"Best Parameters: {grid_search.best_params_}")

model = grid_search.best_estimator_

# Evaluate the model
y_pred = model.predict(X_test)
mae = mean_absolute_error(y_test, y_pred)
print(f'Mean Absolute Error: {mae}')

# Save the model
joblib.dump(model, "random_forest_model.joblib")

# Create the plot
plt.figure(figsize=(12, 6))
plt.plot(y_test, label='Actual Values', color='blue', linestyle='-', linewidth=2)
plt.plot(y_pred, label='Predicted Values', color='red', linestyle='--', linewidth=2)

# Add titles and labels
plt.title('Actual vs Predicted PM2.5', fontsize=16)
plt.xlabel('Sample Index', fontsize=14)
plt.ylabel('PM2.5 (µg/m³)', fontsize=14)
plt.legend(fontsize=12, loc='best')

# Add grid for better readability
plt.grid(True)

# Show the plot
plt.tight_layout()
plt.show()

 
