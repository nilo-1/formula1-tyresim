import matplotlib.pyplot as plt
import sqlite3
import pandas as pd
import fastf1

# --- 1. DATA COLLECTION ---
fastf1.Cache.enable_cache('f1_cache')
session = fastf1.get_session(2024, 'Abu Dhabi', 'R')
session.load()

# Lando (Driver 4) - Stint 1
lando_laps = session.laps.pick_drivers('4')
lando_laps = lando_laps[lando_laps['Stint'] == 1]
real_times = lando_laps['LapTime'].dt.total_seconds()
real_lap_nums = lando_laps['LapNumber']

# Connect to the Bridge DB
conn = sqlite3.connect('f1_sim.db')
try:
    proj_df = pd.read_sql_query("SELECT lap, lap_time FROM simulation_results", conn)
except (pd.errors.DatabaseError, sqlite3.OperationalError):
    print("❌ ERROR: 'simulation_results' table not found. Run ./f1sim.exe first!")
    conn.close()
    exit()
conn.close()

# --- 2. SMART SCALING & ALIGNMENT ---
# Slicing data from index 1 onwards to eliminate the Lap 1 standing start
# This prevents the Y-axis from zooming out to 130s+ 
proj_lap_clean = proj_df['lap'][1:]
proj_time_clean = proj_df['lap_time'][1:]
real_lap_clean = real_lap_nums[1:]
real_time_clean = real_times[1:]

# Calculate zoom based on the average racing pace (ignoring the spike)
base_ref = real_time_clean.mean() if not real_time_clean.empty else 89.0
y_min, y_max = base_ref - 3, base_ref + 3  # Tight ±3s window

# Determine the final lap N for the X-axis
n_laps = int(max(real_lap_nums.max(), proj_df['lap'].max()))

# --- 3. THE DASHBOARD ---
plt.style.use('dark_background')
fig = plt.figure(figsize=(16, 9))
gs = fig.add_gridspec(2, 2)

# Maximize screen real estate
fig.subplots_adjust(left=0.06, right=0.98, top=0.94, bottom=0.08, hspace=0.3, wspace=0.15)

# Subplot 1: C++ Projection
ax1 = fig.add_subplot(gs[0, 0])
ax1.plot(proj_lap_clean, proj_time_clean, color='#FF0000', linewidth=2)
ax1.set_title("OUR PROJECTION (LAP 2+)", color='red', fontweight='bold')

# Subplot 2: Lando's Real Stint
ax2 = fig.add_subplot(gs[0, 1])
ax2.plot(real_lap_clean, real_time_clean, color='#FFFF00', linewidth=2)
ax2.set_title("LANDO REAL STINT (LAP 2+)", color='yellow', fontweight='bold')

# Subplot 3: Comparison Overlay
ax3 = fig.add_subplot(gs[1, :])
ax3.plot(proj_lap_clean, proj_time_clean, color='#FF0000', label='Sim Projection', alpha=0.9)
ax3.plot(real_lap_clean, real_time_clean, color='#FFFF00', label='Lando Real', alpha=0.7)
ax3.set_title("STRATEGY OVERLAY", color='white', fontweight='bold')
ax3.legend(loc='upper left', frameon=True, facecolor='black', edgecolor='white')

# --- 4. APPLY X (2 to N) AND Y (±3s) SCALING ---
for ax in [ax1, ax2, ax3]:
    ax.set_xlim(2, n_laps) # X-axis from 2 to N
    ax.set_ylim(y_min, y_max) # Y-axis focused on racing pace
    ax.grid(color='gray', linestyle=':', alpha=0.3)
    ax.set_ylabel("Lap Time (s)")

# Create a smoothed version of Lando's times (3-lap rolling average)
lando_smooth = real_time_clean.rolling(window=3, center=True).mean()

# Plot the smooth line instead of the jagged one
ax3.plot(real_lap_clean, lando_smooth, color='#FFFF00', label='Lando (Smoothed)', linewidth=2)

print(f"🏎️ Dashboard Updated. Scaling from Lap 2 to {n_laps} | Y-Range: {y_min:.1f}s - {y_max:.1f}s")
plt.show()