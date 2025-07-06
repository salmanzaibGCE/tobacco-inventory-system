import PyInstaller.__main__
import os

# Build command
PyInstaller.__main__.run([
    'main.py',
    '--onefile',                    # Single exe file
    '--windowed',                   # No console window
    '--name=Tobacco Inventory System',      # Name of exe
    '--icon=icon.ico',              # App icon (optional)
    '--add-data=modules;modules',   # Include modules folder
    '--clean',                      # Clean build
    '--distpath=dist',              # Output directory
    '--workpath=build',             # Temp build directory
])