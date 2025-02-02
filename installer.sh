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
INSTALL_DIR="$HOME/.local/bin/cipheros"
EXECUTABLE="cipheros"
RAW_ARCHITECTURE=$(uname -m)

# get system architecture
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
elif [ "$OS" = "Darwin" ]; then
    if [ "$ARCHITECTURE" = "x64" ]; then
        GITHUB_REPO_URL="https://github.com/mas6y6/CipherOS/releases/latest/download/macos-x64-executeable"
    elif [ "$ARCHITECTURE" = "arm64" ]; then
        GITHUB_REPO_URL="https://github.com/mas6y6/CipherOS/releases/latest/download/macos-arm64-executeable"
    elif [ "$ARCHITECTURE" = "x32" ]; then
        GITHUB_REPO_URL="https://github.com/mas6y6/CipherOS/releases/latest/download/macos-x32-executeable"
    fi
else
    echo "Unsupported operating system: $OS"
    exit 1
fi
mkdir -p "$INSTALL_DIR"

if [ -e $INSTALL_DIR/$EXECUTABLE ] ; then
    echo "Found existing \"cipheros\" binary. If you wish to reinstall it, please run the following line and rerun the install script again."
    echo "rm -rf $INSTALL_DIR"
    exit 1
fi

echo "${BLUE}Downloading CipherOS executable...$CLEAR"
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

chmod +x "$INSTALL_DIR/$EXECUTABLE"

if [[ ":$PATH:" != *":$INSTALL_DIR:"* ]] ; then
    echo "Adding $INSTALL_DIR to \$PATH variable."
    PATHPERSISTENCENOTE="# This line is used to add \"cipheros\" to \$PATH"
    if [[ $SHELL == *bash ]] ; then
        echo $PATHPERSISTENCENOTE >> $HOME/.bashrc
        echo "PATH=$INSTALL_DIR:\$PATH" >> $HOME/.bashrc
    elif [[ $SHELL == *zsh ]] ; then
        echo $PATHPERSISTENCENOTE >> $HOME/.zshrc
        echo "PATH=$INSTALL_DIR:\$PATH" >> $HOME/.zshrc
    else
        echo $RED"Your shell is not supported yet."
        echo "Please add the following line to the file for your shell, that equals the \".bashrc\" file for bash."
        echo $YELLOW"PATH=$INSTALL_DIR:\$PATH"$CLEAR
    fi
fi

PATH=$INSTALL_DIR:$PATH
export PATH

echo "${BLUE}Creating symbolic link...$CLEAR"
#ln -sf "$INSTALL_DIR/$EXECUTABLE" /usr/local/bin/$EXECUTABLE

echo "${GREEN}CipherOS installation complete! You can run CipherOS by typing 'cipheros' in the terminal.$CLEAR"
