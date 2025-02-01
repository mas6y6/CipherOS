#!/bin/bash

#this file should work on UNIX based systems
#tested shells: bash and zsh

set -e

MAGENTA=$(printf '\033[1;35m')
BLUE=$(printf '\033[1;34m')
YELLOW=$(printf '\033[1;33m')
RED=$(printf '\033[1;31m')
GREEN=$(printf '\033[1;32m')
CLEAR=$(printf '\033[0m')

echo "$MAGENTA   _______       __              ____  _____"
echo "  / ____(_)___  / /_  ___  _____/ __ \/ ___/"
echo " / /   / / __ \/ __ \/ _ \/ ___/ / / /\__ \ "
echo "/ /___/ / /_/ / / / /  __/ /  / /_/ /___/ /"
echo "\____/_/ .___/_/ /_/\___/_/   \____//____/"
echo "      /_/                             "
echo "${BLUE}Project Codename: Paradox"
echo
echo "${BLUE}Open source on github: https://github.com/mas6y6/CipherOS"
echo "${YELLOW}Starting CipherOS installation..$CLEAR"
echo
echo "Starting CipherOS installation..."

OS=$(uname -s)
EXECUTABLE="cipheros"
RAW_ARCHITECTURE=$(uname -m)

if [ "$RAW_ARCHITECTURE" = "x86_64" ]; then
    ARCHITECTURE="x64"
elif [ "$RAW_ARCHITECTURE" = "aarch64" ]; then
    ARCHITECTURE="arm64"
elif [ "$RAW_ARCHITECTURE" = "arm64" ]; then
    ARCHITECTURE="arm64"
elif [ "$RAW_ARCHITECTURE" = "i386" ] || [ "$ARCHITECTURE" = "i686" ]; then
    ARCHITECTURE="x32"
else
    echo "Unsupported architecture: $ARCHITECTURE"
    exit 1
fi

echo "System architecture: $ARCHITECTURE"

if [ "$OS" = "Linux" ]; then
    if [ "$ARCHITECTURE" = "x64" ]; then
        GITHUB_REPO_URL="https://github.com/mas6y6/CipherOS/releases/latest/download/linux-x64-executeable"
    elif [ "$ARCHITECTURE" = "arm64" ]; then
        GITHUB_REPO_URL="https://github.com/mas6y6/CipherOS/releases/latest/download/linux-arm64-executeable"
    elif [ "$ARCHITECTURE" = "x32" ]; then
        GITHUB_REPO_URL="https://github.com/mas6y6/CipherOS/releases/latest/download/linux-x32-executeable"
    fi
    INSTALL_DIR="/opt/cipheros"
elif [ "$OS" = "Darwin" ]; then
    if [ "$ARCHITECTURE" = "x64" ]; then
        GITHUB_REPO_URL="https://github.com/mas6y6/CipherOS/releases/latest/download/macos-x64-executeable"
    elif [ "$ARCHITECTURE" = "arm64" ]; then
        GITHUB_REPO_URL="https://github.com/mas6y6/CipherOS/releases/latest/download/macos-arm64-executeable"
    elif [ "$ARCHITECTURE" = "x32" ]; then
        GITHUB_REPO_URL="https://github.com/mas6y6/CipherOS/releases/latest/download/macos-x32-executeable"
    fi
    INSTALL_DIR="/usr/local/cipheros"
else
    echo "Unsupported operating system: $OS"
    exit 1
fi
echo "${BLUE}Running a sudo command this will prompt a password prompt...$CLEAR"

echo "${BLUE}Downloading CipherOS executable...$CLEAR"
mkdir -p "$INSTALL_DIR"

HTTP_STATUS=$(curl -L -s -o "$INSTALL_DIR/$EXECUTABLE" -w "%{http_code}" "$GITHUB_REPO_URL")

if [ "$HTTP_STATUS" -ne 200 ]; then
    echo "${RED}Failed to download CipherOS. HTTP Status: $HTTP_STATUS. Please check the URL or try again later. $CLEAR"
    rm -f "$INSTALL_DIR/$EXECUTABLE"
    exit 1
fi

if [ $? -ne 0 ]; then
    echo "${RED}Failed to download CipherOS. Please check your network or the URL. $CLEAR"
    exit 1
fi

sudo chmod +x "$INSTALL_DIR/$EXECUTABLE"

echo "${BLUE}Creating symbolic link...$CLEAR"
sudo ln -sf "$INSTALL_DIR/$EXECUTABLE" /usr/local/bin/$EXECUTABLE

echo "${GREEN}CipherOS installation complete! You can run CipherOS by typing 'cipheros' in the terminal.$CLEAR"
