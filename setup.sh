#!/bin/bash

echo "🏎️ Setting up F1 Strategy Sim Environment..."

# 1. Update and install system dependencies via pacman
echo "📦 Installing System & Python Binaries..."
pacman -S --needed --noconfirm \
    mingw-w64-ucrt-x86_64-python-matplotlib \
    mingw-w64-ucrt-x86_64-python-pandas \
    mingw-w64-ucrt-x86_64-python-scipy \
    mingw-w64-ucrt-x86_64-python-pydantic \
    mingw-w64-ucrt-x86_64-sqlite3 \
    mingw-w64-ucrt-x86_64-toolchain

# 2. Install FastF1 via pip
echo "🐍 Installing FastF1 API..."
/ucrt64/bin/python -m pip install fastf1 --break-system-packages

echo "✅ Setup Complete! You can now run the simulation."