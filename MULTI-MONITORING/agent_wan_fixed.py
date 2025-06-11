import asyncio
import time
import json
import subprocess
import platform
import psutil
import datetime
import socket
import os
import requests

import websockets
#from PIL import ImageGrab # Commented out, uncomment and install Pillow if needed
import tkinter as tk
import io # Added for screenshot buffer

from threading import Thread

import base64



# L'URL de l'API PHP qui retourne l'adresse du serveur WebSocket
API_URL = "https://tsilavina.alwaysdata.net/urls.php"

while True:
    try:
        response = requests.get(API_URL, timeout=5)  # timeout pour éviter blocage
        data = response.json()
        SERVER_URL = data["url"].replace("http://", "ws://")
        #print(f"[+URL : {SERVER_URL}")
        break  # Succès, on sort de la boucle

    except Exception as e:
        print(f"[-] ERRROR FATA : {e}")
        print("[*] Retry")
        time.sleep(5)






async def send_register(websocket):
    agent_ip = get_local_ip()
    register_payload = {
        "type": "register",
        "ip": agent_ip
    }
    await websocket.send(json.dumps(register_payload))
    print(f">> Agent connected : {agent_ip}")


# Fonction pour récupérer l'adresse IP locale de la machine de manière plus robuste
def get_local_ip():
    # Définir les plages d'adresses IP privées
    private_ip_ranges = [
        "10.",
        "172.16.", "172.17.", "172.18.", "172.19.", "172.20.",
        "172.21.", "172.22.", "172.23.", "172.24.", "172.25.",
        "172.26.", "172.27.", "172.28.", "172.29.", "172.30.", "172.31.",
        "192.168."
    ]

    for interface, addrs in psutil.net_if_addrs().items():
        for addr in addrs:
            if addr.family == socket.AF_INET:
                ip_address = addr.address
                # Vérifier si l'adresse est une adresse privée
                for private_prefix in private_ip_ranges:
                    if ip_address.startswith(private_prefix):
                        # On a trouvé une adresse IP privée
                        return ip_address
    
    # Si aucune adresse IP privée n'est trouvée, retourner localhost ou None
    return "127.0.0.1" # Ou None, selon votre préférence si aucune IP privée n'est active


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
            print(f">> RECONNECT TO SERVER {backoff_time}s...")
            await asyncio.sleep(backoff_time)  # Attente avant de tenter la reconnexion
            # Removed direct call to send_data, main loop handles reconnection
            break  # If connection attempt is successful (handled by main), exit
        except Exception as e:
            print(f">> ERROR WHEN CONNECT: {e}")
            backoff_time = min(backoff_time * 2, max_backoff)


async def run_command(cmd):
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await proc.communicate()

    return stdout.decode('utf-8', errors='ignore')  # 🔥 UTF-8 + ignore erreurs


async def resolve_ip(ip):
    try:
        # Tentative de résolution de l'IP en utilisant gethostbyaddr
        # This is a blocking call, for true async, might need to run in a thread pool
        # For typical use, it might be acceptable for occasional calls.
        loop = asyncio.get_event_loop()
        host_info = await loop.run_in_executor(None, socket.gethostbyaddr, ip)
        return host_info[0]  # Le nom d'hôte
    except socket.herror:
        # Erreur lors de la résolution de l'adresse IP (pas de nom d'hôte trouvé)
        return None
    except OSError as e:
        print(f"ERROR WHEN GET IP {ip}: {e}")
        return None


async def get_established_connections():
    connections = []
    # psutil.net_connections is generally fast enough, but iterating through many can be slow.
    # If this becomes a bottleneck, consider reducing frequency or optimizing hostname lookups.
    for conn in psutil.net_connections(kind='inet'):
        if conn.status == "ESTABLISHED" and conn.raddr:
            # hostname = await resolve_ip(conn.raddr.ip) # This could be slow if there are many connections
            # For performance, temporarily omit or make resolve_ip optional based on needs.
            connections.append({
                "ip": conn.raddr.ip,
                "port": conn.raddr.port,
                "hostname": "Unknown" # Setting to unknown for now to avoid blocking resolve_ip
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
    # Call cpu_percent without interval for non-blocking. First call returns 0.0.
    # Second call after a short sleep gives actual usage since last call.
    psutil.cpu_percent(interval=None) # First call to initialize
    await asyncio.sleep(0.1) # Short await to allow CPU usage to be measured
    return psutil.cpu_percent(interval=None) # Second call for actual percentage

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

    await asyncio.sleep(1) # Changed from time.sleep(1) to asyncio.sleep(1)
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


# If ImageGrab is to be used, uncomment and ensure Pillow is installed.
# It should also be run in a separate thread or process if performance is critical.
# from PIL import ImageGrab
# async def capture_and_send_screenshot():
#     # Capture écran (blocking call, consider running in executor)
#     loop = asyncio.get_event_loop()
#     image = await loop.run_in_executor(None, ImageGrab.grab)

#     # Sauvegarde dans un buffer mémoire (PNG)
#     buffer = io.BytesIO()
#     image.save(buffer, format="PNG")
#     buffer.seek(0)

#     # Encode en base64 pour transmission textuelle
#     img_b64 = base64.b64encode(buffer.read()).decode('utf-8')

#     # Construire un message JSON
#     timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#     return {
#         "type": "screenshot",
#         "timestamp": timestamp,
#         "image_b64": img_b64
#     }



async def get_cron_jobs():
    if platform.system().lower() == "windows":
        import winreg
        locations = [
            (winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\Run"),
            (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run")
        ]
        startup_programs = []

        for hive, path in locations:
            try:
                # winreg operations are generally fast, but if many entries, it adds up.
                with winreg.OpenKey(hive, path) as key:
                    i = 0
                    while True:
                        try:
                            name, value, _ = winreg.EnumValue(key, i)
                            startup_programs.append({
                                "Name": name,
                                "Command": value,
                                "Location": f"{'HKLM' if hive == winreg.HKEY_LOCAL_MACHINE else 'HKCU'}\\{path}"
                            })
                            i += 1
                        except OSError:
                            break
            except FileNotFoundError:
                continue

        return json.dumps(startup_programs, indent=4)
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
    
    percent = battery.percent
    on_ac_power = battery.power_plugged
    status = "On AC power" if on_ac_power else "Running on battery"

    return {
        "battery_percent": percent,
        "battery_status": status
    }


async def check_internet_connection():
    try:
        # Use asyncio.create_subprocess_exec for non-blocking ping
        proc = await asyncio.create_subprocess_exec(
            "ping", "-n" if platform.system().lower() == "windows" else "-c", "1", "8.8.8.8",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()
        if proc.returncode == 0:
            return "Up"
        else:
            return "Down"
    except Exception as e:
        return "Down"

        
""" Tsy mandeha NOT WORK"""
async def get_temperature():
    sensors = psutil.sensors_temperatures()
    
    if not sensors:
        return "Temperature not available"

    for sensor_name, sensor_list in sensors.items():
        for sensor in sensor_list:
            if 'cpu' in sensor_name.lower():
                return f"CPU Temperature: {sensor.current}°C"

    return "CPU Temperature not available"


async def get_uptime():
        uptime_seconds = time.time() - psutil.boot_time()
        uptime_str = str(datetime.timedelta(seconds=int(uptime_seconds)))
        return uptime_str


allowed_processes = set()


async def allow_connection():
    global allowed_processes # Typo fix: allowed_processess -> allowed_processes

    # print(f"PROCESSUS ALLOWED  : {allowed_processes}") # Uncomment for debugging

    seen = set()
    unauthorized_processes = []

    # Iterating through all processes can be heavy, but necessary for this check.
    # Consider reducing frequency if performance is an issue.
    for proc in psutil.process_iter(['pid', 'name']):
        pid = proc.info['pid']
        name = proc.info['name'].lower()

        if pid and pid not in seen:
            try:
                if name not in allowed_processes:
                    unauthorized_processes.append({
                        "pid": pid,
                        "name": name,
                        "status": "unauthorized"
                    })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

            seen.add(pid)

    return {
        "type": "unauthorized_processes_alert",
        "processes": unauthorized_processes
    }


async def get_outbound_traffic():
    connections = []
    # This also iterates through all connections, similar considerations as above.
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

            # Concurrent execution of async functions for better performance
            cpu, ram, disk, bandwidth, open_ports, established_connections, cron_jobs, outbound_traffic, battery_data, internet_status, unauthorized_procs, uptime = await asyncio.gather(
                get_cpu_usage(),
                get_ram_usage(),
                get_disk_usage(),
                get_bandwidth_usage(),
                get_open_ports(),
                get_established_connections(),
                get_cron_jobs(),
                get_outbound_traffic(),
                get_battery_status(),
                check_internet_connection(),
                allow_connection(),
                get_uptime()
            )
            
            system_state = evaluate_system_state(cpu, ram, disk, bandwidth)

            agent_type = "wan"

            data = {
                "type": "status",
                "agent_type": agent_type,
                "system_state": system_state,
                "local_ip": local_ip,
                "cpu": cpu,
                "ram": ram,
                "disk": disk,
                "open_ports": open_ports,
                "connections": established_connections,
                "bandwidth": bandwidth,
                "cron_jobs": cron_jobs,
                "outbound_traffic": outbound_traffic,
                "battery_data": battery_data,
                "internet_status": internet_status,
                "allow_connection": unauthorized_procs, # Renamed for clarity on the server side
                "os": get_os(),
                "uptime": uptime,
            }

            await websocket.send(json.dumps(data))
            await asyncio.sleep(2) # You might want to adjust this interval based on server load and desired granularity
        except websockets.exceptions.ConnectionClosedError as e:
            print(f"[SEND CLOSED ERROR] {e}")
            raise e
        except Exception as e:
            print(f"[SEND ERROR] {e}")
            raise e


async def execute_command(command, timeout=10):
    local_ip = get_local_ip()
    output_lines = []

    try:
        process = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        async def read_output(stream, collector):
            while True:
                line = await stream.readline()
                if line:
                    decoded_line = line.decode(errors='ignore').strip()
                    collector.append(decoded_line)
                else:
                    break

        try:
            await asyncio.wait_for(asyncio.gather(
                read_output(process.stdout, output_lines),
                read_output(process.stderr, output_lines),
                process.wait()
            ), timeout=timeout)

        except asyncio.TimeoutError:
            process.kill()
            output_lines.append(f"[TIMEOUT] Command took too long (> {timeout}s) and was terminated.")
        except Exception as e:
            output_lines.append(f"[ERROR] Subprocess error: {e}")

        result = f"[+] {local_ip} >>\n" + "\n".join(output_lines)
        return result

    except Exception as e:
        return f"[-]{local_ip} >> [ERROR] {str(e)}"


# ======================
# 📢 Fonction pour afficher une popup/message
# ======================
# root.after(10000, root.destroy)
def show_popup(message):
    os_type = platform.system()

    def popup():
        root = tk.Tk()
        root.title(">> MESSAGE DU DEPARTEMENT INFORMATIQUE:")
        root.geometry("1366x768")  
        root.resizable(False, False)
        root.configure(bg="black")

        # ✅ Centrage vertical et horizontal
        msg_label = tk.Label(
            root,
            text=message,
            bg="black",
            fg="green",
            font=("Fira Code", 14, "bold"),  # Police plus grande et en gras
            wraplength=460,
            justify="center"  # ✅ Centre horizontalement
        )
        msg_label.place(relx=0.5, rely=0.5, anchor="center")  # ✅ Centre parfaitement dans la fenêtre


     
        root.mainloop()

    Thread(target=popup).start()

# ======================
# 🧠 Nouveau : Gérer réception de message texte
# ======================
async def handle_text_message(data):
    message = data.get("message", "")
    print(f"[TEXT MESSAGE RECEIVED] {message}")
    # Run show_popup in a separate thread as it uses Tkinter
    show_popup(message)


# ======================
# 📡 Réception de commandes
# ======================
async def receive_commands(websocket):
    global allowed_processes
    try:
        while True:
            message = await websocket.recv()
            data = json.loads(message)
            if data.get("type") == "command":
                command = data.get("command")
                print(f"[COMMANDE RECEIVED] {command}")
                result = await execute_command(command)
                local_ip = get_local_ip() 
                response = {
                    "type": "command_result",
                    "result": result,
                    "ip" : local_ip 
                }
                print(f"IP : {local_ip}")
                await websocket.send(json.dumps(response))

            elif data.get("type") == "message":
                await handle_text_message(data)

            elif data.get("type") == "process_config_broadcast":
                print("[+] Process allowed:")
                allowed_list = data.get("allowed_processes", [])
                allowed_processes = set(proc.lower() for proc in allowed_list)
                print(allowed_processes)
                
    except websockets.exceptions.ConnectionClosedOK:
        print("[INFO] Connection forced to close.")
    except websockets.exceptions.ConnectionClosedError as e:
        print(f"[CLOSED ERROR] {e}")
    except Exception as e:
        print(f"[RECEIVE ERROR] {e}")
    finally:
        # No need to close websocket here, the main loop handles it.
        # This block might get executed after a connection error,
        # but the main loop will attempt reconnection.
        print("Websocket receive task ended.")


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

                # Wait for any of the tasks to complete or raise an exception
                done, pending = await asyncio.wait(
                    [send_task, recv_task],
                    return_when=asyncio.FIRST_COMPLETED # Use FIRST_COMPLETED to react faster
                                                        # if one task finishes or errors
                )

                for task in done:
                    try:
                        await task # Await completed tasks to propagate exceptions
                    except Exception as e:
                        print(f"Task raised an exception: {e}")

                for task in pending:
                    task.cancel() # Cancel remaining tasks
                    try:
                        await task # Await cancelled tasks to ensure cleanup
                    except asyncio.CancelledError:
                        pass # Expected if cancelled
                    except Exception as e:
                        print(f"Error during task cancellation: {e}")

                print("[INFO] >> Connection websocket closed.")
        except Exception as e:
            print(f"[MAIN ERROR] {e} | Reconnecting in 5 seconds...")
            await asyncio.sleep(5)


if __name__ == "__main__":
    asyncio.run(main())