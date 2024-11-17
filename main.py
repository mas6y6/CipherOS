import os
import socket
import sys
sys.path.append(os.getcwd())
import argparse
import traceback
import colorama, websockets, math, shutil, paramiko, progressbar, time, requests, readline
from cipher.api import CipherAPI
import cipher.exceptions as ex
import tarfile
import importlib.util
import os
import tempfile
import shutil

colorama.init()

def hidec():
    print("\033[?25l", end="", flush=True) #hide cursor
    
def showc():
    print("\033[?25h", end="", flush=True) #show cursor
#variables
api = CipherAPI()

if not os.path.exists("data"):
    os.mkdir("data")

if not os.path.exists("data/cache"):
    os.mkdir("data/cache")

if not os.path.exists("data/config"):
    os.mkdir("data/config")

if not os.path.exists("data/cache/packages"):
    os.mkdir("data/cache/packages")
#builtin functions

@api.command()
def exit(args):
    print("Closing CipherOS")
    sys.exit(0)

@api.command(alias=["cd"])
def chdir(args):
    if os.path.isdir(args[0]):
        os.chdir(args[0])
    else:
        print(colorama.Style.BRIGHT+colorama.Fore.RED+f"Error:",args[0],"is a file"+colorama.Fore.RESET+colorama.Style.NORMAL)
    api.pwd = os.getcwd()

@api.command()
def mkdir(args):
    if os.path.exists(args[0]):
        os.mkdir(args[0])
    else:
        print(colorama.Style.BRIGHT+colorama.Fore.RED+f"Error:",args[0],"exists"+colorama.Fore.RESET+colorama.Style.NORMAL)

@api.command(alias=["l"])
def ls(args):
    import os
    import colorama
    if len(args) > 0:
        path = args[0]
    else:
        path = api.pwd
    try:
        raw = os.listdir(path)
    except FileNotFoundError:
        print(f"Error: The directory '{path}' does not exist.")
        return
    except PermissionError:
        print(f"Error: Permission denied to access '{path}'.")
        return
    files = []
    folders = []
    for item in raw:
        full_path = os.path.join(path, item)
        if os.path.isfile(full_path):
            files.append(item)
        elif os.path.isdir(full_path):
            folders.append(item)
    folders.sort()
    files.sort()
    for i in folders:
        print(f"{colorama.Fore.BLUE}{i}/ {colorama.Fore.RESET}")
    for i in files:
        print(f"{colorama.Fore.GREEN}{i} {colorama.Fore.RESET}")


@api.command()
def touch(args):
    if os.path.exists(args[0]):
        open(args[0],"w")
        print("Created file",args[0])
    else:
        print(colorama.Style.BRIGHT+colorama.Fore.RED+f"Error:",args[0],"exists"+colorama.Fore.RESET+colorama.Style.NORMAL)

def _tabcompleter(text, state):
    # Get command options from the API
    command_options = [cmd for cmd in api.commands if cmd.startswith(text)]
    
    # Get file and folder options from the current directory
    current_dir = os.getcwd()
    file_folder_options = [item for item in os.listdir(current_dir) if item.startswith(text)]
    
    # Combine command options and file/folder options
    options = command_options + file_folder_options
    
    # Return the state-th option if it exists
    if state < len(options):
        return options[state]
    else:
        return None

print("Starting CipherOS...")
readline.set_completer(_tabcompleter)
readline.parse_and_bind("tab: complete")
readline.parse_and_bind("set editing-mode emacs")
if not os.path.exists("plugins"):
    os.mkdir("plugins")

if not len(os.listdir(os.path.join(api.starterdir,"plugins"))) == 0:
    for i in os.listdir(os.path.join(api.starterdir,"plugins")):
        api.load_plugin(os.path.join(api.starterdir,"plugins",i))
else:
    print("No plugins found")

print(colorama.Fore.MAGENTA+"Made by @mas6y6 and @malachi196 (on github)")

print(r"""   _______       __              ____  _____
  / ____(_)___  / /_  ___  _____/ __ \/ ___/
 / /   / / __ \/ __ \/ _ \/ ___/ / / /\__ \ 
/ /___/ / /_/ / / / /  __/ /  / /_/ /___/ / 
\____/_/ .___/_/ /_/\___/_/   \____//____/  
      /_/                                   

Project Codename: Paradox"""+colorama.Fore.RESET)

while True:
    try:
        if api.addressconnected == "":
            commandlineinfo = f"{api.currentenvironment} {api.pwd}"
        else:
            commandlineinfo = f"{api.currentenvironment} {api.addressconnected} {api.pwd}"
        _argx = input(commandlineinfo+"> ").split(" ")
        if not _argx[0] == "":
            cmd = _argx[0]
            e = api.run(_argx)
            if e[0] == 404:
                print(colorama.Style.BRIGHT+colorama.Fore.RED+f"Error: Command \"{cmd}\" not found"+colorama.Fore.RESET+colorama.Style.NORMAL)
            elif not e[0] == 0:
                print(colorama.Style.BRIGHT+colorama.Fore.RED+f"Error: Command \"{cmd}\" incountered an error\n"+e[1]+colorama.Fore.RESET+colorama.Style.NORMAL)
            else:
                pass
        else:
            pass
    except (EOFError, KeyboardInterrupt):
        print()
        exit(None)
        break