import os
import fastf1
import sqlite3
import pandas as pd

if not os.path.exists('f1_cache'):
    os.makedirs('f1_cache')
fastf1.Cache.enable_cache('f1_cache') 

try:
    print("Connecting to F1 servers for Abu Dhabi 2024...")
    session = fastf1.get_session(2024, 'Abu Dhabi', 'R')
    session.load(telemetry=False, weather=True)

    weather = session.weather_data.iloc[0]
    t_temp = weather['TrackTemp']

    all_laps = session.laps.pick_drivers('4')
    all_laps['LapTimeSeconds'] = all_laps['LapTime'].dt.total_seconds()
    clean_laps = all_laps[(all_laps['LapNumber'] > 1) & (all_laps['LapTimeSeconds'].notna())]
    
    auto_base_time = clean_laps['LapTimeSeconds'].median()

    conn = sqlite3.connect('f1_sim.db')
    cursor = conn.cursor()
    cursor.execute('DROP TABLE IF EXISTS race_weather')
    cursor.execute('CREATE TABLE race_weather (track_temp REAL)')
    cursor.execute('DROP TABLE IF EXISTS race_rules')
    cursor.execute('CREATE TABLE race_rules (track TEXT, stint_len INTEGER, base_time REAL)')

    cursor.execute('INSERT INTO race_weather VALUES (?)', (t_temp,))
    cursor.execute('INSERT INTO race_rules VALUES (?, ?, ?)', ('Abu Dhabi', 25, auto_base_time))

    conn.commit()
    conn.close()
    print(f"--- SUCCESS: Anchored at {auto_base_time:.3f}s ---")

except Exception as e:
    print(f"--- ERROR: {e}")