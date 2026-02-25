import matplotlib.pyplot as plt
import fastf1
import numpy as np

# 1. Load Lando's Real Data (Abu Dhabi 2024, Stint 1)
session = fastf1.get_session(2024, 'Abu Dhabi', 'R')
session.load(laps=True)
lando_laps = session.laps.pick_drivers('4')
stint1_real = lando_laps[lando_laps['Stint'] == 1].copy()

# Convert LapTime to total seconds
stint1_real['Seconds'] = stint1_real['LapTime'].dt.total_seconds()
real_times = stint1_real['Seconds'].tolist()
laps = stint1_real['LapNumber'].tolist()

# 2. Setup Constants for Projection
base_time = min(real_times[1:]) # Fastest flying lap
stint_len = len(laps)
x_sim = np.array(range(1, stint_len + 1))

# Your Day 5 Physics Logic
fuel_gain = (x_sim - 1) * 0.07
thermal_cliff = np.power(((x_sim - 1) / stint_len), 12)
projected_times = base_time - fuel_gain + thermal_cliff

# 3. Plotting Setup
plt.style.use('dark_background')
fig = plt.figure(figsize=(14, 10))
gs = fig.add_gridspec(2, 2)

# Y-Axis Range: 5 seconds above/below basetime
y_min, y_max = base_time - 5, base_time + 5

# --- TOP LEFT: YOUR PROJECTION (RED) ---
ax1 = fig.add_subplot(gs[0, 0])
ax1.plot(x_sim, projected_times, color='red', linewidth=2, label="Projection")
ax1.set_title("OUR PROJECTION", color='red', fontweight='bold')
ax1.grid(True, color='maroon', linestyle='--', alpha=0.6)
ax1.set_ylim(y_min, y_max)
ax1.set_ylabel("Time (s)")

# --- TOP RIGHT: LANDO'S STINT (YELLOW) ---
ax2 = fig.add_subplot(gs[0, 1])
ax2.plot(laps, real_times, color='yellow', linewidth=2, label="Lando")
ax2.set_title("LANDO'S REAL STINT", color='yellow', fontweight='bold')
ax2.grid(True, color='#8B8000', linestyle='--', alpha=0.6) # Darker yellow/gold
ax2.set_ylim(y_min, y_max)

# --- BOTTOM: COMPARISON (WHITE GRID) ---
ax3 = fig.add_subplot(gs[1, :])
ax3.plot(x_sim, projected_times, color='red', label="Projection", alpha=0.8)
ax3.plot(laps, real_times, color='yellow', label="Lando", alpha=0.8)
ax3.set_title("COMPARISON OVERLAY", color='white', fontweight='bold')
ax3.grid(True, color='white', linestyle=':', alpha=0.3)
ax3.set_ylim(y_min, y_max)
ax3.set_xlabel("Lap Count")
ax3.set_ylabel("Time (s)")
ax3.legend()

plt.tight_layout()
plt.show()