import os
import socket
import sys
sys.path.append(os.getcwd())
import argparse
import traceback
import colorama, websockets, math, shutil, paramiko, progressbar, time, requests
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

colorama.init()

def hidec():
    print("\033[?25l", end="", flush=True) #hide cursor
    
def showc():
    print("\033[?25h", end="", flush=True) #show cursor
#variables
api = CipherAPI()
version = 1

if not os.path.exists("data"):
    os.mkdir("data")

if not os.path.exists("data/cache"):
    os.mkdir("data/cache")

if not os.path.exists("data/config"):
    os.mkdir("data/config")

if not os.path.exists("data/cache/packages"):
    os.mkdir("data/cache/packages")

if not os.path.exists("data/cache/packageswhl"):
    os.mkdir("data/cache/packageswhl")
#builtin functions

complations = []

def updatecomplations():
    for i in os.listdir(api.pwd):
        complations.append(i)
    
    for i in api.commands:
        complations.append(i)

@api.command()
def exit(args):
    print("Closing CipherOS")
    sys.exit(0)

@api.command(alias=["cd"])
def chdir(args):
    updatecomplations()
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

@api.command(alias=["cls"])
def clear(args):
    print("\033c", end="")

@api.command(alias=["pl"])
def plugins(args):
    if args[0] == "reloadall":
        print("Reloading all plugins")
        for i in api.plugins:
            api.disable_plugin(i)
        for i in os.listdir(api.starterdir):
            api.load_plugin(i,api)
    
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
    if os.path.exists(args[0]):
        open(args[0],"w")
        print("Created file",args[0])
    else:
        print(colorama.Style.BRIGHT+colorama.Fore.RED+f"Error:",args[0],"exists"+colorama.Fore.RESET+colorama.Style.NORMAL)

print("Starting CipherOS...")
if not os.path.exists("plugins"):
    os.mkdir("plugins")

if not len(os.listdir(os.path.join(api.starterdir,"plugins"))) == 0:
    for i in os.listdir(os.path.join(api.starterdir,"plugins")):
        try:
            api.load_plugin(os.path.join(api.starterdir,"plugins",i),api)
        except:
            print(colorama.Style.BRIGHT+colorama.Fore.RED+f"Error: Plugin '{i}' failed to load\n"+traceback.format_exc()+colorama.Fore.RESET+colorama.Style.NORMAL)
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
updatecomplations()

history = InMemoryHistory()

command_completer = WordCompleter(complations, ignore_case=True)
path_completer = PathCompleter()

while True:
    try:
        # Construct command line info
        if api.addressconnected == "":
            commandlineinfo = f"{api.currentenvironment} {api.pwd}"
        else:
            commandlineinfo = f"{api.currentenvironment} {api.addressconnected} {api.pwd}"

        # Use prompt_toolkit to gather input
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
