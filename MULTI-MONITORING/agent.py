
import asyncio
import json
import subprocess
import platform
import psutil
import socket
import os
import websockets


SERVER_URL = "ws://localhost:9000"

# Fonction pour récupérer l'adresse IP locale de la machine de manière plus robuste
def get_local_ip():
    # Obtenir l'adresse IP de l'interface réseau active
    for interface, addrs in psutil.net_if_addrs().items():
        for addr in addrs:
            if addr.family == socket.AF_INET and not addr.address.startswith("127"):
                return addr.address
    return "127.0.0.1"  # Retourner localhost si aucune IP valide n'est trouvée

def get_os():
    return platform.platform()


def evaluate_system_state(cpu, ram, disks:dict, bandwidth):
    """
    Évalue l'état général de la machine en se basant sur l'utilisation CPU, RAM, Disque, et Bande Passante.
    Renvoie : Good, Medium ou Critical.
    """
    score = 0

    # Analyse CPU
    if cpu < 50:
        score += 1
    elif cpu < 80:
        score += 0.5
    else:
        score -= 1

    # Analyse RAM
    if ram < 50:
        score += 1
    elif ram < 80:
        score += 0.5
    else:
        score -= 1

    # DISKS (analyse moyenne ou max selon ton besoin)
    if isinstance(disks, dict) and disks:
        average_disk_usage = sum(disks.values()) / len(disks)
        if average_disk_usage < 50:
            score += 1
        elif average_disk_usage < 80:
            score += 0.5
        else:
            score -= 1
    else:
        score -= 1  # Penalise si on ne reçoit rien



    # Analyse Bande passante (en KB/s)
    if bandwidth["sent_kb"] < 100 and bandwidth["received_kb"] < 100:
        score += 1
    elif bandwidth["sent_kb"] < 500 and bandwidth["received_kb"] < 500:
        score += 0.5
    else:
        score -= 1

    # Définir l'état global en fonction du score
    if score >= 3:
        return "Good"
    elif 1.5 <= score < 3:
        return "Medium"
    else:
        return "Critical"



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
            open_ports.append({
                "port": conn.laddr.port,
                "pid": conn.pid,
                "process": process_name
            })
    return open_ports

    """ MONITORING SYSTEM INFORMATION """
async def get_cpu_usage():
    return psutil.cpu_percent(interval=1)
async def get_ram_usage():
    return psutil.virtual_memory().percent
async def get_disk_usage():
    usage = {}

    for part in psutil.disk_partitions(all=False):
        try:
            mountpoint = part.mountpoint
            percent = psutil.disk_usage(mountpoint).percent
            usage[mountpoint] = percent
        except PermissionError:
            # Ignore les volumes inaccessibles
            continue

    return usage



async def get_bandwidth_usage():
    old_data = psutil.net_io_counters()
    await asyncio.sleep(1)
    new_data = psutil.net_io_counters()
    return {
        "sent_kb": (new_data.bytes_sent - old_data.bytes_sent) / 1024.0,
        "received_kb": (new_data.bytes_recv - old_data.bytes_recv) / 1024.0,
    }



async def get_cron_jobs():
    if platform.system().lower() == "windows":
        # Pour Windows, utilise 'schtasks' pour lister les tâches planifiées
        return await run_command("schtasks /query /fo LIST /v")
    else:
        # Pour Linux (et Unix-like), utilise crontab
        cron_path = "/var/spool/cron/crontabs/root"
        if os.path.exists(cron_path):
            return await run_command("crontab -l")
        else:
            return "Aucune tâche cron trouvée pour root"


async def get_battery_status():
    battery = psutil.sensors_battery()
    if battery is None:
        return {"battery_status": "No battery info available"}
    
    # Pourcentage de batterie
    percent = battery.percent
    
    # Si l'appareil est sur secteur ou non
    on_ac_power = battery.power_plugged
    
    # Indication de l'état
    status = "On AC power" if on_ac_power else "Running on battery"

    return {
        "battery_percent": percent,
        "battery_status": status
    }



async def check_internet_connection():
    try:
        # Ping Google DNS (8.8.8.8) pour vérifier la connexion internet
        result = subprocess.run(["ping", "-c", "1", "8.8.8.8"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode == 0:
            return "Up"
        else:
            return "Down"
    except Exception as e:
        return "Down"

async def get_temperature():
    # Vérification si le système supporte la récupération de la température
    sensors = psutil.sensors_temperatures()
    
    # If there are no sensors available
    if not sensors:
        return "Temperature not available"

    # Loop through all the sensors
    for sensor_name, sensor_list in sensors.items():
        for sensor in sensor_list:
            # If a sensor is named 'coretemp' or a similar CPU-related name
            if 'cpu' in sensor_name.lower():
                return f"CPU Temperature: {sensor.current}°C"

    return "CPU Temperature not available"


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
                os_name = platform.platform()

                cpu = await get_cpu_usage()
                ram = await get_ram_usage()
                disk = await get_disk_usage()
                bandwidth = await get_bandwidth_usage()
                system_state = evaluate_system_state(cpu, ram, disk, bandwidth) #Etat du système
                
                data = {
                    "system_state":system_state,
                    "local_ip": local_ip,  # Ajout de l'adresse IP de la machine dans les données envoyées
                    "cpu": await get_cpu_usage(),
                    "ram": await get_ram_usage(),
                    "disk": await get_disk_usage(),
                    "open_ports": await get_open_ports(),
                    "connections": await get_established_connections(),
                    "bandwidth": await get_bandwidth_usage(),
                    "cron_jobs": await get_cron_jobs(),
                    "logs": await get_system_logs(),
                    "outbound_traffic": await get_outbound_traffic(),
                    "battery_data": await get_battery_status(),
                    "internet_status": await check_internet_connection(),
                    "temperature": await get_temperature(),
                    "os": get_os(),
                    
                }
                await websocket.send(json.dumps(data))
                await asyncio.sleep(2)  # Envoi des données toutes les 5 secondes
        except websockets.exceptions.ConnectionClosedError as e:
            print(f"Erreur de connexion: {e}. Tentative de reconnexion...")
            await asyncio.sleep(2)  # Attente avant de réessayer la connexion

if __name__ == "__main__":
    asyncio.run(send_data())
