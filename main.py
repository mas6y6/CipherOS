import os
import socket
import sys
sys.path.append(os.getcwd())
import argparse
import traceback
import colorama, websockets, math, shutil, paramiko, progressbar, time, requests, platform, pyinputplus, urllib3
import tarfile
import importlib.util
import tempfile
import shutil
from prompt_toolkit import prompt
from prompt_toolkit.completion import Completer, Completion, PathCompleter, WordCompleter
from prompt_toolkit.history import InMemoryHistory

colorama.init()
running_on_mac = False #Meant as the cipher library is not installed
macpwd = None
macapistarter = None

import urllib.request
import progressbar
import os
pbar = None
def show_progress(block_num, block_size, total_size):
    global pbar
    if pbar is None:
        pbar = progressbar.ProgressBar(widgets=[progressbar.Percentage()," ",progressbar.Bar(left="[",right="]")," ",progressbar.AbsoluteETA()],maxval=total_size)
        pbar.start()

    downloaded = block_num * block_size
    if downloaded < total_size:
        pbar.update(downloaded)
    else:
        pbar.finish()
        pbar = None

if os.name == "posix":
    if os.getcwd() == os.path.expanduser("~"):
        macpwd = os.path.expanduser("~")
        os.chdir(macpwd)
        if not os.path.exists(os.path.join(os.path.expanduser("~"),"CipherOS")):
            os.mkdir(os.path.join(os.path.expanduser("~"),"CipherOS"))
        macapistarter = os.path.join(os.path.expanduser("~"),"CipherOS")
        if not os.path.exists(os.path.join(os.path.expanduser("~"),"CipherOS","cipher")):
            print("Warning the \"cipher\" library is not installed and its required to run")
            print("Do you want to download the \"cipher\" library?")
            print()
            print("You cannot install it using \"pip\" as its not available on pypi.org")
            print()
            q = pyinputplus.inputYesNo("Would you like to continue? (Y/n): ")
            if q:
                urllib.request.urlretrieve("https://codeload.github.com/mas6y6/CipherOS/zip/refs/heads/main",os.path.join(os.path.expanduser("~"),"CipherOS","cache.zip"), show_progress)
            else:
                print("You can download the \"cipher\" folder from github https://github.com/mas6y6/CipherOS/archive")
                sys.exit()
        

from cipher.api import CipherAPI
import cipher.exceptions as ex

api = CipherAPI()

if running_on_mac:
    # To fix the path plugins and data folders being created in the ~ folder
    #
    # The plugins folder must be in the ~/CipherOS/plugins if you are using linux or macOS
    #
    # macOS is just a linux distro so :)
    api.pwd = macpwd
    api.starterdir = macapistarter

sys.path.append(os.path.join(api.starterdir,"plugins"))
sys.path.append(os.path.join(api.starterdir,"data","cache","packages"))

def hidec():
    print("\033[?25l", end="", flush=True) #hide cursor
    
def showc():
    print("\033[?25h", end="", flush=True) #show cursor

def printerror(msg):
    print(colorama.Style.BRIGHT+colorama.Fore.RED+msg+colorama.Fore.RESET+colorama.Style.NORMAL)
#variables
version = 1

def is_running_in_program_files():
    program_files = os.environ.get("ProgramFiles")  # C:\Program Files
    program_files_x86 = os.environ.get("ProgramFiles(x86)")  # C:\Program Files (x86)
    current_dir = os.path.abspath(os.getcwd())
    return current_dir.startswith(program_files) or current_dir.startswith(program_files_x86)

if os.name == "nt":
    if is_running_in_program_files():
        api.pwd = os.path.expanduser("~")
        roaming_folder = os.path.join(os.environ.get("APPDATA"), "cipheros")
        os.makedirs(roaming_folder, exist_ok=True)
        api.starterdir = roaming_folder
        os.chdir(api.pwd)
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
        printerror(f"Error: {args[0]} is a file")
    api.pwd = os.getcwd()
    api.updatecompletions()

@api.command()
def mkdir(args):
    if os.path.exists(args[0]):
        os.mkdir(args[0])
    else:
        printerror(f"Error: {args[0]} exists")

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

@api.command(alias=["list","l"])
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
        printerror(f"Error: The directory '{path}' does not exist.")
        return
    except PermissionError:
        printerror(f"Error: Permission denied to access '{path}'.")
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

@api.command(alias=["rm"])
def remove(args):
    try:
        os.remove(os.path.join(api.starterdir,args[0]))
    except PermissionError:
        printerror(f"Error: Permission to delete '{args[0]}' denied")
    except FileNotFoundError:
        printerror(f"Error: '{args[0]}' does not exist.")

print("Starting CipherOS...")

if not len(os.listdir(os.path.join(api.pwd,"plugins"))) == 0:
    for i in os.listdir(os.path.join(api.pwd,"plugins")):
        try:
            api.load_plugin(os.path.join(api.pwd,"plugins",i),api)
        except:
            printerror(f"Error: Plugin '{i}' failed to load\n")
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
api.updatecompletions()

while True:
    try:
        # Construct command line info
        if api.addressconnected == "":
            commandlineinfo = f"{api.currentenvironment} {api.pwd}"
        else:
            commandlineinfo = f"{api.currentenvironment} {api.addressconnected} {api.pwd}"

        # Use prompt_toolkit to gather input
        command_completer = WordCompleter(api.completions, ignore_case=True)
        user_input = prompt(f"{commandlineinfo}> ",completer=command_completer ,history=history)

        # Split input into arguments
        _argx = user_input.split(" ")

        if not _argx[0] == "":
            cmd = _argx[0]
            e = api.run(_argx)
            
            # Command output handling
            if e[0] == 404:
                printerror(f"Error: Command \"{cmd}\" not found")
            elif not e[0] == 0:
                printerror(f"Error: Command \"{cmd}\" encountered an error\n{e[1]}")
            else:
                pass
        else:
            pass
    except (EOFError, KeyboardInterrupt):
        print()
        exit(None)
        break
