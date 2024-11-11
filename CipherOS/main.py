import os
import socket
import sys
import argparse
import traceback
import colorama, websockets, math, shutil, paramiko, progressbar, time, requests, readline

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
commands = {"exit":{"command"}}
pwd = os.getcwd()
addressconnected = ""
hostname = socket.gethostname()
localip = socket.gethostbyname()
currentenvironment = "COS"

if not os.path.exists("cipheros"):
    os.mkdir("cipheros")

#builtin functions
def _exit(args):
    print("Closing CipherOS")
    sys.exit(0)

def _tabcompleter(text, state):
    options = [cmd for cmd in commands if cmd.startswith(text)]
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

while True:
    try:
        commandlineinfo = f"{currentenvironment} {addressconnected} {pwd}"
        input(commandlineinfo+" > ")
        
    except KeyError:
        print(colorama.Style.BRIGHT+colorama.Fore.RED+f"Error: Command \"{commandlineinfo[0]}\" not found"+colorama.Fore.RESET+colorama.Style.NORMAL)
    
    except Exception:
        print(colorama.Style.BRIGHT+colorama.Fore.RED+f"Error: Command \"{commandlineinfo[0]}\" incountered an error\n"+traceback.format_exc()+colorama.Fore.RESET+colorama.Style.NORMAL)
    
    except (EOFError, KeyboardInterrupt):
        _exit()
        break