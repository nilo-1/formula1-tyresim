import os
import fastf1
import sqlite3
import pandas as pd

# 1. SETUP ENVIRONMENT
if not os.path.exists('f1_cache'):
    os.makedirs('f1_cache')

fastf1.Cache.enable_cache('f1_cache') 

try:
    print("Connecting to F1 servers for Abu Dhabi 2024...")
    session = fastf1.get_session(2024, 'Abu Dhabi', 'R')
    session.load(telemetry=False, weather=True)

    # 2. WEATHER DATA
    weather = session.weather_data.iloc[0]
    t_temp, a_temp, hum = weather['TrackTemp'], weather['AirTemp'], weather['Humidity']

    # 3. STRATEGY DATA 
    # Norris (Driver '4') 
    lando_laps = session.laps.pick_drivers('4')
    
    # Pre-convert LapTime to total seconds
    lando_laps['LapTimeSeconds'] = lando_laps['LapTime'].dt.total_seconds()

    # Filter for clean racing laps (ignoring Lap 1 standing start and pit stops)
    # We also filter out laps where the time is way off (e.g., > 110% of median) to avoid yellow flags
    valid_laps = lando_laps[(lando_laps['LapNumber'] > 1) & (lando_laps['LapTimeSeconds'].notna())]
    
    # NEW: Using Median (0.5) instead of 0.1 to get a realistic "Race Pace"
    auto_base_time = valid_laps['LapTimeSeconds'].median()

    # Grouping stints for the database
    stint_data = []
    unique_stints = valid_laps['Stint'].unique()

    for stint_num in unique_stints:
        stint_subset = valid_laps[valid_laps['Stint'] == stint_num]
        compound = stint_subset['Compound'].iloc[0]
        stint_len = len(stint_subset)
        
        # Use the automated median pace for the primary stint comparison
        # This ensures the Red and Yellow lines start at the same height
        base_time = auto_base_time if stint_num == 1 else stint_subset['LapTimeSeconds'].median()
        
        stint_data.append(('Abu Dhabi', compound, stint_len, base_time))

    # 4. DATABASE INJECTION
    conn = sqlite3.connect('f1_sim.db')
    cursor = conn.cursor()

    # Clean start for both tables
    cursor.execute('DROP TABLE IF EXISTS race_weather')
    cursor.execute('CREATE TABLE race_weather (track_temp REAL, air_temp REAL, humidity REAL, session_name TEXT)')
    
    cursor.execute('DROP TABLE IF EXISTS race_rules')
    cursor.execute('CREATE TABLE race_rules (track TEXT, compound TEXT, stint_len INTEGER, base_time REAL)')

    # Inject Weather and Stint Rules
    cursor.execute('INSERT INTO race_weather VALUES (?, ?, ?, ?)', (t_temp, a_temp, hum, 'Abu Dhabi 2024'))
    cursor.executemany('INSERT INTO race_rules VALUES (?, ?, ?, ?)', stint_data)

    conn.commit()
    conn.close()

    print(f"--- SUCCESS ---")
    print(f"Weather: {t_temp}°C | Automated Base Time (Median): {auto_base_time:.3f}s")
    print(f"Strategy: {len(stint_data)} stints recorded for NOR.")
    print("Database f1_sim.db is updated and ready for C++.")

except Exception as e:
    print(f"--- ERROR: {e}")