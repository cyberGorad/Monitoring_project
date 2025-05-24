
import asyncio
import time
import json
import subprocess
import platform
import psutil
import datetime
import socket
import os
import websockets
from PIL import ImageGrab

import base64

SERVER_URL = "ws://192.168.10.167:9000"


async def send_register(websocket):
    agent_ip = get_local_ip()
    register_payload = {
        "type": "register",
        "ip": agent_ip
    }
    await websocket.send(json.dumps(register_payload))
    print(f"Agent Saved : {agent_ip}")






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




# Fonction de reconnexion avec délai exponentiel
async def reconnect_with_backoff():
    backoff_time = 2  # Temps initial de reconnexion (en secondes)
    max_backoff = 60  # Délai maximum (en secondes)
    
    while True:
        try:
            print(f"RECONNECT TO SERVER {backoff_time}s...")
            await asyncio.sleep(backoff_time)  # Attente avant de tenter la reconnexion
            await send_data()  # Essaye de reconnecter et de renvoyer des données
            break  # Si la connexion réussit, sortir de la boucle
        except Exception as e:
            print(f"ERROR WHEN CONNECT: {e}")
            backoff_time = min(backoff_time * 2, max_backoff)


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




total_sent_bytes = 0
total_recv_bytes = 0

async def get_bandwidth_usage():
    global total_sent_bytes, total_recv_bytes

    # Garder les compteurs précédents comme attributs de la fonction
    if not hasattr(get_bandwidth_usage, "old"):
        get_bandwidth_usage.old = psutil.net_io_counters()

    await asyncio.sleep(1)
    new = psutil.net_io_counters()

    # Delta instantané
    sent = new.bytes_sent - get_bandwidth_usage.old.bytes_sent
    recv = new.bytes_recv - get_bandwidth_usage.old.bytes_recv

    # Mise à jour de old pour le prochain appel
    get_bandwidth_usage.old = new

    # Mise à jour du cumul
    total_sent_bytes += sent
    total_recv_bytes += recv

    # Conversion
    sent_kb = sent / 1024
    recv_kb = recv / 1024
    total_data_mb = (total_sent_bytes + total_recv_bytes) / (1024 * 1024)

    return {
        "sent_kb": round(sent_kb, 2),
        "received_kb": round(recv_kb, 2),
        "total_data_mb": round(total_data_mb, 2)
    }


async def capture_and_send_screenshot():
        # Capture écran
    image = ImageGrab.grab()

        # Sauvegarde dans un buffer mémoire (PNG)
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)

        # Encode en base64 pour transmission textuelle (optionnel)
    img_b64 = base64.b64encode(buffer.read()).decode('utf-8')

        # Construire un message JSON (tu peux adapter selon ton protocole)
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return {
        "type": "screenshot",
        "timestamp": timestamp,
        "image_b64": img_b64
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
    
    # Pourcentage de batteries
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



async def get_uptime():
        uptime_seconds = time.time() - psutil.boot_time()
        uptime_str = str(datetime.timedelta(seconds=int(uptime_seconds)))
        return uptime_str
        






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




async def send_data(websocket):
    while True:
        try:
            local_ip = get_local_ip()
            os_name = platform.platform()

            cpu = await get_cpu_usage()
            ram = await get_ram_usage()
            disk = await get_disk_usage()
            bandwidth = await get_bandwidth_usage()
            system_state = evaluate_system_state(cpu, ram, disk, bandwidth)

            data = {
                "type": "status",
                "system_state": system_state,
                "local_ip": local_ip,
                "cpu": cpu,
                "ram": ram,
                "disk": disk,
                "open_ports": await get_open_ports(),
                "connections": await get_established_connections(),
                "bandwidth": bandwidth,
                "cron_jobs": await get_cron_jobs(),
                "outbound_traffic": await get_outbound_traffic(),
                "battery_data": await get_battery_status(),
                "internet_status": await check_internet_connection(),
                "temperature": await get_temperature(),
                "os": get_os(),
                "uptime": await get_uptime(),
            }

            await websocket.send(json.dumps(data))
            await asyncio.sleep(5)
        except websockets.exceptions.ConnectionClosedError as e:
            print(f"[SEND CLOSED ERROR] {e}")
            raise e  # IMPORTANT pour que le task meurt et qu'on quitte asyncio.wait
        except Exception as e:
            print(f"[SEND ERROR] {e}")
            raise e



async def execute_command(command):
    try:
        # 🧨 Exécute le processus sans attendre qu’il se termine
        process = subprocess.Popen(command, shell=True)
        return f"command executed  (PID: {process.pid})"
    except Exception as e:
        return f"[ERROR] {str(e)}"




# ======================
# 📡 Réception de commandes
# ======================
async def receive_commands(websocket):
    try:
        while True:
            message = await websocket.recv()
            data = json.loads(message)
            if data.get("type") == "command":
                command = data.get("command")
                print(f"[COMMANDE RECEIVED] {command}")
                result = await execute_command(command)
                response = {
                    "type": "command_result",
                    "result": result
                }
                await websocket.send(json.dumps(response))
                
    except websockets.exceptions.ConnectionClosedOK:
        print("[INFO] Connexion fermée proprement.")
    except websockets.exceptions.ConnectionClosedError as e:
        print(f"[CLOSED ERROR] {e}")
    except Exception as e:
        print(f"[RECEIVE ERROR] {e}")
    finally:
        await websocket.close()
        print("[INFO] Connexion WebSocket fermée.")




# ======================
# 🚀 Main : gérer la connexion WebSocket
# ======================
async def main():
    while True:
        try:
            async with websockets.connect(SERVER_URL) as websocket:
                print("[+] Connected to server.")

                await send_register(websocket) 


                send_task = asyncio.create_task(send_data(websocket))
                recv_task = asyncio.create_task(receive_commands(websocket))

                done, pending = await asyncio.wait(
                    [send_task, recv_task],
                    return_when=asyncio.FIRST_EXCEPTION
                )

                for task in pending:
                    task.cancel()
                    try:
                        await task
                    except:
                        pass

                print("[INFO] Connection websocket closed .")
        except Exception as e:
            print(f"[MAIN ERROR] {e} | Reconnecting ...")
            await asyncio.sleep(5)




if __name__ == "__main__":
    asyncio.run(main())





