import socket,platform, subprocess
import traceback
import nmap, nmap3
import struct, re
from ipaddress import IPv4Network
from concurrent.futures import ThreadPoolExecutor, as_completed
from .exceptions import ExitCodeError
from ping3 import ping, verbose_ping

def get_mac(ip):
    try:
        # Check platform to determine which command to use
        if platform.system().lower() == "windows":
            command = ["arp", "-a", ip]
        else:
            command = ["arp", "-n", ip]

        # Run the arp command
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        output = result.stdout
        
        # Search for the MAC address in the output
        for line in output.splitlines():
            if ip in line:
                parts = line.split()
                for part in parts:
                    if ":" in part or "-" in part:  # MAC address pattern
                        return part.upper()

        return "Unknown"
    except subprocess.CalledProcessError as e:
        # This will catch errors in subprocess execution
        print(f"An error occurred while running arp for {ip}: {e}")
        return "Unknown"
    except Exception as e:
        # Catch other types of exceptions
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

def scan_ports(ip, port_range):
    try:
        start, end = map(int, port_range.split('-'))
        open_ports = []
        
        for port in range(start, end + 1):
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(0.5)
                result = s.connect_ex((ip, port))
                if result == 0:
                    open_ports.append(port)
                s.close()
            except Exception as e:
                print(f"Error scanning port {port} on {ip}: {e}")
        return open_ports
    except Exception as e:
        traceback.print_exc()
        return []

def get_subnet_mask():
    system = platform.system()

    if system == 'Windows':
        # On Windows, use ipconfig to get the subnet mask
        cmd = 'ipconfig'
        result = subprocess.run(cmd, capture_output=True, text=True)

        # Use regex to find the subnet mask
        match = re.search(r"Subnet Mask[ .]*: ([\d\.]+)", result.stdout)
        if match:
            return match.group(1)
        else:
            raise Exception("Subnet Mask not found")

    elif system == 'Linux' or system == 'Darwin':  # Darwin is macOS
        # On Unix-like systems (Linux/macOS), use ifconfig or ip
        cmd = 'ifconfig'  # Alternatively, you can use 'ip a' on Linux
        result = subprocess.run(cmd, capture_output=True, text=True)

        # Use regex to find the subnet mask
        match = re.search(r"inet\s([\d\.]+)\snetmask\s([\d\.]+)", result.stdout)
        if match:
            return match.group(2)
        else:
            raise Exception("Subnet Mask not found")

    else:
        raise Exception("Unsupported OS")