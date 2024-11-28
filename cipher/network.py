import socket,platform, subprocess, time
import traceback
import nmap, nmap3
import struct, re, psutil
from ipaddress import IPv4Network
from concurrent.futures import ThreadPoolExecutor, as_completed
from .exceptions import ExitCodeError
from ping3 import ping, verbose_ping
from scapy.all import sr1, IP, TCP, UDP, ICMP, conf
from socket import getservbyport

def get_active_interface_and_netmask():
    interfaces = psutil.net_if_addrs()
    ifaces = []
    nms = []
    for iface, addrs in interfaces.items():
        for addr in addrs:
            if addr.family == socket.AF_INET:  # IPv4 address
                if addr.address != "127.0.0.1":  # Exclude loopback
                    if iface in {name for name, net in psutil.net_if_stats().items() if net.isup} and iface != "Loopback Pseudo-Interface 1": # Make sure given interface is running
                        ifaces.append(iface)
                        nms.append(addr.netmask)
    return ifaces, nms

def get_mac(ip):
    try:
        if platform.system().lower() == "windows":
            command = ["arp", "-a", ip]
        else:
            command = ["arp", "-n", ip]
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        output = result.stdout
        for line in output.splitlines():
            if ip in line:
                parts = line.split()
                for part in parts:
                    if ":" in part or "-" in part:
                        return part.upper()
        return "Unknown"
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while running arp for {ip}: {e}")
        return "Unknown"
    except Exception as e:
        print(f"An error occurred while getting MAC for {ip}: {e}")
        return "Unknown"

def cipher_ping(host):
    try:
        response_time = ping(host, timeout=2)
        if response_time is not None:
            return True
        return False
    except TimeoutError:
        print(f"Timeout while pinging {host}.")
        return False
    except Exception as e:
        print(f"An error occurred while pinging {host}: {e}")
        return False

def chunk_ports(start, end, chunk_size):
    return [(i, min(i + chunk_size - 1, end)) for i in range(start, end + 1, chunk_size)]
