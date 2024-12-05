#!/bin/bash

echo "\033[1;35m   _______       __              ____  _____\033[0m"
echo "\033[1;35m  / ____(_)___  / /_  ___  _____/ __ \/ ___/\033[0m"
echo "\033[1;35m / /   / / __ \/ __ \/ _ \/ ___/ / / /\__ \ \033[0m"
echo "\033[1;35m/ /___/ / /_/ / / / /  __/ /  / /_/ /___/ / \033[0m"
echo "\033[1;35m\____/_/ .___/_/ /_/\___/_/   \____//____/\033[0m"
echo "\033[1;35m      /_/                                   \033[0m"
echo "\033[1;35mProject Codename: Paradox\033[0m"
echo
echo "\033[1;34mOpen source on github: https://github.com/mas6y6/CipherOS\033[0m"
echo "\033[1;33mStarting CipherOS installation...\033[0m"
echo
echo "Starting CipherOS installation..."

OS=$(uname -s)
EXECUTABLE="cipheros"
RAW_ARCHITECTURE=$(uname -m)

if [ "$RAW_ARCHITECTURE" = "x86_64" ]; then
    ARCHITECTURE="x64"
elif [ "$RAW_ARCHITECTURE" = "aarch64" ]; then
    ARCHITECTURE="arm64"
elif [ "$RAW_ARCHITECTURE" = "i386" ] || [ "$ARCHITECTURE" = "i686" ]; then
    ARCHITECTURE="x32"
else
    echo "Unsupported architecture: $ARCHITECTURE"
    exit 1
fi

echo "System architecture: $ARCHITECTURE"

if [ "$(id -u)" -ne 0 ]; then
    echo "\033[1;31mPlease run as root using sudo.\033[0m"
    exit 1
fi

if [ "$OS" = "Linux" ]; then
    if [ "$ARCHITECTURE" = "x64" ]; then
        GITHUB_REPO_URL="https://github.com/username/CipherOS/releases/latest/download/linux-x64-executable"
    elif [ "$ARCHITECTURE" = "arm64" ]; then
        GITHUB_REPO_URL="https://github.com/username/CipherOS/releases/latest/download/linux-arm64-executable"
    elif [ "$ARCHITECTURE" = "x32" ]; then
        GITHUB_REPO_URL="https://github.com/username/CipherOS/releases/latest/download/linux-x32-executable"
    fi
    INSTALL_DIR="/opt/cipheros"
elif [ "$OS" = "Darwin" ]; then
    if [ "$ARCHITECTURE" = "x64" ]; then
        GITHUB_REPO_URL="https://github.com/username/CipherOS/releases/latest/download/macos-x64-executable"
    elif [ "$ARCHITECTURE" = "arm64" ]; then
        GITHUB_REPO_URL="https://github.com/username/CipherOS/releases/latest/download/macos-arm64-executable"
    fi
    INSTALL_DIR="/usr/local/cipheros"
else
    echo "Unsupported operating system: $OS"
    exit 1
fi
echo "\033[1;34mDownloading CipherOS executable...\033[0m"
mkdir -p "$INSTALL_DIR"

curl -L "$GITHUB_REPO_URL" -o "$INSTALL_DIR/$EXECUTABLE"
if [ $? -ne 0 ]; then
    echo "\033[1;31mFailed to download CipherOS. Please check your network or the URL.\033[0m"
    exit 1
fi

chmod +x "$INSTALL_DIR/$EXECUTABLE"

echo "\033[1;34mCreating symbolic link...\033[0m"
ln -sf "$INSTALL_DIR/$EXECUTABLE" /usr/local/bin/$EXECUTABLE

echo "\033[1;32mCipherOS installation complete! You can run CipherOS by typing 'cipheros' in the terminal.\033[0m"