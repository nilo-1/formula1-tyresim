import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import fastf1

# 1. LOAD DATA
conn = sqlite3.connect('f1_sim.db')
sim_df = pd.read_sql_query("SELECT * FROM simulation_results", conn)

session = fastf1.get_session(2024, 'Abu Dhabi', 'R')
session.load(telemetry=False, weather=False)
real_laps = session.laps.pick_drivers('4')
real_laps['LapTimeSeconds'] = real_laps['LapTime'].dt.total_seconds()

# Clean slice for one-point alignment
real_stint = real_laps[real_laps['Stint'] == 1].iloc[3:]

# 2. PLOT SETUP (3 Subplots)
plt.style.use('dark_background')
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 15))
plt.subplots_adjust(hspace=0.4)

# --- GRAPH 1: OUR PROJECTION ---
ax1.plot(range(len(sim_df)), sim_df['lap_time'], color='red', linewidth=2.5)
ax1.set_title("1. Physics Simulation Projection", color='red', fontweight='bold')
ax1.set_ylabel("Lap Time (s)")
ax1.set_ylim(87, 93)
ax1.grid(alpha=0.2)

# --- GRAPH 2: LANDO'S REAL TIME ---
ax2.plot(range(len(real_stint)), real_stint['LapTimeSeconds'], color='gold', linewidth=2.5)
ax2.set_title("2. Lando Norris Real Telemetry", color='gold', fontweight='bold')
ax2.set_ylabel("Lap Time (s)")
ax2.set_ylim(87, 93)
ax2.grid(alpha=0.2)

# --- GRAPH 3: THE OVERLAP ---
ax3.plot(range(len(real_stint)), real_stint['LapTimeSeconds'], color='gold', label='Lando', linewidth=2.5)
ax3.plot(range(len(sim_df)), sim_df['lap_time'], color='red', label='Sim', linewidth=2.5) # Solid line now
ax3.set_title("3. Strategy Overlay", fontweight='bold')
ax3.set_xlabel("Laps into Stint")
ax3.set_ylabel("Lap Time (s)")
ax3.set_ylim(87, 93)
ax3.legend()
ax3.grid(alpha=0.2)

plt.show()