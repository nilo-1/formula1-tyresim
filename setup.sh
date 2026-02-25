#!/bin/bash

echo "🏎️  F1 Strategy Sim: Full Engine & Dashboard Setup"
echo "--------------------------------------------------"

# 1. INSTALL SYSTEM DEPENDENCIES
echo "📦 Installing System & Python Binaries (UCRT64)..."
pacman -S --needed --noconfirm \
    mingw-w64-ucrt-x86_64-python-matplotlib \
    mingw-w64-ucrt-x86_64-python-pandas \
    mingw-w64-ucrt-x86_64-python-scipy \
    mingw-w64-ucrt-x86_64-python-pydantic \
    mingw-w64-ucrt-x86_64-sqlite3 \
    mingw-w64-ucrt-x86_64-toolchain

# 2. INSTALL FASTF1
echo "🐍 Ensuring FastF1 is installed..."
/ucrt64/bin/python -m pip install fastf1 --break-system-packages --quiet

# 3. COMPILE C++ PHYSICS ENGINE
echo "⚙️  Compiling C++ Physics Engine (f1sim.exe)..."
# Using the UCRT64 g++ directly to ensure it links lsqlite3 correctly
g++ -g tyredegsim.cpp time.cpp -o f1sim.exe -lsqlite3

if [ $? -eq 0 ]; then
    echo "✅ C++ Engine compiled successfully."
else
    echo "❌ Error: Compilation failed. Check if tyredegsim.cpp and time.cpp exist."
    exit 1
fi

# 4. DATABASE INITIALIZATION
DB_FILE="f1_sim.db"
if [ ! -f "$DB_FILE" ]; then
    echo "🗄️  Database not found. Fetching Lando's Abu Dhabi telemetry..."
    /ucrt64/bin/python fetch_data.py
    echo "✅ Database initialized."
else
    echo "✨ Database already exists. Skipping fetch."
fi

echo "--------------------------------------------------"
echo "🏁 SUCCESS! Your environment is ready."
echo "   1. Run Simulation:  ./f1sim.exe"
echo "   2. View Dashboard:  python plot_stint.py"