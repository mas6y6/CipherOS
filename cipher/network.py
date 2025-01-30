import socket, platform, subprocess, psutil

def get_active_interface_and_netmask() -> tuple[list[str], list[str | None]]:
    interfaces = psutil.net_if_addrs()
    ifaces: list[str] = []
    nms: list[str|None] = []
    for iface, addrs in interfaces.items():
        for addr in addrs:
            if addr.family == socket.AF_INET:  # IPv4 address
                if addr.address != "127.0.0.1":  # Exclude loopback
                    if iface in {name for name, net in psutil.net_if_stats().items() if net.isup} and iface != "Loopback Pseudo-Interface 1": # Make sure given interface is running
                        ifaces.append(iface)
                        nms.append(addr.netmask)
    return ifaces, nms

def get_mac(ip: str) -> str:
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

def cipher_ping(ip:str, pings:int=1, timeout:int|float=4) -> bool:
    if platform.system().lower().startswith("win"):
        cmd = f"ping /n {pings} /w {int(timeout * 1000)}"
    else:
        cmd = f'ping -c {pings} -W {timeout} {ip}'
    try:
        _output = subprocess.check_output(cmd, shell=True).decode(encoding="utf-8", errors="replace")
    except: # Exception as e:
        return False
    return True

def chunk_ports(start:int, end:int, chunk_size:int) -> list[tuple[int, int]]:
    return [(i, min(i + chunk_size - 1, end)) for i in range(start, end + 1, chunk_size)]
