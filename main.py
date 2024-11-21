import os
import socket
import sys
sys.path.append(os.getcwd())
sys.path.append('./cipher')
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
from commands import register_main_cmds
from completer import get_full_completer

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
#register all builtin functions

register_main_cmds(api)

print("Starting CipherOS...")

if not len(os.listdir(os.path.join(api.starterdir,"plugins"))) == 0:
    for i in os.listdir(os.path.join(api.starterdir,"plugins")):
        try:
            api.load_plugin(os.path.join(api.starterdir,"plugins",i),api)
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
        user_input = prompt(f"{commandlineinfo}> ",completer=get_full_completer(api) ,history=history)

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
