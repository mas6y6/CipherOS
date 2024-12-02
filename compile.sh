#!/bin/bash
# Set output directory
OUTPUT_DIR="dist/linux"
if [[ "$(uname)" == "Darwin" ]]; then
  OUTPUT_DIR="dist/macos"
fi

# Create the directory if it doesn't exist
mkdir -p "$OUTPUT_DIR"

# Run PyInstaller

pyinstaller main.py --distpath %OUTPUT_DIR% --hidden-import=yaml --hidden-import=yaml --exclude-module=pygame --exclude-module=PyQt5 --exclude-module=PySide6 --exclude-module=cipher --onefile --icon="./icon.ico" --name="cipheros_build" 