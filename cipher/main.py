import os
import socket
import sys
import argparse
import traceback
import colorama, websockets, math, shutil, paramiko, progressbar, time, requests, readline
from api import CipherAPI
import exceptions as ex
import tarfile
import importlib.util
import os
import tempfile


colorama.init()

def hidec():
    print("\033[?25l", end="", flush=True) #hide cursor
    
def showc():
    print("\033[?25h", end="", flush=True) #show cursor

print(colorama.Fore.MAGENTA+"Made by @mas6y6 and @malachi196 (on github)")

print(r"""   _______       __              ____  _____
  / ____(_)___  / /_  ___  _____/ __ \/ ___/
 / /   / / __ \/ __ \/ _ \/ ___/ / / /\__ \ 
/ /___/ / /_/ / / / /  __/ /  / /_/ /___/ / 
\____/_/ .___/_/ /_/\___/_/   \____//____/  
      /_/                                   

Project Codename: Paradox"""+colorama.Fore.RESET)

#variables
api = CipherAPI()

if not os.path.exists("data"):
    os.mkdir("data")

if not os.path.exists("data/cache"):
    os.mkdir("data/cache")

if not os.path.exists("data/config"):
    os.mkdir("data/config")

if not os.path.exists("data/cache/plugins"):
    os.mkdir("data/cache/plugins")

#builtin functions

@api.command()
def exit(args):
    print("Closing CipherOS")
    sys.exit(0)

@api.command(alias=["cd"])
def chdir(args):
    os.chdir(args[0])
    api.pwd = os.getcwd()

def _tabcompleter(text, state):
    options = [cmd for cmd in api.commands if cmd.startswith(text)]
    if state < len(options):
        return options[state]
    else:
        return None

print("Starting CipherOS...")
readline.set_completer(_tabcompleter)
readline.parse_and_bind("tab: complete")
readline.parse_and_bind("set editing-mode emacs")
print("Loading Plugins")
if not os.path.exists("plugins"):
    os.mkdir("plugins")

for i in os.listdir(os.path.join(api.starterdir,"plugins")):
    api.load_plugin(os.path.join(api.starterdir,"plugins",i))

while True:
    try:
        if api.addressconnected == "":
            commandlineinfo = f"{api.currentenvironment} {api.pwd}"
        else:
            commandlineinfo = f"{api.currentenvironment} {api.addressconnected} {api.pwd}"
        _argx = input(commandlineinfo+" > ").split(" ")
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
        _exit(None)
        break