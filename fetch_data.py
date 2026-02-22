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
    # Norris (Driver '4') - Ignoring Lap 1 standing start for better baseline
    winner_laps = session.laps.pick_drivers('4')
    
    # Pre-convert LapTime to total seconds to avoid Timedelta syntax errors
    winner_laps['LapTimeSeconds'] = winner_laps['LapTime'].dt.total_seconds()

    # Filter out Lap 1 and rows without lap times
    valid_laps = winner_laps[(winner_laps['LapNumber'] > 1) & (winner_laps['LapTimeSeconds'].notna())]

    # Grouping using simple Pandas logic
    stint_data = []
    unique_stints = valid_laps['Stint'].unique()

    for stint_num in unique_stints:
        stint_subset = valid_laps[valid_laps['Stint'] == stint_num]
        compound = stint_subset['Compound'].iloc[0]
        stint_len = len(stint_subset)
        base_time = stint_subset['LapTimeSeconds'].min()
        
        stint_data.append(('Abu Dhabi', compound, stint_len, base_time))

    # 4. DATABASE INJECTION
    conn = sqlite3.connect('f1_sim.db')
    cursor = conn.cursor()

    # Clean start for both tables
    cursor.execute('DROP TABLE IF EXISTS race_weather')
    cursor.execute('CREATE TABLE race_weather (track_temp REAL, air_temp REAL, humidity REAL, session_name TEXT)')
    
    cursor.execute('DROP TABLE IF EXISTS race_rules')
    cursor.execute('CREATE TABLE race_rules (track TEXT, compound TEXT, stint_len INTEGER, base_time REAL)')

    # Inject
    cursor.execute('INSERT INTO race_weather VALUES (?, ?, ?, ?)', (t_temp, a_temp, hum, 'Abu Dhabi 2024'))
    cursor.executemany('INSERT INTO race_rules VALUES (?, ?, ?, ?)', stint_data)

    conn.commit()
    conn.close()

    print(f"--- SUCCESS ---")
    print(f"Weather: {t_temp}°C | Strategy: {len(stint_data)} stints recorded for NOR.")
    print("Database f1_sim.db is updated and ready.")

except Exception as e:
    print(f"--- ERROR: {e}")