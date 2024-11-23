with ThreadPoolExecutor(max_workers=300) as executor:
        future_to_ip = {executor.submit(cipher.network.ping, str(ip)): str(ip) for ip in network}
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
            except Exception as e:
                print(f"Error scanning {ip}: {e}")