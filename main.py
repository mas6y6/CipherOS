import os
import socket
import sys
sys.path.append(os.getcwd())
import argparse
import traceback
import colorama, websockets, math, shutil, paramiko, progressbar, time, requests, platform, pyinputplus, urllib3, subprocess, markdown
import tarfile
import importlib.util
import tempfile
import shutil
from prompt_toolkit import prompt
from prompt_toolkit.completion import Completer, Completion, PathCompleter, WordCompleter
from prompt_toolkit.history import InMemoryHistory
import urllib.request
import progressbar
import os
import socket,platform, subprocess
import psutil
import struct, json
from ipaddress import IPv4Network, IPv4Address
from concurrent.futures import ThreadPoolExecutor, as_completed
import signal
import nmap3,nmap
from rich.console import Console
from rich.table import Table

colorama.init()
running_on_mac = False # Meant as the cipher library is not installed (for macOS)
macpwd = None
macapistarter = None
console = Console()

pbar = None

#! README
# The api.pwd class is the current path where CipherOS is in right now
# The api.starterdir is where the plugins and data folder is located in the this variable is to not change and if it changes then its going to break a lot of problems.
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
import cipher.network

#variables
version = 1
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
    console.print(msg,style="bold bright_red")

if not os.path.exists(os.path.join(api.starterdir,"data","cache","networkmap.json")):
    json.dump({},open(os.path.join(api.starterdir,"data","cache","networkmap.json"),"w"))

networkmap = json.load(open(os.path.join(api.starterdir,"data","cache","networkmap.json"),"r"))

def networkmap_save():
    global networkmap
    with open(os.path.join(api.starterdir,"data","cache","networkmap.json"),"w") as f:
        json.dump(networkmap,f,indent=4)
        f.close()

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

@api.command(alias=["pscn"])
def portscan(args):
    global sigIntPscn
    sigIntPscn = False
    ip = args[0]

    console.print("CipherOS Port Scanner",style="bold bright_blue")
    console.print("Scanning...",style="bright_blue")

    def sig_handler(sig, frame):
        global sigIntPscn
        sigIntPscn = True

    signal.signal(signal.SIGINT, sig_handler)

    def scan_ports(ip, port):
        if sigIntPscn:
            return None
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(0.5)
                result = s.connect_ex((ip, port))
                if result == 0:
                    return port
        except Exception:
            pass
        return None

    open_ports = []
    completed = 0
    errors = []
    max_workers = min(3000, os.cpu_count() * 5)
    console.print("MAX WORKERS PER CHUNK:",max_workers)
    pbar = progressbar.ProgressBar(widgets=[f"{colorama.Fore.LIGHTBLUE_EX}Progress: ",f" [SCANNED: N/A,OPEN: N/A]",progressbar.Percentage()," [",progressbar.Bar(),"] ",progressbar.AdaptiveETA()," ",progressbar.AnimatedMarker(),colorama.Fore.RESET])
    pbar.maxval=65536
    pbar.start()

    with ThreadPoolExecutor(max_workers=30) as executor:
        futures = {executor.submit(scan_ports, ip, port): port for port in range(1,65536)}

        for future in as_completed(futures):
            port = futures[future]
            try:
                if sigIntPscn:
                    print("Cancelled")
                    future.cancel()
                    break
                result = future.result()
                if result:
                    open_ports.append(port)
                completed += 1
                pbar.widgets[1] = f"[SCANNED: {completed},OPEN: {len(open_ports)}]"
                pbar.update(completed)
            except Exception as e:
                error_msg = f"Error scanning port {port}: {e}"
                errors.append(error_msg)
                printerror(error_msg)
    
    pbar.finish()
    console.print("Scan Complete\n",style="bold bright_green")
    open_ports.sort()

    table = Table(title="Ports open",min_width=15)
    table.add_column("Port",justify="left",style="yellow")
    for port in open_ports:
        table.add_row(str(port))
    console.print(table)

@api.command(alias=["scn","netscan"])
def scannet(args):
    console.print("CipherOS Network Device Scanner",style="bright_blue")
    console.print("Getting Network Range... ",style="bright_blue")
    console.print("\tGetting localip... ",end="",style="bright_blue")
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        localip = s.getsockname()[0]
        s.close()
    except Exception as e:
        console.print("Failed. Cannot continue",style="bright_red")
        raise ConnectionError(e)
    else:
        console.print("Success",style="bright_green")
    
    console.print("\tTesting Network connectivity... ",end="",style="bright_blue")
    try:
        onlineip = requests.get("https://ifconfig.me/").text
    except:
        console.print("Failed",style="bright_red")
        onlineip = ""
    else:
        console.print("Success",style="bright_green")
    
    console.print("\tGetting Submask... ",end="",style="bright_blue")
    try:
        interface, subnet_mask = cipher.network.get_active_interface_and_netmask()
        if subnet_mask == 0:
            raise ConnectionAbortedError()
    except Exception:
        console.print("Failed. using \"255.255.255.0\" as submask",style="bright_red")
        subnet_mask = "255.255.255.0"
    else:
        console.print("Success",style="bright_green")
    
    cidr = sum(bin(int(x)).count("1") for x in subnet_mask.split("."))
    network_range = f"{localip}/{cidr}"
    console.print("Using Interface:",interface,style="green")
    console.print("OnlineIP:",onlineip,style="green")
    console.print("LocalIP:",localip,style="green")
    console.print("Submask:",subnet_mask,style="green")
    console.print("NetworkRange:",network_range,style="green")
    console.print("Ready. Scanning for devices...",style="bold bright_green")
    print("")
    network = IPv4Network(network_range,strict=False)
    devices = []
    devicerange = 0
    completed = 0
    for i in network:
        devicerange += 1
    
    max_workers = min(60, os.cpu_count() * 5)
    console.print("MAX WORKERS PER CHUNK:",max_workers)
    pbar = progressbar.ProgressBar(widgets=[colorama.Fore.LIGHTBLUE_EX,"Progress:",progressbar.Percentage()," [",progressbar.Bar(),"] ",progressbar.AdaptiveETA()," ",progressbar.AnimatedMarker(),colorama.Fore.RESET])
    pbar.start()
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_ip = {executor.submit(cipher.network.cipher_ping, str(ip)): str(ip) for ip in network}
        for future in as_completed(future_to_ip):
            ip = future_to_ip[future]
            try:
                if future.result():
                    mac_address = cipher.network.get_mac(ip)
                    try:
                        if IPv4Address(ip).is_multicast or IPv4Address(ip).is_reserved or IPv4Address(ip).is_loopback:
                            hostname = "Skipped"
                        else:
                            hostname = socket.gethostbyaddr(ip)[0]
                    except socket.herror:
                        hostname = "Unknown"
                    except ValueError:
                        hostname = "Unknown"
                    
                    devices.append({"ip": ip, "mac": mac_address,"hostname":hostname})
                    completed += 1
                    pbar.update(completed)
            except Exception as e:
                pass
                #print(f"Error scanning {ip}: {e}")
    
    pbar.finish()
    
    print()
    console.print("Scan Complete",style="bold bright_green")
    networkmap[onlineip] = {"devices":{}}
    sorted_devices = sorted(devices, key=lambda d: (len(d['ip']), tuple(map(int, d['ip'].split(".")))))
    table = Table(title="Devices Found",show_header=True)
    table.add_column("IP Address", style="yellow",justify="left",header_style="bold yellow")
    table.add_column("Hostname", style="blue",justify="left",header_style="bold blue")
    table.add_column("MAC Address", style="magenta",justify="left",header_style="bold magenta")

    networkmap[onlineip] = {"devices": {}}
    sorted_devices = sorted(devices, key=lambda d: (len(d['ip']), tuple(map(int, d['ip'].split(".")))))
    for device in sorted_devices:
        ip = device['ip']
        hostname = device['hostname']
        mac = device['mac']
        table.add_row(ip, hostname, mac)
        networkmap[onlineip]['devices'][ip] = {"mac": mac, "hostname": hostname}
    console.print(table)
    networkmap_save()

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

    elif args[0] == "help":
        print("""Usage:

reloadall: Reloads all plugins
disable <plugin name>: Disables a specified plugin
enable <plugin name>: Enables a specified plugin
info <plugin name>: Provides a description of the specified plugin
list: Lists all enabled plugins
help: Opens this menu
""")

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
        os.remove(os.path.join(api.pwd,args[0]))
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
            printerror(f"Error: Plugin '{i}' failed to load\n"+traceback.format_exc())
else:
    print("No plugins found")

console.print("[bold bright_magenta]Made by @mas6y6, @malachi196, and @overo3 (on github)[/bold bright_magenta]")

print(colorama.Fore.MAGENTA+r"""   _______       __              ____  _____
  / ____(_)___  / /_  ___  _____/ __ \/ ___/
 / /   / / __ \/ __ \/ _ \/ ___/ / / /\__ \ 
/ /___/ / /_/ / / / /  __/ /  / /_/ /___/ / 
\____/_/ .___/_/ /_/\___/_/   \____//____/  
      /_/                                   

Project Codename: Paradox"""+colorama.Fore.RESET)
console.print("")

history = InMemoryHistory()
api.updatecompletions()

while True:
    try:

        if api.addressconnected == "":
            commandlineinfo = f"{api.currentenvironment} {api.pwd}"
        else:
            commandlineinfo = f"{api.currentenvironment} {api.addressconnected} {api.pwd}"
        command_completer = WordCompleter(api.completions, ignore_case=True)
        user_input = prompt(f"{commandlineinfo}> ",completer=command_completer ,history=history)
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