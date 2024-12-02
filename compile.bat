@echo off
REM Set output directory
set OUTPUT_DIR=dist\windows

REM Create the directory if it doesn't exist
if not exist %OUTPUT_DIR% mkdir %OUTPUT_DIR%

REM Run PyInstaller

pyinstaller main.py --hidden-import=yaml --hidden-import=yaml --exclude-module=pygame --exclude-module=PyQt5 --exclude-module=PySide6 --onefile --icon="./icon.ico" --name="cipheros_test"