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

# 2. PLOT SETUP (Asymmetric Grid)
plt.style.use('dark_background')
fig = plt.figure(figsize=(14, 10))

# --- GRAPH 1: TOP LEFT (Simulation) ---
ax1 = plt.subplot2grid((2, 2), (0, 0))
ax1.plot(range(len(sim_df)), sim_df['lap_time'], color='red', linewidth=2.5)
ax1.set_title("1. OUR PROJECTION", color='red', fontweight='bold')
ax1.set_ylabel("Lap Time (s)")
ax1.set_ylim(87, 93)
ax1.grid(alpha=0.2)

# --- GRAPH 2: TOP RIGHT (Lando Real) ---
ax2 = plt.subplot2grid((2, 2), (0, 1))
ax2.plot(range(len(real_stint)), real_stint['LapTimeSeconds'], color='gold', linewidth=2.5)
ax2.set_title("2. LANDO REAL TELEMETRY", color='gold', fontweight='bold')
ax2.set_ylabel("Lap Time (s)")
ax2.set_ylim(87, 93)
ax2.grid(alpha=0.2)

# --- GRAPH 3: BOTTOM SPAN (The Overlap) ---
# colspan=2 makes this graph take up the full width of the bottom row
ax3 = plt.subplot2grid((2, 2), (1, 0), colspan=2)
ax3.plot(range(len(real_stint)), real_stint['LapTimeSeconds'], color='gold', label='Lando', linewidth=2.5)
ax3.plot(range(len(sim_df)), sim_df['lap_time'], color='red', label='Sim', linewidth=2.5)
ax3.set_title("3. STRATEGY OVERLAP", fontweight='bold')
ax3.set_xlabel("Laps into Stint")
ax3.set_ylabel("Lap Time (s)")
ax3.set_ylim(87, 93)
ax3.legend()
ax3.grid(alpha=0.2)

# Adjust layout to prevent title/label overlap
plt.tight_layout(pad=4.0)
plt.show()  