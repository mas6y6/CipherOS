import os
import socket
import sys
sys.path.append(os.getcwd())
import argparse
import traceback
import colorama, websockets, math, shutil, paramiko, progressbar, time, requests, platform
from cipher.api import CipherAPI
import cipher.exceptions as ex
import tarfile
import importlib.util
import os
import tempfile
import shutil
from prompt_toolkit import prompt
from prompt_toolkit.completion import Completer, Completion, PathCompleter, WordCompleter
from prompt_toolkit.history import InMemoryHistory
from PyInstaller.utils.hooks import collect_all

datas, binaries, hiddenimports = collect_all('prompt_toolkit')

colorama.init()

def hidec():
    print("\033[?25l", end="", flush=True) #hide cursor
    
def showc():
    print("\033[?25h", end="", flush=True) #show cursor
#variables
api = CipherAPI()
version = 1

def is_running_in_program_files():
    # Get Program Files directories
    program_files = os.environ.get("ProgramFiles")  # C:\Program Files
    program_files_x86 = os.environ.get("ProgramFiles(x86)")  # C:\Program Files (x86)

    # Get the current directory of the script
    current_dir = os.path.abspath(os.getcwd())

    # Check if the current directory starts with either Program Files path
    return current_dir.startswith(program_files) or current_dir.startswith(program_files_x86)

# Example usage
if os.name == "nt":  # Check if running on Windows
    if is_running_in_program_files():
        # Set api.pwd to the home directory
        api.pwd = os.path.expanduser("~")
        print(f"api.pwd set to: {api.pwd}")

        # Set api.starterdir to Roaming\cipheros
        roaming_folder = os.path.join(os.environ.get("APPDATA"), "cipheros")
        os.makedirs(roaming_folder, exist_ok=True)  # Ensure the folder exists
        api.starterdir = roaming_folder
        os.chdir(api.pwd)
        print(f"api.starterdir set to: {api.starterdir}")
    else:
        pass
else:
    pass


if not os.path.exists(os.path.join(api.starterdir,"data")):
    os.mkdir(os.path.join(api.starterdir,"data"))

if not os.path.exists(os.path.join(api.starterdir,"plugins")):
    os.mkdir(os.path.join(api.starterdir,"plugins"))

if not os.path.exists(os.path.join(api.starterdir,"data","cache")):
    os.mkdir(os.path.join(api.starterdir,"data","cache"))

if not os.path.exists(os.path.join(api.starterdir,"data","config")):
    os.mkdir(os.path.join(api.starterdir,"data","config"))

if not os.path.exists(os.path.join(api.starterdir,"data","cache","packages")):
    os.mkdir(os.path.join(api.starterdir,"data","cache","packages"))

if not os.path.exists(os.path.join(api.starterdir,"data","cache","packageswhl")):
    os.mkdir(os.path.join(api.starterdir,"data","cache","packageswhl"))
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
    api.updatecompletions()

@api.command()
def mkdir(args):
    if os.path.exists(args[0]):
        os.mkdir(args[0])
    else:
        print(colorama.Style.BRIGHT+colorama.Fore.RED+f"Error:",args[0],"exists"+colorama.Fore.RESET+colorama.Style.NORMAL)

@api.command(alias=["cls"])
def clear(args):
    print("\033c", end="")

@api.command(alias=["pl"])
def plugins(args):
    if args[0] == "reloadall":
        print("Reloading all plugins")
        for i in list(api.plugins):
            api.disable_plugin(api.plugins[i])
        for i in os.listdir(os.path.join(api.starterdir,"plugins")):
            api.load_plugin(os.path.join(api.starterdir,"plugins",i), api)
        print("Reload complete")
    
    elif args[0] == "disable":
        api.disable_plugin(args[1])
    
    elif args[0] == "enable":
        pass
    
    elif args[0] == "list":
        pass
    
    elif args[0] == "info":
        pass

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
    if not os.path.exists(args[0]):
        open(args[0],"w")
        print("Created file",args[0])
        api.updatecompletions()
    else:
        print(colorama.Style.BRIGHT+colorama.Fore.RED+f"Error:",args[0],"exists"+colorama.Fore.RESET+colorama.Style.NORMAL)

print("Starting CipherOS...")

if not len(os.listdir(os.path.join(api.starterdir,"plugins"))) == 0:
    for i in os.listdir(os.path.join(api.starterdir,"plugins")):
        try:
            api.load_plugin(os.path.join(api.starterdir,"plugins",i),api)
        except:
            print(colorama.Style.BRIGHT+colorama.Fore.RED+f"Error: Plugin '{i}' failed to load\n"+traceback.format_exc()+colorama.Fore.RESET+colorama.Style.NORMAL)
else:
    print("No plugins found")

print(colorama.Fore.MAGENTA+"Made by @mas6y6, @malachi196, and @overo3 (on github)")

print(r"""   _______       __              ____  _____
  / ____(_)___  / /_  ___  _____/ __ \/ ___/
 / /   / / __ \/ __ \/ _ \/ ___/ / / /\__ \ 
/ /___/ / /_/ / / / /  __/ /  / /_/ /___/ / 
\____/_/ .___/_/ /_/\___/_/   \____//____/  
      /_/                                   

Project Codename: Paradox"""+colorama.Fore.RESET)

history = InMemoryHistory()
command_completer = WordCompleter(api.completions, ignore_case=True)
api.updatecompletions()

while True:
    try:
        # Construct command line info
        if api.addressconnected == "":
            commandlineinfo = f"{api.currentenvironment} {api.pwd}"
        else:
            commandlineinfo = f"{api.currentenvironment} {api.addressconnected} {api.pwd}"

        # Use prompt_toolkit to gather input
        command_completer = WordCompleter(api.complations, ignore_case=True)
        user_input = prompt(f"{commandlineinfo}> ",completer=command_completer ,history=history)

        # Split input into arguments
        _argx = user_input.split(" ")

        if not _argx[0] == "":
            cmd = _argx[0]
            e = api.run(_argx)
            
            # Command output handling
            if e[0] == 404:
                print(colorama.Style.BRIGHT + colorama.Fore.RED + f"Error: Command \"{cmd}\" not found" + colorama.Fore.RESET + colorama.Style.NORMAL)
            elif not e[0] == 0:
                print(colorama.Style.BRIGHT + colorama.Fore.RED + f"Error: Command \"{cmd}\" encountered an error\n" + e[1] + colorama.Fore.RESET + colorama.Style.NORMAL)
            else:
                pass
        else:
            pass
    except (EOFError, KeyboardInterrupt):
        print()
        exit(None)
        break
