import argparse
import os
import socket
import sys

import rich
import rich.traceback

# Check if the cipher folder exists and adds it to the sys.path.append
if "cipher" in os.listdir() and os.path.isdir("cipher"):
    sys.path.append(os.getcwd())
    sys.path.append(os.path.join(os.getcwd(),"cipher"))
else:
    def get_resource_path(relative_path):
        """Get the absolute path to a resource, works for development and PyInstaller."""
        if hasattr(sys, "_MEIPASS"):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)
    sys.path.append(get_resource_path("resources/cipher"))
    sys.path.append(get_resource_path("resources/cipher/tools"))
    
# Thats hella lot of libraries
# And thats just the beginning there is more in the cipher/api.py file :)
#
# - @mas6y6
import json
import math
import os
import platform
import shutil
import signal
import socket
import struct
import subprocess
import tarfile
import tempfile
import time
import traceback
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from ipaddress import IPv4Address, IPv4Network
from threading import Lock
import colorama
import markdown
import paramiko
import progressbar
import psutil
import pyinputplus
import requests
import urllib3
import websockets
from ping3 import ping, verbose_ping
from prompt_toolkit import prompt
from prompt_toolkit.completion import (Completer, Completion, PathCompleter,WordCompleter)
from prompt_toolkit.history import InMemoryHistory
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.tree import Tree
from rich.markdown import Markdown

colorama.init()
running_on_mac = False  # Meant as the cipher library is not installed (for macOS)
macpwd = None
macapistarter = None

pbar = None

#! README
# The api.pwd class is the current path where CipherOS is in right now
# The api.starterdir is where the plugins and data folder is located in the this variable is to not change and if it changes then its going to break a lot of problems.

#if os.name == "posix":
#    if os.getcwd() == os.path.expanduser("~"):
#        macpwd = os.path.expanduser("~")
#        os.chdir(macpwd)
#        if not os.path.exists(os.path.join(os.path.expanduser("~"), "CipherOS")):
#            os.mkdir(os.path.join(os.path.expanduser("~"), "CipherOS"))
#        macapistarter = os.path.join(os.path.expanduser("~"), "CipherOS")
#        if not os.path.exists(
#            os.path.join(os.path.expanduser("~"), "CipherOS", "cipher")
#        ):
#            print(
#                'Warning the "cipher" library is not installed and its required to run'
#            )
#            print('Do you want to download the "cipher" library?')
#            print()
#            print('You cannot install it using "pip" as its not available on pypi.org')
#            print()
#            q = pyinputplus.inputYesNo("Would you like to continue? (Y/n): ")
#            if q:
#                urllib.request.urlretrieve(
#                    "https://codeload.github.com/mas6y6/CipherOS/zip/refs/heads/main",
#                    os.path.join(os.path.expanduser("~"), "CipherOS", "cache.zip"),
#                    show_progress,
#                )
#           else:
#               print(
#                    'You can download the "cipher" folder from github https://github.com/mas6y6/CipherOS/archive'
#                )
#                sys.exit()

from cipher.api import CipherAPI
import cipher.exceptions as ex
import cipher.network
from cipher.parsers import ArgumentParser, ConfigParser
import cipher.api

# variables
version = 1
api = CipherAPI()
cipher.api.initialized_api = api
console = api.console
debugmode = False

if running_on_mac:
    # To fix the path plugins and data folders being created in the ~ folder
    #
    # The plugins folder must be in the ~/CipherOS/plugins if you are using linux or macOS
    #
    # macOS is just a linux distro so :)
    api.pwd = macpwd
    api.starterdir = macapistarter

sys.path.append(os.path.join(api.starterdir, "plugins"))
sys.path.append(os.path.join(api.starterdir, "data", "cache", "packages"))


def hidec():
    print("\033[?25l", end="", flush=True)  # hide cursor


def showc():
    print("\033[?25h", end="", flush=True)  # show cursor


def printerror(msg):
    console.print(msg, style="bold bright_red")

parser = argparse.ArgumentParser()
parser.add_argument("--debug",action="store_true",help="Enables debug mode")
parser.add_argument("--startdir",action="store",help="Overrides the cache directory")

executeargs = parser.parse_args()

def is_running_in_appdata():
    appdata_folder = os.environ.get("LOCALAPPDATA")  # e.g., C:\Users\<User>\AppData\Roaming
    current_dir = os.path.abspath(os.getcwd())
    return current_dir.startswith(appdata_folder)

def create_directories(path_list):
    for path in path_list:
        if not os.path.exists(path):
            print(path)
            os.makedirs(path)

if not executeargs.startdir != None:
    if platform.system() == "Windows": 
        if is_running_in_appdata():
            api.pwd = os.path.expanduser("~")
            roaming_folder = os.environ.get("APPDATA")
            os.makedirs(roaming_folder,exist_ok=True)
            api.starterdir = os.path.join(os.environ.get("APPDATA"),"CipherOS")
            os.chdir(api.pwd)
        else:
            pass
    elif platform.system() == "Linux":
        if not debugmode:
            api.starterdir = os.path.expanduser("~")
    elif platform.system() == "Darwin":
        if not debugmode:
            api.starterdir = os.path.expanduser("~")
else:
    api.starterdir = executeargs.startdir

directories_to_create = [
    os.path.join(api.starterdir, "data"),
    os.path.join(api.starterdir, "plugins"),
    os.path.join(api.starterdir, "data", "cache"),
    os.path.join(api.starterdir, "data", "config"),
    os.path.join(api.starterdir, "data", "cache", "packages"),
    os.path.join(api.starterdir,"CipherOS", "data", "cache", "packageswhl")
]

for i in directories_to_create:
    os.makedirs(i,exist_ok=True)

json.dump(
    {}, open(os.path.join(api.starterdir, "data", "cache", "networkmap.json"), "w")
)

networkmap = json.load(
    open(os.path.join(api.starterdir, "data", "cache", "networkmap.json"), "r")
)

def networkmap_save():
    global networkmap
    with open(
        os.path.join(api.starterdir, "data", "cache", "networkmap.json"), "w"
    ) as f:
        json.dump(networkmap, f, indent=4)
        f.close()

@api.command()
def exit(args):
    print("Closing CipherOS")
    sys.exit(0)


@api.command(alias=["pscn"])
def portscan(argsraw):
    parser = ArgumentParser(api, description="Scan the specified device for open ports (This is will work in progress so it will not be reliable)")
    parser.add_argument("ip",type=str,action="store",required=True,help_text="IP Address to device to scan")

    args = parser.parse_args(argsraw)
    
    #If the --help (-h) is passes it kills the rest of the script
    if parser.help_flag:
        return None
    
    global sigIntPscn
    sigIntPscn = False
    ip = args.ip

    console.print(Panel("CipherOS Port Scanner\n[red]Not fully accurate[/red]", style="bold bright_blue"))
    console.print("Scanning...", style="bright_blue")

    def sig_handler_pscn(sig, frame):
        global sigIntPscn
        sigIntPscn = True

    signal.signal(signal.SIGINT, sig_handler_pscn)

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
    max_workers = min(80, os.cpu_count() * 100)
    console.print("MAX WORKERS PER CHUNK:", max_workers)
    pbar = progressbar.ProgressBar(
        widgets=[
            f"{colorama.Fore.LIGHTBLUE_EX}Progress: ",
            f" [SCANNED: N/A,OPEN: N/A]",
            progressbar.Percentage(),
            " [",
            progressbar.Bar(),
            "] ",
            progressbar.AdaptiveETA(),
            " ",
            progressbar.AnimatedMarker(),
            colorama.Fore.RESET,
        ]
    )
    pbar.maxval = 65536
    pbar.start()

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(scan_ports, ip, port): port for port in range(1, 65536)
        }

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
                printerror(error_msg)

    pbar.finish()
    console.print("Scan Complete\n", style="bold bright_green")
    open_ports.sort()

    table = Table(title="Ports open", min_width=15)
    table.add_column("Port", justify="left", style="yellow")
    for port in open_ports:
        table.add_row(str(port))
    console.print(table)

@api.command(alias=["scn", "netscan"])
def scannet(argsraw):
    parser = ArgumentParser(api, description="Scan your network for devices")

    args = parser.parse_args(argsraw)
    
    #If the --help (-h) is passes it kills the rest of the script
    if parser.help_flag:
        return None
    
    global sigIntScn
    sigIntScn = False

    def sig_handler_scn(sig, frame):
        global sigIntScn
        sigIntScn = True

    signal.signal(signal.SIGINT, sig_handler_scn)
    console.print(Panel("CipherOS Network Device Scanner", style="bright_blue",expand=True))
    console.print("Getting Network Range... ", style="bright_blue")
    console.print("\tGetting localip... ", end="", style="bright_blue")

    def cipher_ping(host):
        # if host.split(".")[3] == "0":
        #     print(f"Checking {host}/8")
        if sigIntScn:
            return None
        try:
            return cipher.network.cipher_ping(host)
        except TimeoutError:
            #print(f"Timeout while pinging {host}.")
            return False
        except Exception as e:
            #print(f"An error occurred while pinging {host}: {e}")
            return False
        return False

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        localip = s.getsockname()[0]
        s.close()
    except Exception as e:
        console.print("Failed. Cannot continue", style="bright_red")
        raise ConnectionError(e)
    else:
        console.print("Success", style="bright_green")

    console.print("\tTesting Network connectivity... ", end="", style="bright_blue")
    try:
        onlineip = requests.get("https://ifconfig.me/").text
    except:
        console.print("Failed", style="bright_red")
        onlineip = ""
    else:
        console.print("Success", style="bright_green")

    console.print("\tGetting Submask... ", end="", style="bright_blue")
    try:
        interfaces, netmasks = cipher.network.get_active_interface_and_netmask()
        if netmasks == None:
            raise ConnectionAbortedError()
    except Exception:
        console.print('Failed. using "255.255.255.0" as submask', style="bright_red")
        for i in range(len(interfaces)):
            netmasks[i] = "255.255.255.0"
    else:
        console.print("Success", style="bright_green")

    s = 0
    for i in interfaces:
        cidr = sum(bin(int(x)).count("1") for x in netmasks[s].split("."))
        network_range = f"{localip}/{cidr}"
        console.print("Using Interface:", i, style="green")
        console.print("OnlineIP:", onlineip, style="green")
        console.print("LocalIP:", localip, style="green")
        console.print("Submask:", netmasks[s], style="green")
        console.print("NetworkRange:", network_range, style="green")
        console.print("Ready. Scanning for devices...", style="bold bright_green")
        print("")
        network = IPv4Network(network_range, strict=False)
        devices = []
        devicerange = 0
        scanned = 0
        for i in network:
            devicerange += 1

        console.print(f"Scanning {devicerange} potential devices on your network")
        max_workers = min(60, os.cpu_count() * 5)
        console.print("MAX WORKERS PER CHUNK:", max_workers)
        bar = progressbar.ProgressBar(
            widgets=[
                colorama.Fore.LIGHTBLUE_EX,
                "Progress: ",
                " [SCANNED: N/A, ONLINE: N/A] ",
                progressbar.Percentage(),
                " [",
                progressbar.Bar(),
                "] ",
                progressbar.AdaptiveETA(),
                " ",
                progressbar.AnimatedMarker(),
                colorama.Fore.RESET,
            ]
        )
        bar.maxval = devicerange
        bar.start()
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_ip = {
                executor.submit(cipher_ping, str(ip)): str(ip)
                for ip in network
            }
            for future in as_completed(future_to_ip):
                ip = future_to_ip[future]
                try:
                    if sigIntScn:
                        console.print("Canceled")
                        future.cancel()
                        break
                    result = future.result()
                    if result:
                        mac_address = cipher.network.get_mac(ip)
                        try:
                            if (
                                IPv4Address(ip).is_multicast
                                or IPv4Address(ip).is_reserved
                                or IPv4Address(ip).is_loopback
                            ):
                                hostname = "Skipped"
                            else:
                                hostname = socket.gethostbyaddr(ip)[0]
                        except socket.herror:
                            hostname = "Unknown"
                        except ValueError:
                            hostname = "Unknown"
                        
                        devices.append(
                                    {"ip": ip, "mac": mac_address, "hostname": hostname}
                                )

                        scanned += 1
                        bar.widgets[2] = (
                            f" [SCANNED: {scanned}/{devicerange}, ONLINE: {len(devices)}] "
                        )
                        bar.update(scanned)
                    else:
                        scanned += 1
                        bar.widgets[2] = (
                            f" [SCANNED: {scanned}/{devicerange}, ONLINE: {len(devices)}] "
                        )
                        bar.update(scanned)
                except Exception:
                    scanned += 1
                    bar.widgets[2] = (
                        f" [SCANNED: {scanned}/{devicerange}, ONLINE: {len(devices)}] "
                    )
                    bar.update(scanned)

        s += 1
        bar.finish()

        print()
        console.print("Scan Complete", style="bold bright_green")
        networkmap[onlineip] = {"devices": {}}
        sorted_devices = sorted(
            devices, key=lambda d: (len(d["ip"]), tuple(map(int, d["ip"].split("."))))
        )
        table = Table(title="Devices Found", show_header=True)
        table.add_column(
            "IP Address", style="yellow", justify="left", header_style="bold yellow"
        )
        table.add_column(
            "Hostname", style="blue", justify="left", header_style="bold blue"
        )
        table.add_column(
            "MAC Address", style="magenta", justify="left", header_style="bold magenta"
        )

        networkmap[onlineip] = {"devices": {}}
        sorted_devices = sorted(
            devices, key=lambda d: (len(d["ip"]), tuple(map(int, d["ip"].split("."))))
        )
        for device in sorted_devices:
            ip = device["ip"]
            hostname = device["hostname"]
            mac = device["mac"]
            table.add_row(ip, hostname, mac)
            networkmap[onlineip]["devices"][ip] = {"mac": mac, "hostname": hostname}
        console.print(table)
    networkmap_save()

@api.command(alias=["cd"])
def chdir(argsraw):
    parser = ArgumentParser(api, description="Change to a directory")
    parser.add_argument("path",type=str,required=True,help_text="Directory to move to")

    args = parser.parse_args(argsraw)
    
    #If the --help (-h) is passes it kills the rest of the script
    if parser.help_flag:
        return None
    
    if not args.path == "~":
        if os.path.isdir(args.path):
            os.chdir(args.path)
        else:
            printerror(f"Error: {args.path} is a file")
        api.pwd = os.getcwd()
    else:
        api.pwd = os.path.expanduser("~")
        os.chdir(api.pwd)
    api.updatecompletions()

@api.command()
def mkdir(argsraw):
    parser = ArgumentParser(api, description="Makes a directory")
    parser.add_argument("path",type=str,required=True,help_text="Directory to create")

    args = parser.parse_args(argsraw)
    
    #If the --help (-h) is passes it kills the rest of the script
    if parser.help_flag:
        return None
    
    if os.path.exists(args.folder):
        os.mkdir(args.folder)
    else:
        printerror(f"Error: {args.folder} exists")

@api.command(alias=["cls"])
def clear(args):
    print("\033c", end="")

@api.command(alias=["pl"])
def plugins(argsraw):
    parser = ArgumentParser(api, description="Manage plugins for the system.")

    reload_parser = parser.add_subcommand("reload", description="Reloads a given plugin.")
    reload_parser.add_argument("plugin",type=str, help_text="The name of the plugin to reload.",required=True)
    
    reloadall_parser = parser.add_subcommand("reloadall", description="Reload all plugins.")
    
    disable_parser = parser.add_subcommand("disable", description="Disable a plugin.")
    disable_parser.add_argument("plugin", type=str, help_text="The name of the plugin to disable.",required=True)

    enable_parser = parser.add_subcommand("enable", description="Enable a plugin.")
    enable_parser.add_argument("plugin", type=str, help_text="The name of the plugin to enable.",required=True)

    list_parser = parser.add_subcommand("list", description="List all available plugins.")
    
    info_parser = parser.add_subcommand("info", description="Get detailed info about a plugin.")
    info_parser.add_argument("plugin", type=str, help_text="The name of the plugin to get info about.",required=True)

    args = parser.parse_args(argsraw)

    #If the --help (-h) is passes it kills the rest of the script
    if parser.help_flag:
        return None

    if args.subcommand == "reload":
        if args.plugin in api.plugins:
            console.print(f"Reloading \"{args.plugin}\"")
            print(api.plugins[args.plugin].__class__.name)
            api.disable_plugin(api.plugins[args.plugin])
            api.load_plugin(os.path.join(api.starterdir, "plugins", args.plugin))
            console.print("Reload complete.")
        else:
            console.print(f"Error: plugin {args.plugin} does not exist.")
        

    elif args.subcommand == "reloadall":
        console.print("Reloading all plugins...")
        for plugin_name in list(api.plugins):
            api.disable_plugin(api.plugins[plugin_name])
        for plugin_file in os.listdir(os.path.join(api.starterdir,"CipherOS", "plugins")):
            api.load_plugin(os.path.join(api.starterdir, "plugins", plugin_file))
        console.print("Reload complete.")

    elif args.subcommand == "disable":
        if args.plugin:
            if args.plugin in api.plugins:
                console.print(f'Disabling \"{args.plugin}\"...')
                api.disable_plugin(api.plugins[args.plugin])
                console.print(f'Plugin \"{args.plugin}\" disabled.')
            else:
                printerror(f"Error: Plugin \"{args.plugin}\" enabled (not yet implemented).")
        else:
            printerror("Error: No plugin specified to disable.")

    elif args.subcommand == "enable":
        if args.plugin:
            if args.plugin in os.listdir(os.path.join(api.starterdir,"plugins")):
                if not args.plugin in api.plugins:
                    console.print(f'Enabling \"{args.plugin}\"...')
                    api.load_plugin(os.path.join(api.starterdir,"plugins",args.plugin))
                    console.print(f"Plugin \"{args.plugin}\" enabled.")
                else:
                    printerror(f"Error: \"{args.plugin}\" is already enabled")
            else:
                printerror(f"Error: \"{args.plugin}\" is not found in the plugins folder.")
        else:
            printerror("Error: No plugin specified to enable.")

    elif args.subcommand == "list":
        print("Listing plugins:")
        for plugin in api.plugins:
            console.print(f"  - {plugin}")

    elif args.subcommand == "info":
        if args.plugin in api.plugins:
            config = api.plugins[args.plugin].config
            console.print(f"Plugin '{config.displayname}' details:\n")
            console.print("Version:",config.version)
            console.print("Description:",config.description)
            console.print("Organization/Team:",config.team)
            console.print("Authors of plugin")
            for i in config.authors:
                console.print(f"  - [bold green]{i}[/bold green]")
            console.print("\nPluginclass:",config.classname)
            if config.dependencies:
                console.print("Dependencies (Downloaded by PyPI):",config.classname)
                for i in config.dependencies:
                    console.print(f"  - [bold bright_magenta]{i}[/bold bright_magenta]")
        else:
            printerror(f"Plugin '{args.plugin}' not found or enabled.")

    else:
        print("Unknown subcommand.")


@api.command()
def tree(argsraw):
    parser = ArgumentParser(api, description="List the contents of a path in a tree-like structure, making it easier to read.")
    parser.add_argument("path", type=str, help_text="Folder or path to list", required=False)
    
    args = parser.parse_args(argsraw)
    
    # If the --help (-h) is passed, it kills the rest of the script
    if parser.help_flag:
        return None
    
    if args.path is None:
        path = api.pwd
    else:
        path = args.path

    console.print(Panel(path, expand=True))
    
    tree = Tree(".")
    
    for dirpath, dirnames, filenames in os.walk(path):
        relative_path = os.path.relpath(dirpath, path)
        parts = relative_path.split(os.sep) if relative_path != "." else []
        
        branch = tree
        for part in parts:
            branch = next((child for child in branch.children if child.label == f"[bold]{part}[/bold]"), branch)
        
        # Add directories and files to the tree
        for dirname in dirnames:
            branch.add(f"[bold]{dirname}[/bold]")
        for filename in filenames:
            branch.add(filename)
    console.print(tree)

@api.command(alias=["list", "l"])
def ls(argsraw):
    parser = ArgumentParser(api,description="List the contents of a path")
    parser.add_argument("path",type=str,help_text="Folder or path to list",required=False)
    
    args = parser.parse_args(argsraw)
    
    #If the --help (-h) is passes it kills the rest of the script
    if parser.help_flag:
        return None
    
    if not args.path is None:
        path = args.path
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
def touch(argsraw):
    parser = ArgumentParser(api,description="Creates a file")
    parser.add_argument("file",type=str,help_text="File to create",required=True)
    
    args = parser.parse_args(argsraw)
    
    #If the --help (-h) is passes it kills the rest of the script
    if parser.help_flag:
        return None
    
    if not os.path.exists(args.file):
        open(args.file, "w")
        print("Created file", args.file)
        api.updatecompletions()
    else:
        print(
            colorama.Style.BRIGHT + colorama.Fore.RED + f"Error:",
            args.file,
            "exists" + colorama.Fore.RESET + colorama.Style.NORMAL,
        )

@api.command(alias=["cat"])
def viewfile(argsraw):
    parser = ArgumentParser(api,description="Echos a file's contents to the console")
    parser.add_argument("file", type=str, help_text="The file to display", required=True)
    parser.add_argument("--markdown",action="store_true",help_text="Enables markdown text processing",aliases=["-md"])
    parser.add_argument("--color",action="store_true",help_text="Enables Color code texting (Uses rich as processer)",aliases=["-c"])
    
    args = parser.parse_args(argsraw)
    
    #If the --help (-h) is passes it kills the rest of the script
    if parser.help_flag:
        return None
    
    with open(args.file) as f:
        if args.markdown:
            console.print(Markdown(f.read()))
        elif args.color:
            console.print(f.read())
        else:
            print(f.read())

@api.command(alias=["rm"])
def remove(argsraw):
    parser = ArgumentParser(api,description="Removes a file")
    parser.add_argument("file",type=str,help_text="File to delete",required=True)
    
    args = parser.parse_args(argsraw)
    
    #If the --help (-h) is passes it kills the rest of the script
    if parser.help_flag:
        return None
    try:
        os.remove(os.path.join(api.pwd, args.file))
    except PermissionError:
        printerror(f"Error: Permission to delete '{args.file}' denied")
    except FileNotFoundError:
        printerror(f"Error: '{args.file}' does not exist.")



if __name__ == "__main__":
    debugmode = executeargs.debug
    
    if debugmode:
        console.print("Starting CipherOS in [purple]debug mode[/purple]")
        api.debug = True
        @api.command()
        def arbc(argsraw):
            parser = ArgumentParser(api,description="Executes arbitrary code")
            parser.add_argument("code",type=str,help_text="Code to execute",required=True)
            
            args = parser.parse_args(argsraw)

            if parser.help_flag:
                return None
            try:
                eval(args.code)
            except Exception as e:
                print(f"arbc encountered an error: {e}")
        @api.command()
        def vdump(argsraw):
            parser = ArgumentParser(api, description="Dumps all variables to console")
            parser.add_argument("scope", type=str, help_text="Scope (global/local)",required=True)

            args = parser.parse_args(argsraw)

            if parser.help_flag:
                return None

            try:
                username = os.environ.get("USER", "unknown")

                if args.scope == "local":
                    local_vars = {k: v for k, v in locals().items() if k != "local_vars"}
                    console.print(str(local_vars).replace(username, "###"))
                elif args.scope == "global":
                    global_vars = {k: v for k, v in globals().items() if k != "global_vars"}
                    console.print(str(global_vars).replace(username, "###"))
                else:
                    console.print(f"[bold red]Invalid option: {args.scope}[/bold red]")
            except Exception as e:
                console.print(f"[bold red]vdump encountered an error: {e}[/bold red]")
            except Exception as e:
                print(f"vdump encountered an error: {e}")
    else:
        console.print("Starting CipherOS")

    if not len(os.listdir(os.path.join(api.starterdir,"plugins"))) == 0:
        for i in os.listdir(os.path.join(api.starterdir,"plugins")):
            try:
                api.load_plugin(os.path.join(api.starterdir, "plugins", i))
            except:
                printerror(f"Error: Plugin '{i}' failed to load\n" + traceback.format_exc())
    else:
        console.print("No plugins found")

    console.print(
        "[bold bright_magenta]Made by @mas6y6, @malachi196, and @overo3 (on github)[/bold bright_magenta]"
    )

    print(
    colorama.Fore.LIGHTMAGENTA_EX
    + r"""   _______       __              ____  _____
  / ____(_)___  / /_  ___  _____/ __ \/ ___/
 / /   / / __ \/ __ \/ _ \/ ___/ / / /\__ \ 
/ /___/ / /_/ / / / /  __/ /  / /_/ /___/ / 
\____/_/ .___/_/ /_/\___/_/   \____//____/  
      /_/                                   

Project Codename: Paradox"""
    + colorama.Fore.RESET
)
    console.print("\n")

    history = InMemoryHistory()
    api.updatecompletions()
    while True:
        try:
            if api.addressconnected == "":
                commandlineinfo = f"{api.currentenvironment} {api.pwd}"
            else:
                commandlineinfo = (
                    f"{api.currentenvironment} {api.addressconnected} {api.pwd}"
                )
            command_completer = WordCompleter(api.completions, ignore_case=True)
            try:
                user_input = user_input = prompt(
                f"{commandlineinfo}> ", completer=command_completer, history=history
            )
            except Exception as e:
                if debugmode:
                    print("No console found Debugmode is enabled so this will exit the program. (Used for github workflows)")
                    sys.exit(0)
                raise RuntimeError(e)
            _argx = user_input.split(" ")

            if not _argx[0] == "":
                cmd = _argx[0]
                if cmd in api.commands:
                    e = api.run(_argx)

                    if e[0] == 232:
                        printerror(f'Error: "{cmd}" requires arguments:\n{e[1]}')
                    elif e[0] == 231:
                        printerror(f'Error: {e[1]}')
                    elif not e[0] == 0 or e[0] == 404:
                        printerror(f'Error: Command "{cmd}" encountered an error\n{e[1]}')
                    else:
                        pass
                else:
                    printerror(f"Error: Command \"{cmd}\" not found")
            else:
                pass
        except (EOFError, KeyboardInterrupt):
            print()
            exit(None)
            break
