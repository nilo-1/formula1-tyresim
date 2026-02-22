import fastf1
import sqlite3

try:
    print("Connecting to F1 servers... this may take a moment.")
    # Fetch 2024 Abu Dhabi GP Race data
    session = fastf1.get_session(2024, 'Abu Dhabi', 'R')
    session.load(telemetry=False, weather=True)

    # Grab the first row of weather data
    weather = session.weather_data.iloc[0]
    t_temp = weather['TrackTemp']
    a_temp = weather['AirTemp']
    hum = weather['Humidity']

    # Connect to the database we made with the Mega-Command
    conn = sqlite3.connect('f1_sim.db')
    cursor = conn.cursor()

    # Inject the real-world values into your 'race_weather' table
    cursor.execute('''
        INSERT INTO race_weather (track_temp, air_temp, humidity, session_name)
        VALUES (?, ?, ?, ?)
    ''', (t_temp, a_temp, hum, 'Abu Dhabi 2024'))

    conn.commit()
    conn.close()
    print(f"--- SUCCESS ---")
    print(f"Track Temp: {t_temp}°C | Air Temp: {a_temp}°C | Humidity: {hum}%")
    print("Data injected into f1_sim.db successfully.")

except Exception as e:
    print("--- ERROR ---")
    print(f"Something went wrong: {e}")

#
