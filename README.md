🏎️ F1 Race Strategy & Tyre Degradation Simulator

A high-performance simulation suite designed to model realistic Formula 1 tyre wear and lap time evolution by bridging real-world telemetry with a custom C++ physics engine.

🛠️ The Tech Stack

Data Scout: Python 3.14 + FastF1 API (Extracting real-world telemetry and lap data).

The Bridge: SQLite3 (Relational database for storing historical race data and compound coefficients).

Physics Engine: C++17 (MSYS2/GCC) (Core simulation logic, fuel weight scaling, and non-linear tyre wear curves).

Dashboard: Matplotlib (Triple-graph strategy visualization).📈 

Current Physics ImplementationThe simulator utilizes a V-Curve (Polynomial/Power) model to represent the life of a tyre stint:

- Warm-up Phase: Initial lap time penalty for cold tyres.
- Stable Phase: The "sweet spot" where fuel burn-off compensates for rubber wear.
- Degradation Phase: Exponential lap time increase as the tyre carcass reaches its thermal limit.

Laptime = BaseTime - (Lap \times 0.07) + (\frac{Lap}{LifeLimit})^{12}

🚀 Getting Started (1-Step Setup)This project is optimized for the MSYS2 UCRT64 environment. To install all dependencies, compile the engine, and initialize the database in one go, 

run:chmod +x setup.sh && ./setup.sh (in bahs terminal on VSCODE)

Manual Execution

If you prefer to run the components individually:

- Extract Telemetry: /ucrt64/bin/python fetch_data.py
- Run Simulation: ./f1sim.exe
- View Dashboard: /ucrt64/bin/python plot_stint.py

💻 Local Development

VS Code Build ShortcutShortcut: Ctrl + Shift + B

Configuration: The project is set up to link time.cpp and tyredegsim.cpp automatically.

Task Setup: Ensure tasks.json uses ${fileDirname}/*.cpp in the args section to support multi-file compilation.

Dependencies

The setup.sh script handles these, but for reference:

- mingw-w64-ucrt-x86_64-sqlite3
- mingw-w64-ucrt-x86_64-python-matplotlib
- mingw-w64-ucrt-x86_64-python-pandas
- fastf1 (Installed via pip with --break-system-packages)

📂 Project Structure

- tyredegsim.cpp: Main physics engine logic.
- time.cpp/h: Time conversion and formatting utilities.
- fetch_data.py: Python script to pull Lando's Abu Dhabi 2024 data.
- plot_stint.py: The "Pit Wall" dashboard with 3-graph layout.
- f1_sim.db: SQLite database acting as the bridge between languages.