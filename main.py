import argparse
import os
import socket
import sys
import runpy

import cipher.cipher_aio

# Check if the cipher folder exists and add it to the sys.path
if "cipher" in os.listdir() and os.path.isdir("cipher"):
    sys.path.append(os.getcwd())
    sys.path.append(os.path.join(os.getcwd(),"cipher"))
else:
    def get_resource_path(relative_path:str) -> str:
        """Get the absolute path to a resource, works for development and PyInstaller."""
        if hasattr(sys, "_MEIPASS"):
            base_path = sys._MEIPASS # type: ignore
        else:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path) # type: ignore
    sys.path.append(get_resource_path("resources/cipher"))
    sys.path.append(get_resource_path("resources/cipher/tools"))

'''
Thats hella lot of libraries
And thats just the beginning there is more in the cipher/api.py file :)
- @mas6y6

Yes. And many are unused, which is why I decided to remove them for now.
- tex
'''
import json
import platform
import signal
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
from ipaddress import IPv4Address, IPv4Network
import colorama
import progressbar # type: ignore
import requests
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.history import InMemoryHistory
from rich.panel import Panel
from rich.table import Table
from rich.tree import Tree
from rich.markdown import Markdown


colorama.init()
running_on_mac = False  # Meant as the cipher library is not installed (for macOS)
macpwd = None
macapistarter = None

pbar = None

#! README
# The api.pwd class is the current path where CipherOS is in right now
# The api.configdir is where the plugins and data folders are located in. This variable should not change and because otherwise it's going to bring a lot of problems.

'''
if os.name == "posix":
    if os.getcwd() == os.path.expanduser("~"):
        macpwd = os.path.expanduser("~")
        os.chdir(macpwd)
        if not os.path.exists(os.path.join(os.path.expanduser("~"), "CipherOS")):
            os.mkdir(os.path.join(os.path.expanduser("~"), "CipherOS"))
        macapistarter = os.path.join(os.path.expanduser("~"), "CipherOS")
        if not os.path.exists(
            os.path.join(os.path.expanduser("~"), "CipherOS", "cipher")
        ):
            print(
                'Warning the "cipher" library is not installed and its required to run'
            )
            print('Do you want to download the "cipher" library?')
            print()
            print('You cannot install it using "pip" as its not available on pypi.org')
            print()
            q = pyinputplus.inputYesNo("Would you like to continue? (Y/n): ")
            if q:
                urllib.request.urlretrieve(
                    "https://codeload.github.com/mas6y6/CipherOS/zip/refs/heads/main",
                    os.path.join(os.path.expanduser("~"), "CipherOS", "cache.zip"),
                    show_progress,
                )
           else:
               print(
                    'You can download the "cipher" folder from github https://github.com/mas6y6/CipherOS/archive'
                )
                sys.exit()
'''

from cipher.cipher_aio import CipherAPI, ArgumentParser
import cipher.network
from cipher.elevate import elevate, is_root

# variables
version = 1
api = CipherAPI()
#cipher.cipher_aio.api_instance = api
console = api.console
debugmode = False

if running_on_mac:
    # To fix the path plugins and data folders being created in the ~ folder
    #
    # The plugins folder must be in the ~/CipherOS/plugins if you are using linux or macOS
    #
    # macOS is just a linux distro so :)
    if macpwd != None:        api.pwd = macpwd
    if macapistarter != None: api.configdir = macapistarter

sys.path.append(os.path.join(api.configdir, "plugins"))
sys.path.append(os.path.join(api.configdir, "data", "cache", "packages"))


def hidec():
    print("\033[?25l", end="", flush=True)  # hide cursor


def showc():
    print("\033[?25h", end="", flush=True)  # show cursor


def printerror(msg:str):
    console.print(msg, style="bold bright_red")

parser = argparse.ArgumentParser()
parser.add_argument("--debug",action="store_true",help="Enables debug mode")
parser.add_argument("--startdir",action="store",help="Overrides the cache directory")
parser.add_argument("--sudo",action="store_true",help="Enables sudo mode")
executeargs = parser.parse_args()

def is_running_in_appdata() -> bool:
    appdata_folder = os.environ.get("LOCALAPPDATA")  # e.g., C:\Users\<User>\AppData\Roaming
    if appdata_folder == None: return False
    current_dir = os.path.abspath(os.getcwd())
    return current_dir.startswith(appdata_folder)

def create_directories(path_list:list[str]) -> None:
    for path in path_list:
        if not os.path.exists(path):
            print(f"creating path '{path}'.")
            os.makedirs(path)

if executeargs.startdir == None:
    if platform.system() == "Windows": 
        if is_running_in_appdata():
            api.pwd = os.path.expanduser("~")
            roaming_folder = os.environ.get("APPDATA")
            if roaming_folder != None:
                os.makedirs(roaming_folder ,exist_ok=True)
                api.configdir = os.path.join(roaming_folder,"CipherOS")
            os.chdir(api.pwd)
        else:
            pass
    elif platform.system() == "Linux":
        if not debugmode:
            api.configdir = os.path.join(os.path.expanduser("~"), ".config/CipherOS")
    elif platform.system() == "Darwin":
        if not debugmode:
            api.configdir = os.path.expanduser("~")
else:
    api.configdir = executeargs.startdir

directories_to_create = [
    #os.path.join(api.configdir, "data"),
    os.path.join(api.configdir, "plugins"),
    #os.path.join(api.configdir, "data", "cache"),
    os.path.join(api.configdir, "data", "config"),
    os.path.join(api.configdir, "data", "cache", "packages"),
    os.path.join(api.configdir, "data", "cache", "packageswhl")
]

for i in directories_to_create:
    os.makedirs(i,exist_ok=True)

json.dump(
    {}, open(os.path.join(api.configdir, "data", "cache", "networkmap.json"), "w")
)

networkmap = json.load(
    open(os.path.join(api.configdir, "data", "cache", "networkmap.json"), "r")
)

def networkmap_save():
    global networkmap
    with open(
        os.path.join(api.configdir, "data", "cache", "networkmap.json"), "w"
    ) as f:
        json.dump(networkmap, f, indent=4)
        f.close()

@api.command(desc="Exits CipherOS")
def exit(args:list[str]):
    print("Closing CipherOS")
    sys.exit(0)

@api.command(name="open", desc="Opens a file")
def openfile(argsraw:list[str]):
    parser = ArgumentParser(api, description="Opens a file")
    parser.add_argument(name="file", argtype=str,action="store",required=True,help_text="File to open")

    args = parser.parse_args(argsraw)
    
    #If the --help (-h) is passes it kills the rest of the script
    if parser.help_flag:
        return None
    
    if not hasattr(args, "file"):
        raise AttributeError(f"Argument 'folder' missing.")
    file = args.file # type: ignore
    if not isinstance(file, str):
        raise TypeError(f"Type of 'file' ({type(file)}) does not match expected type (str)") # type: ignore
    
    if os.path.exists(file):
        base = os.path.basename(file)
        if base.endswith(".exe"):
            console.print("[blue]Starting Windows Executeable[/blue]")
        else:
            viewfile([file])

@api.command(alias=["pscn"], desc="Scan the specified device for open ports (This is work in progress so it will not be reliable)")
def portscan(argsraw:list[str]):
    parser = ArgumentParser(api, description="Scan the specified device for open ports (This is work in progress so it will not be reliable)")
    parser.add_argument("ip",argtype=str, action="store", required=True, help_text="IP Address to device to scan")

    args = parser.parse_args(argsraw)
    
    #If the --help (-h) is passes it kills the rest of the script
    if parser.help_flag:
        return None
    
    global sigIntPscn
    sigIntPscn = False
    ip: str = args.ip # type: ignore
    if not isinstance(ip, str):
        console.print(colorama.Fore.RED + "An error occured while trying to get the target ip. Exiting command..." + colorama.Fore.RESET)
        return

    console.print(Panel("CipherOS Port Scanner\n[red]Not fully accurate[/red]", style="bold bright_blue"))
    console.print("Scanning...", style="bright_blue")

    def sig_handler_pscn(sig, frame): # type: ignore
        global sigIntPscn
        sigIntPscn = True

    signal.signal(signal.SIGINT, sig_handler_pscn) # type: ignore

    def scan_ports(ip:str, port:int):
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

    open_ports: list[int] = []
    completed = 0
    cpu_count = os.cpu_count()
    max_workers = min(80, (0 if cpu_count == None else cpu_count) * 100)
    console.print("MAX WORKERS PER CHUNK:", max_workers)
    pbar = progressbar.ProgressBar(
        maxval=65536,
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
    pbar.start() # type: ignore

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
                pbar.widgets[1] = f"[SCANNED: {completed},OPEN: {len(open_ports)}]" # type: ignore
                pbar.update(completed) # type: ignore
            except Exception as e:
                error_msg = f"Error scanning port {port}: {e}"
                printerror(error_msg)

    pbar.finish() # type: ignore
    console.print("Scan Complete\n", style="bold bright_green")
    open_ports.sort()

    table = Table(title="Ports open", min_width=15)
    table.add_column("Port", justify="left", style="yellow")
    for port in open_ports:
        table.add_row(str(port))
    console.print(table)

@api.command(alias=["exe","cmd"], desc="Lists all commands")
def executables(argsraw:list[str]):
    parser = ArgumentParser(api, description="Lists all commands")

    _args = parser.parse_args(argsraw)
    
    #If the --help (-h) is passes it kills the rest of the script
    if parser.help_flag:
        return None

    tab = Table()
    tab.add_column("Commands")
    for i in api.commands:
        tab.add_row(i)
    console.print(tab)

@api.command(name="elevate", desc="Elevates permissions to admin permissions for CipherOS", alias=["sudo-su"])
def elevateperm(argsraw:list[str]):
    parser = ArgumentParser(api, description="Elevates permissions to admin permissions for CipherOS")

    _args = parser.parse_args(argsraw)
    
    if parser.help_flag:
        return None
    
    if not is_root():
        console.print("Attempting to elevate permissions for CipherOS",style="bright_red")
        console.print("Acquiring Admin privileges (This may open a password prompt)",style="bright_red")
        if os.name == "nt":
            elevate(show_console=True,graphical=False)
        else:
            elevate(graphical=False)
    else:
        printerror("Error: Admin permissions already acquired")

@api.command(alias=["scn", "netscan"], desc="Scan your network for devices")
def scannet(argsraw:list[str]):
    parser = ArgumentParser(api, description="Scan your network for devices")

    _args = parser.parse_args(argsraw)
    
    #If the --help (-h) is passes it kills the rest of the script
    if parser.help_flag:
        return None
    
    global sigIntScn
    sigIntScn = False

    def sig_handler_scn(sig, frame): # type: ignore
        global sigIntScn
        sigIntScn = True

    signal.signal(signal.SIGINT, sig_handler_scn) # type: ignore
    console.print(Panel("CipherOS Network Device Scanner", style="bright_blue",expand=True))
    console.print("Getting Network Range... ", style="bright_blue")
    console.print("\tGetting localip... ", end="", style="bright_blue")

    def cipher_ping(host:str):
        # if host.split(".")[3] == "0":
        #     print(f"Checking {host}/8")
        if sigIntScn:
            return None
        try:
            return cipher.network.cipher_ping(host)
        except TimeoutError:
            #print(f"Timeout while pinging {host}.")
            return False
        except Exception as _e:
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
    interfaces: list[str] = []
    try:
        interfaces, netmasks_any = cipher.network.get_active_interface_and_netmask()
        netmasks = [netmask for netmask in netmasks_any if netmask != None]
        if netmasks == []:
            raise ConnectionAbortedError()
    except Exception:
        console.print('Failed. using "255.255.255.0" as submask', style="bright_red")
        netmasks = ["255.255.255.0" for _i in range(len(interfaces))]
    else:
        console.print("Success", style="bright_green")

    # why limit the "max_workers"?
    # This is a networking-delayed task, meaning you can have way more threads, because they don't need to calculate anything.
    # They just wait. Running the scan with 256 workers made the process spike at 1.11% cpu-capacity with my crappy cpu.
    # If you have a function that actually can check if a host is up, that is.
    max_workers = 256 #min(60, (0 if (cc:=os.cpu_count()) == None else cc) * 5)
    s = 0
    for i in interfaces:
        if s >= len(netmasks): break
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
        devices: list[dict[str, str]] = []
        devicerange = 0
        scanned = 0
        for i in network:
            devicerange += 1

        console.print(f"Scanning {devicerange} potential devices on your network")
        console.print("MAX WORKERS PER CHUNK:", max_workers)
        bar = progressbar.ProgressBar(
            maxval=devicerange,
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
        bar.start() # type: ignore
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_ip = {
                executor.submit(cipher_ping, str(ip)): str(ip) #cipher_ping
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
                        
                        devices.append({"ip": ip, "mac": mac_address, "hostname": hostname})
                except Exception:
                    ...
                scanned += 1
                bar.widgets[2] = (f" [SCANNED: {scanned}/{devicerange}, ONLINE: {len(devices)}] ") # type: ignore
                bar.update(scanned) # type: ignore

        s += 1
        bar.finish() # type: ignore

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

@api.command(alias=["cd"], desc="Change to a directory")
def chdir(argsraw:list[str]):
    parser = ArgumentParser(api, description="Change to a directory")
    parser.add_argument("path",argtype=str,required=True,help_text="Directory to move to")

    args = parser.parse_args(argsraw)

    #If the --help (-h) is passes it kills the rest of the script
    if parser.help_flag:
        return None

    if not hasattr(args, "path"):
        path = "~"
    else:
        path: str = args.path # type: ignore
    if not isinstance(path, str):
        raise TypeError(f"Type of 'path' ({type(path)}) does not match expected type (str)") # type: ignore
    
    if not path == "~":
        if os.path.isdir(path):
            os.chdir(path)
        else:
            printerror(f"Error: {path} is a file")
        api.pwd = os.getcwd()
    else:
        api.pwd = os.path.expanduser("~")
        os.chdir(api.pwd)
    api.updatecompletions()

@api.command(desc="Makes a directory")
def mkdir(argsraw:list[str]):
    parser = ArgumentParser(api, description="Makes a directory")
    parser.add_argument("path",argtype=str,required=True,help_text="Directory to create")

    #If the --help (-h) is passes it kills the rest of the script
    if parser.help_flag:
        return None

    args = parser.parse_args(argsraw)
    if not hasattr(args, "folder"):
        raise AttributeError(f"Argument 'folder' missing.")
    folder: str = args.folder # type: ignore
    if not isinstance(folder, str):
        raise TypeError(f"Type of 'path' ({type(folder)}) does not match expected type (str)") # type: ignore
    
    if os.path.exists(folder):
        os.mkdir(folder)
    else:
        printerror(f"Error: {folder} exists")

@api.command(alias=["cls"], desc="Clears the screen")
def clear(args:list[str]):
    print("\033c", end="")

@api.command(alias=["pl"], desc="Manage plugins for the system.")
def plugins(argsraw:list[str]):
    parser = ArgumentParser(api, description="Manage plugins for the system.")

    reload_parser = parser.add_subcommand("reload", description="Reloads a given plugin.")
    reload_parser.add_argument("plugin",argtype=str, help_text="The name of the plugin to reload.",required=True)
    
    _reloadall_parser = parser.add_subcommand("reloadall", description="Reload all plugins.")
    
    disable_parser = parser.add_subcommand("disable", description="Disable a plugin.")
    disable_parser.add_argument("plugin", argtype=str, help_text="The name of the plugin to disable.",required=True)

    enable_parser = parser.add_subcommand("enable", description="Enable a plugin.")
    enable_parser.add_argument("plugin", argtype=str, help_text="The name of the plugin to enable.",required=True)

    _list_parser = parser.add_subcommand("list", description="List all available plugins.")
    
    info_parser = parser.add_subcommand("info", description="Get detailed info about a plugin.")
    info_parser.add_argument("plugin", argtype=str, help_text="The name of the plugin to get info about.",required=True)

    args = parser.parse_args(argsraw)
    if parser.help_flag: return
    if len(argsraw) == 0:
        parser.print_help()
        return

    if hasattr(args, "plugin"): args_plugin: str = args.plugin # type: ignore
    else: args_plugin = ""
    if not isinstance(args_plugin, str):
        raise TypeError(f"Type of 'arg_plugin' ({type(args_plugin)}) does not match expected type (str)") # type: ignore

    #If the --help (-h) is passes it kills the rest of the script
    if parser.help_flag:
        return None

    if args.subcommand == "reload":
        if args_plugin in api.plugins:
            console.print(f"Reloading \"{args_plugin}\"")
            print(f'"{api.plugins[args_plugin].name}" or "{api.plugins[args_plugin].__class__.__name__}()"')
            api.disable_plugin(args_plugin)
            api.load_plugin(os.path.join(api.configdir, "plugins", args_plugin))
            console.print("Reload complete.")
        else:
            console.print(f"Error: plugin {args_plugin} does not exist.")
        

    elif args.subcommand == "reloadall":
        console.print("Reloading all plugins...")
        for plugin_name in list(api.plugins):
            api.disable_plugin(api.plugins[plugin_name].config.name)
        for plugin_file in os.listdir(os.path.join(api.configdir, "plugins")):
            api.load_plugin(os.path.join(api.configdir, "plugins", plugin_file))
        console.print("Reload complete.")

    elif args.subcommand == "disable":
        if args_plugin:
            if args_plugin in api.plugins:
                console.print(f'Disabling \"{args_plugin}\"...')
                api.disable_plugin(args_plugin)
                console.print(f'Plugin \"{args_plugin}\" disabled.')
            else:
                printerror(f"Error: Plugin with name \"{args_plugin}\" not found. Does it exist? Is it already disabled?")
        else:
            printerror("Error: No plugin specified to disable.")

    elif args.subcommand == "enable":
        if args_plugin:
            if args_plugin in os.listdir(os.path.join(api.configdir,"plugins")):
                if not args_plugin in api.plugins:
                    console.print(f'Enabling \"{args_plugin}\"...')
                    api.load_plugin(os.path.join(api.configdir,"plugins",args_plugin))
                    console.print(f"Plugin \"{args_plugin}\" enabled.")
                else:
                    printerror(f"Error: \"{args_plugin}\" is already enabled")
            else:
                printerror(f"Error: \"{args_plugin}\" is not found in the plugins folder.")
        else:
            printerror("Error: No plugin specified to enable.")

    elif args.subcommand == "list":
        print("Listing plugins:")
        for plugin in api.plugins:
            console.print(f"  - {plugin}")

    elif args.subcommand == "info":
        if args_plugin in api.plugins:
            config = api.plugins[args_plugin].config
            console.print(f"Plugin '{config.displayname}' details:\n")
            console.print("Config Version:",config.version)
            console.print("Description:",config.description)
            console.print("Organization/Team:",config.team)
            console.print("Authors of plugin")
            if config.authors != None:
                for i in config.authors:
                    console.print(f"  - [bold green]{i}[/bold green]")
            else:
                console.print(f"  - [bold red]- missing -[/bold red]")
            console.print("Pluginclass:",config.classname)
            if config.dependencies:
                console.print("Dependencies (Downloaded by PyPI):")
                for i in config.dependencies:
                    console.print(f"  - [bold bright_magenta]{i}[/bold bright_magenta]")
        else:
            printerror(f"Plugin '{args_plugin}' not found or enabled.")

    else:
        print("Unknown subcommand.")

@api.command(desc="List the contents of a path in a tree-like structure, making it easier to read.")
def tree(argsraw:list[str]):
    parser = ArgumentParser(api, description="List the contents of a path in a tree-like structure, making it easier to read.")
    parser.add_argument("path", argtype=str, help_text="Folder or path to list", required=False)
    
    args = parser.parse_args(argsraw)
    
    # If the --help (-h) is passed, it kills the rest of the script
    if parser.help_flag:
        return None
    
    if hasattr(args, "path") and args.path != None: # type: ignore
        path: str = args.path # type: ignore
    else:
        path = api.pwd
    
    if not isinstance(path, str):
        raise TypeError(f"Type of 'path' ({type(path)} does not match expected type (str).") # type: ignore

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

@api.command(alias=["list", "l"], desc="List the contents of a path")
def ls(argsraw:list[str]):
    parser = ArgumentParser(api,description="List the contents of a path")
    parser.add_argument("path",argtype=str,help_text="Folder or path to list",required=False)
    
    args = parser.parse_args(argsraw)
    
    #If the --help (-h) is passes it kills the rest of the script
    if parser.help_flag:
        return None
    
    if hasattr(args, "path") and isinstance(args.path, str): # type: ignore
        path: str = args.path # type: ignore
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
    files: list[str] = []
    folders: list[str] = []
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

@api.command(desc="Creates a file")
def touch(argsraw:list[str]):
    parser = ArgumentParser(api,description="Creates a file")
    parser.add_argument("file",argtype=str,help_text="File to create",required=True)
    
    args = parser.parse_args(argsraw)
    
    #If the --help (-h) is passes it kills the rest of the script
    if parser.help_flag:
        return None
    
    if not hasattr(args, "file"):
        raise AttributeError(f"Argument 'file' missing.")
    file: str = args.file # type: ignore
    if not isinstance(file, str):
        raise TypeError(f"Type of 'file' ({type(file)}) does not match expected type (str)") # type: ignore
    
    if not os.path.exists(file):
        open(file, "w")
        print("Created file", file)
        api.updatecompletions()
    else:
        print(
            colorama.Style.BRIGHT + colorama.Fore.RED + f"Error:",
            file,
            "exists" + colorama.Fore.RESET + colorama.Style.NORMAL,
        )
        
@api.command(name="python", alias=["py"], desc="Executes a python file")
def pythoncode(argsraw:list[str]):
    parser = ArgumentParser(api,description="Executes a python file")
    parser.add_argument("file", argtype=str, help_text="The file to display", required=True)
    
    args = parser.parse_args(argsraw)

    #If the --help (-h) is passes it kills the rest of the script
    if parser.help_flag:
        return None

    if not hasattr(args, "file"):
        raise AttributeError(f"Argument 'file' missing.")
    file: str = args.file # type: ignore
    if not isinstance(file, str):
        raise TypeError(f"Type of 'file' ({type(file)}) does not match expected type (str)") # type: ignore
    
    runpy.run_path(file)

@api.command(alias=["cat"], desc="Echos a file's contents to the console")
def viewfile(argsraw:list[str]):
    parser = ArgumentParser(api,description="Echos a file's contents to the console")
    parser.add_argument("file", argtype=str, help_text="The file to display", required=True)
    parser.add_argument("--markdown",action="store_true",help_text="Enables markdown text processing",aliases=["-md"])
    parser.add_argument("--color",action="store_true",help_text="Enables Color code texting (Uses rich as processer)",aliases=["-c"])
    
    args = parser.parse_args(argsraw)

    #If the --help (-h) is passes it kills the rest of the script
    if parser.help_flag:
        return None

    if not hasattr(args, "file"):
        raise AttributeError(f"Argument 'file' missing.")
    file: str = args.file # type: ignore
    if not isinstance(file, str):
        raise TypeError(f"Type of 'file' ({type(file)}) does not match expected type (str)") # type: ignore

    if not hasattr(args, "markdown"):
        raise AttributeError(f"Argument 'markdown' missing.")
    markdown: bool = args.markdown # type: ignore
    if not isinstance(markdown, bool):
        raise TypeError(f"Type of 'markdown' ({type(markdown)}) does not match expected type (str)") # type: ignore
    
    if not hasattr(args, "color"):
        raise AttributeError(f"Argument 'color' missing.")
    color: bool = args.color # type: ignore
    if not isinstance(color, bool):
        raise TypeError(f"Type of 'color' ({type(color)}) does not match expected type (str)") # type: ignore
    
    with open(file) as f:
        if markdown:
            console.print(Markdown(f.read()))
        elif color:
            console.print(f.read())
        else:
            print(f.read())

@api.command(alias=["rm"], desc="Removes a file")
def remove(argsraw:list[str]):
    parser = ArgumentParser(api,description="Removes a file")
    parser.add_argument("file",argtype=str,help_text="File to delete",required=True)
    
    args = parser.parse_args(argsraw)

    #If the --help (-h) is passes it kills the rest of the script
    if parser.help_flag:
        return None

    if not hasattr(args, "file"):
        raise AttributeError(f"Argument 'file' missing.")
    file: str = args.file # type: ignore
    if not isinstance(file, str):
        raise TypeError(f"Type of 'file' ({type(file)}) does not match expected type (str)") # type: ignore
    

    if not hasattr(args, "file"):
        raise AttributeError(f"Argument 'file' missing.")
    file: str = args.file # type: ignore
    if not isinstance(file, str):
        raise TypeError(f"Type of 'file' ({type(file)}) does not match expected type (str)") # type: ignore
    
    try:
        os.remove(os.path.join(api.pwd, file))
    except PermissionError:
        printerror(f"Error: Permission to delete '{file}' denied")
        printerror(f"Error: Permission to delete '{file}' denied")
    except FileNotFoundError:
        printerror(f"Error: '{file}' does not exist.")

@api.command(alias=["rmdir"], desc="Removes a directory")
def rmdir(argsraw:list[str]):
    parser = ArgumentParser(api,description="Removes a directory")
    parser.add_argument("file", argtype=str,help_text="File to directory",required=True)
    
    args = parser.parse_args(argsraw)
    
    #If the --help (-h) is passes it kills the rest of the script
    if parser.help_flag:
        return None
    
    if not hasattr(args, "file"):
        raise AttributeError(f"Argument 'folder' missing.")
    file = args.file # type: ignore
    if not isinstance(file, str):
        raise TypeError(f"Type of 'file' ({type(file)}) does not match expected type (str)") # type: ignore

    try:
        os.rmdir(os.path.join(api.pwd, file))
    except PermissionError:
        printerror(f"Error: Permission to delete '{file}' denied")
    except FileNotFoundError:
        printerror(f"Error: '{file}' does not exist.")

if __name__ == "__main__":
    debugmode = executeargs.debug
    
    if debugmode:
        console.print("Starting CipherOS in [purple]debug mode[/purple]")
        if is_root():
            console.print("Admin privileges detected starting as admin",style="bright_magenta")
        api.debug = True
        @api.command()
        def arbc(argsraw:list[str]):
            parser = ArgumentParser(api,description="Executes arbitrary code")
            parser.add_argument("code",argtype=str,help_text="Code to execute",required=True)
            
            _args = parser.parse_args(argsraw)

            if parser.help_flag: return
            if len(argsraw) == 0: raise AttributeError(f"Argument 'code' missing.")
            code = " ".join(argsraw)
            if parser.help_flag:
                return None
            try:
                eval(code)
            except Exception as e:
                print(f"arbc encountered an error: {e}")
        @api.command()
        def vdump(argsraw:list[str]):
            parser = ArgumentParser(api, description="Dumps all variables to console")
            parser.add_argument("scope", argtype=str, help_text="Scope (global/local)",required=True)

            args = parser.parse_args(argsraw)
            if parser.help_flag: return None

            if not hasattr(args, "scope"):
                raise AttributeError(f"Argument 'scope' missing.")
            scope: str = args.scope # type: ignore
            if not isinstance(scope, str):
                raise TypeError(f"Type of 'scope' ({type(scope)}) does not match expected type (str)") # type: ignore

            try:
                username = os.environ.get("USER", "unknown")

                if scope == "local":
                    local_vars = {k: v for k, v in locals().items() if k != "local_vars"}
                    console.print(str(local_vars).replace(username, "###"))
                elif scope == "global":
                    global_vars = {k: v for k, v in globals().items() if k != "global_vars"}
                    console.print(str(global_vars).replace(username, "###"))
                else:
                    console.print(f"[bold red]Invalid option: {scope}[/bold red]")
            except Exception as e:
                console.print(f"[bold red]vdump encountered an error: {e}[/bold red]")
    else:
        console.print("Starting CipherOS")
        if is_root():
            console.print("Admin privileges detected starting as admin",style="bright_magenta")

    if not len(os.listdir(os.path.join(api.configdir,"plugins"))) == 0:
        for i in os.listdir(os.path.join(api.configdir,"plugins")):
            try:
                api.load_plugin(os.path.join(api.configdir, "plugins", i))
            except:
                printerror(f"Error: Plugin '{i}' failed to load\n" + traceback.format_exc())
    else:
        console.print("No plugins found")

    console.print(
        "[bold bright_magenta]Made by @mas6y6, @malachi196, and @overo3 (on github)[/bold bright_magenta]"
    )
    console.print(
        "[bold bright_magenta]Fixed & modded by tex[/bold bright_magenta]"
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
            command_completer = WordCompleter(api.completions, ignore_case=True)
            try:
                user_input = user_input = prompt(
                f"{api.commandlineinfo}> ", completer=command_completer, history=history
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
                    elif not e[0] == 0:
                        printerror(f'Error: Command "{cmd}" encountered an error\n{e[1]}')
                    else:
                        pass
                else:
                    printerror(f"Error: Command \"{cmd}\" not found")
            else:
                pass
        except (EOFError, KeyboardInterrupt):
            print()
            exit([])
            break
