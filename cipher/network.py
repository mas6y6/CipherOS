import socket,platform, subprocess
import fcntl, nmap, nmap3
import struct
from ipaddress import IPv4Network
from concurrent.futures import ThreadPoolExecutor, as_completed
from .exceptions import ExitCodeError

def ping(host):
    param = "-n" if platform.system().lower() == "windows" else "-c"
    try:
        result = subprocess.run(
            ["ping", param, "1", host],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        return result.returncode == 0
    except Exception as e:
        return False

def get_mac(ip):
    try:
        if platform.system().lower() == "windows":
            command = ["arp", "-a", ip]
        else:
            command = ["arp", "-n", ip]
        result = subprocess.run(command, capture_output=True, text=True)
        output = result.stdout
        for line in output.splitlines():
            if ip in line:
                parts = line.split()
                for part in parts:
                    if ":" in part or "-" in part:
                        return part.upper()

        return "Unknown"
    except Exception as e:
        print(f"An error occurred while getting MAC for {ip}: {e}")
        return "Unknown"

def scan_ports_nmap(ip, port_range):
    scanner = nmap.PortScanner()
    try:
        scanner.scan(ip, port_range)
        open_ports = []
        for proto in scanner[ip].all_protocols():
            ports = scanner[ip][proto].keys()
            for port in ports:
                if scanner[ip][proto][port]['state'] == 'open':
                    open_ports.append(port)
        return open_ports
    except Exception as e:
        return []