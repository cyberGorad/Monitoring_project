
import asyncio
import json
import subprocess
import psutil
import socket
import os
import websockets

SERVER_URL = "ws://192.168.43.225:9000"

# Fonction pour récupérer l'adresse IP locale de la machine de manière plus robuste
def get_local_ip():
    # Obtenir l'adresse IP de l'interface réseau active
    for interface, addrs in psutil.net_if_addrs().items():
        for addr in addrs:
            if addr.family == socket.AF_INET and not addr.address.startswith("127"):
                return addr.address
    return "127.0.0.1"  # Retourner localhost si aucune IP valide n'est trouvée

async def run_command(command):
    try:
        result = subprocess.check_output(command, shell=True, text=True)
        return result.strip()
    except subprocess.CalledProcessError:
        return None

async def resolve_ip(ip):
    try:
        # Tentative de résolution de l'IP en utilisant gethostbyaddr
        host = socket.gethostbyaddr(ip)
        return host[0]  # Le nom d'hôte
    except socket.herror:
        # Erreur lors de la résolution de l'adresse IP (pas de nom d'hôte trouvé)
        return None
    except OSError as e:
        # Si l'adresse IP est de type IPv6 et que le système ne supporte pas cette famille d'adresses
        print(f"Erreur lors de la résolution de l'IP {ip}: {e}")
        return None

async def get_established_connections():
    connections = []
    for conn in psutil.net_connections(kind='inet'):
        if conn.status == "ESTABLISHED" and conn.raddr:
            hostname = await resolve_ip(conn.raddr.ip)
            connections.append({
                "ip": conn.raddr.ip,
                "port": conn.raddr.port,
                "hostname": hostname or "Unknown"
            })
    return connections

async def get_open_ports():
    open_ports = []
    for conn in psutil.net_connections(kind='inet'):
        if conn.status == psutil.CONN_LISTEN:
            process_name = psutil.Process(conn.pid).name() if conn.pid else "Unknown"
            open_ports.append({"port": conn.laddr.port, "pid": conn.pid, "process": process_name})
    return open_ports

async def get_cpu_usage():
    return psutil.cpu_percent(interval=1)

async def get_bandwidth_usage():
    old_data = psutil.net_io_counters()
    await asyncio.sleep(1)
    new_data = psutil.net_io_counters()
    return {
        "sent_kb": (new_data.bytes_sent - old_data.bytes_sent) / 1024.0,
        "received_kb": (new_data.bytes_recv - old_data.bytes_recv) / 1024.0,
    }

async def get_cron_jobs():
    cron_path = "/var/spool/cron/crontabs/root"
    if os.path.exists(cron_path):
        return await run_command("crontab -l")
    return "No cron jobs found."

async def get_system_logs():
    log_path = "/var/log/syslog"
    if os.path.exists(log_path):
        return await run_command("tail -n 10 /var/log/syslog")
    return "No logs found."

async def get_outbound_traffic():
    connections = []
    for conn in psutil.net_connections(kind='inet'):
        if conn.raddr:
            try:
                process = psutil.Process(conn.pid) if conn.pid else None
                name = process.name() if process else "Unknown"
                connections.append({
                    "local": f"{conn.laddr.ip}:{conn.laddr.port}",
                    "remote": f"{conn.raddr.ip}:{conn.raddr.port}",
                    "process": name
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied, AttributeError):
                pass
    return connections

async def send_data():
    while True:
        try:
            async with websockets.connect(SERVER_URL) as websocket:
                # Récupération de l'adresse IP locale de la machine
                local_ip = get_local_ip()
                
                data = {
                    "local_ip": local_ip,  # Ajout de l'adresse IP de la machine dans les données envoyées
                    "cpu": await get_cpu_usage(),
                    "open_ports": await get_open_ports(),
                    "connections": await get_established_connections(),
                    "bandwidth": await get_bandwidth_usage(),
                    "cron_jobs": await get_cron_jobs(),
                    "logs": await get_system_logs(),
                    "outbound_traffic": await get_outbound_traffic(),
                }
                await websocket.send(json.dumps(data))
                await asyncio.sleep(2)  # Envoi des données toutes les 5 secondes
        except websockets.exceptions.ConnectionClosedError as e:
            print(f"Erreur de connexion: {e}. Tentative de reconnexion...")
            await asyncio.sleep(2)  # Attente avant de réessayer la connexion

if __name__ == "__main__":
    asyncio.run(send_data())
