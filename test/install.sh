#!/bin/bash

echo "   _______       __              ____  _____"
echo "  / ____(_)___  / /_  ___  _____/ __ \/ ___/"
echo " / /   / / __ \/ __ \/ _ \/ ___/ / / /\__ \ "
echo "/ /___/ / /_/ / / / /  __/ /  / /_/ /___/ / "
echo "\____/_/ .___/_/ /_/\___/_/   \____//____/  "
echo "       /_/                                  "
echo
echo "Project: Paradox"
echo "Installer for macOS / Linux"

if ! command -v curl &> /dev/null; then
    echo "curl could not be found, please install it first."
    exit 1
fi

if [[ "$(uname -s)" == "Darwin" ]]; then
    echo "Downloading macOS build..."
    curl -f -O https://raw.githubusercontent.com/mas6y6/CipherOS/refs/heads/main/macos/cipher
    if [[ $? -ne 0 ]]; then
        echo "Failed to download macOS build."
        exit 1
    fi
elif [[ "$(uname -s)" == "Linux" ]]; then
    echo "Downloading Linux build..."
    curl -f -O https://raw.githubusercontent.com/mas6y6/CipherOS/refs/heads/main/macos/cipher
    if [[ $? -ne 0 ]]; then
        echo "Failed to download Linux build."
        exit 1
    fi
else
    echo "Unsupported OS: $(uname -s)"
    exit 1
fi

chmod +x cipher

echo "Download complete and file is now executable."
