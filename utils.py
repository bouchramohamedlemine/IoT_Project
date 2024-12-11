def get_action(outdoor_temperature, outdoor_humidity, outdoor_pm2_5, predicted_pm2_5, indoor_temperature, indoor_humidity) -> int:
    """
    Determines the action to open or close the window based on environmental conditions.
    
    Parameters:
    - outdoor_temperature (float): Current outdoor temperature.
    - outdoor_humidity (float): Current outdoor humidity.
    - outdoor_pm10 (float): Current outdoor PM10 level.
    - predicted_pm10 (float): Predicted outdoor PM10 level in the near future.
    - indoor_temperature (float): Current indoor temperature.
    - indoor_humidity (float): Current indoor humidity.
    
    Returns:
    - int: 1 to open the window, or 0 to close it.
    """

    # Thresholds
    max_pm2_5_outdoor = 10  # Safe PM10 level for outdoor air (in µg/m³)
    comfort_temperature_range = (20, 25)  # Comfortable indoor temperature range (°C)
    outdoor_humidity_threshold = 80 

    # Conditions to close the window
    # If PM is high or predicted to be high, close window
    if outdoor_pm2_5 > max_pm2_5_outdoor:
        return -1, "Reduce ventilation: outdoor PM2.5 is high"  # Air quality is too poor
    
    elif predicted_pm2_5 > max_pm2_5_outdoor:
        return -1, "Reduce ventilation: outdoor PM2.5 is predicted to rise"  # Air quality is too poor

    # Temperature considerations 
    if indoor_temperature < comfort_temperature_range[0]:
        # If it's too cold inside, only open the window if outdoor temp is warmer
        if outdoor_temperature > indoor_temperature:
            return 1, "Increase ventilation to warm indoor space"  # Warm indoor space by opening the window
        else:
            return 0, "Indoor conditions are good"  # Keep it closed to retain heat
    elif indoor_temperature > comfort_temperature_range[1]:
        # If it's too warm inside, only open the window if outdoor temp is cooler
        if outdoor_temperature < indoor_temperature:
            return 1, "Increase ventilation to cool indoor space"  # Cool indoor space by opening the window
        else:
            return 0, "Indoor conditions are good"  # Keep it closed to avoid further heating

    # Humidity considerations
    if outdoor_humidity > outdoor_humidity_threshold:
        return -1  # Humidity difference is too large or outdoor humidity is too high

    # If none, do notheing 
    return 0, "Indoor conditions are good"


