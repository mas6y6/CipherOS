import ipaddress
import socket
import sys
import os
import re
import subprocess
import errno
from requests.exceptions import ConnectionError, Timeout
import platform

opsys = platform.system()

#CRCSV: connection refused: cross system version
if opsys == "Windows":
    CRCSV = errno.WSAECONNREFUSED
elif opsys == "Darwin" or opsys == "Linux":
    CRCSV = errno.ECONNREFUSED
else:
    raise Exception(f"platform \"{opsys}\" is not supported by nettest")

def check_host(host, port=80, timeout=1) -> bool | int:
    try:
        socket.create_connection((host, port), timeout)
        return True
    except Exception as e:
        if e.args[0] == "timed out":
            return 2
        elif e.args[0] == CRCSV:
            return True
        else:
            print(f"\n{e.args[0]}")
            return False
    except KeyboardInterrupt:
        return 0

def finalinfo(online):
    print("\n\n","\r"+"-"*20)
    print(f"Online Found: {online}")
    print("-"*20)

def knmap(network: str,output: bool = True, retry: bool = True): #kai network-mapping :)
    """scans online devices on a network (alternate version of nmap)"""
    net4 = ipaddress.ip_network(network)
    roundnum = 1
    retrystate = False
    i = 0
    online = []
    sigint = False
    try:
        for x in net4.hosts():
            if sigint:
                finalinfo(online)
                break
            while True:
                if sigint:
                    break
                if not retrystate:
                    if output:
                        print(f"{roundnum}. checking host {str(x)}... ", end="", flush=True)
                elif retrystate and retry:
                    if output:
                        print(f"{roundnum} (retry). rechecking host {str(x)}... ", end="", flush=True)
                try:
                    out = check_host(str(x), timeout=3) #checking host
                except KeyboardInterrupt:
                    sigint = True
                    break
                if out == True:
                    if output:
                        print(f"online", flush=True)
                    online.append(str(x))
                elif out == 2:
                    if retry:
                        if not retrystate:
                            if output:
                                print("request timed out")
                            retrystate = True
                            continue
                        else:
                            if output:
                                print("offline")
                            retrystate = False
                    else:
                        if output:
                            print("offline")
                elif out == 0:
                    sigint = True
                    break
                else:
                    if output:
                        print("offline")
                roundnum += 1
                i += 1
                break
    except KeyboardInterrupt:
        finalinfo(online)

if __name__ == "__main__":
    knmap(network="192.168.86.0/24", retry=False)