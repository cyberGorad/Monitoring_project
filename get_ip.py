import socket
import psutil

def get_ip():
    # Obtenir toutes les interfaces réseau
    for interface, addrs in psutil.net_if_addrs().items():
        for addr in addrs:
            # Vérifier si l'adresse n'est pas une adresse de loopback
            if addr.family == socket.AF_INET and addr.address != '127.0.0.1':
                return addr.address
    return None

ip = get_ip()
print(f"Adresse IP de votre machine sur le réseau: {ip}")
