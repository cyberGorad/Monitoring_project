import asyncio
import ipaddress
import json
import subprocess
import psutil
import socket
import datetime


import time
import platform
import pyudev
import threading
import os
from pynput.keyboard import Listener, Key
from scapy.all import sniff, IP, TCP
from collections import defaultdict
from channels.generic.websocket import AsyncWebsocketConsumer

CONFIG_PATH_PORTS = "config/settings_ports.json"
CONFIG_PATH_PROCESSES = "config/settings_processes.json"



# executer commande et recupere sortie
def run_command(command):
    try:
        result = subprocess.check_output(command, shell=True, text=True)
        return result
    except subprocess.CalledProcessError as e:
        print(f"Erreur lors de l'exécution de la commande {command}: {e}")
        return None

# nslookup du IP
def resolve_ip(ip):
    try:
        host = socket.gethostbyaddr(ip)
        return host[0]
    except socket.herror:
        return None

        

# Fonction pour obtenir les connexions établies
def get_established_connections():
    netstat_command = "netstat -tunp"
    netstat_output = run_command(netstat_command)

    if not netstat_output:
        return []

    established_connections = []
    for line in netstat_output.splitlines():
        if "ESTABLISHED" in line:
            parts = line.split()
            ip_address = parts[4].split(":")[0]  # L'adresse IP distante est à la 5ème colonne

            # Exclure localhost (127.0.0.1)
            if ip_address == "127.0.0.1":
                continue

            # Résoudre l'adresse IP en nom d'hôte
            hostname = resolve_ip(ip_address)
            established_connections.append({
                'ip': ip_address,
                'hostname': hostname if hostname else 'Inconnu'
            })

    return established_connections

# Fonction pour convertir les octets en unités lisibles
def bytes_to_human(bytes_value):
    symbols = ['B', 'KB', 'MB', 'GB', 'TB']
    step = 1024
    index = 0
    while bytes_value >= step and index < len(symbols) - 1:
        bytes_value /= step
        index += 1
    return f"{bytes_value:.2f} {symbols[index]}"

def bytes_to_mb(bytes_value):
    return round(bytes_value / (1024 * 1024), 2)





def get_machine_id():
    # Obtenir toutes les interfaces réseau
    for interface, addrs in psutil.net_if_addrs().items():
        for addr in addrs:
            # Vérifier si l'adresse n'est pas une adresse de loopback
            if addr.family == socket.AF_INET and addr.address != '127.0.0.1':
                return addr.address
    



def format_duration(seconds):
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours}h {minutes}min {seconds}s"




def run_curl_command():
    # Commande curl pour appeler l'API Gemini
    curl_command = [
        "curl", 
        "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=AIzaSyDUzu9hIkc6hfh5GGZUjov8V8BMgK6yDgg", 
        "-H", "Content-Type: application/json", 
        "-X", "POST", 
        "-d", json.dumps({
            "contents": [{
                "parts": [{"text": "hello gemini"}]
            }]
        })
    ]
    
    try:
        # Exécution de la commande curl
        result = subprocess.check_output(curl_command, text=True)
        print(f"Réponse de l'API Gemini :\n{result}")  # Affiche le résultat dans le terminal
        return result
    except subprocess.CalledProcessError as e:
        print(f"Erreur lors de l'exécution de la commande curl: {e}")
        return None

""" GET STARTUP APPS AND SERVICES """
"""autostart_files": run_command("cat ~/.config/autostart/*.desktop 2>/dev/null || echo 'Aucun .desktop'"),"""
def get_linux_startup_info():
    return {
        "systemd_enabled_services": run_command("systemctl list-unit-files --type=service --state=enabled"),

        "cron_reboot_entries": run_command("crontab -l | grep '@reboot' || echo 'Aucun cron @reboot'")
    }


def get_windows_startup_info():
    return {
        "startup_registry_current_user": run_command("reg query HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run"),
        "startup_registry_all_users": run_command("reg query HKLM\\Software\\Microsoft\\Windows\\CurrentVersion\\Run"),
        "startup_folder": run_command("dir \"%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\Startup\" /b"),
        "scheduled_tasks": run_command("schtasks /Query /FO LIST /V")
    }
"""END STARTUP SERVICES """




""" WINDOWS CODE A TESTER """
""" def parse_registry_output(output):
    lines = output.splitlines()
    entries = {}
    for line in lines:
        parts = re.split(r'\s{2,}', line.strip())
        if len(parts) >= 3:
            name, _, path = parts[0], parts[1], parts[2]
            entries[name] = path
    return entries

def parse_startup_folder(output):
    return [line.strip() for line in output.splitlines() if line.strip()]

def parse_schtasks(output):
    tasks = []
    current = {}
    for line in output.splitlines():
        if not line.strip():
            if all(k in current for k in ('TaskName', 'Task To Run')):
                tasks.append({
                    "TaskName": current.get("TaskName"),
                    "Command": current.get("Task To Run"),
                    "Status": current.get("Status", "N/A"),
                    "NextRunTime": current.get("Next Run Time", "N/A"),
                    "LastRunTime": current.get("Last Run Time", "N/A"),
                    "Author": current.get("Author", "Unknown")
                })
            current = {}
        else:
            key_value = line.split(":", 1)
            if len(key_value) == 2:
                key, value = key_value
                current[key.strip()] = value.strip()
    return tasks

def get_windows_startup_info():
    return {
        "Startup_Registry_Current_User": parse_registry_output(
            run_command("reg query HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run")
        ),
        "Startup_Registry_All_Users": parse_registry_output(
            run_command("reg query HKLM\\Software\\Microsoft\\Windows\\CurrentVersion\\Run")
        ),
        "Startup_Folder_Items": parse_startup_folder(
            run_command("dir \"%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\Startup\" /b")
        ),
        "Scheduled_Tasks": parse_schtasks(
            run_command("schtasks /Query /FO LIST /V")
        )
    } """

async def get_cpu_usage():
    return psutil.cpu_percent(interval=1)
async def get_ram_usage():
    return psutil.virtual_memory().percent
    
async def get_bandwidth_usage():
    old_data = psutil.net_io_counters()
    await asyncio.sleep(1)
    new_data = psutil.net_io_counters()
    return {
        "sent_kb": (new_data.bytes_sent - old_data.bytes_sent) / 1024.0,
        "received_kb": (new_data.bytes_recv - old_data.bytes_recv) / 1024.0,
    }

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



async def run_command_async(command):
    proc = await asyncio.create_subprocess_shell(
        command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await proc.communicate()
    return stdout.decode().strip() if stdout else stderr.decode().strip()




class MultiMonitorConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        
    
        await self.accept()
        await self.load_allowed_ports()
        await self.load_allowed_process()


        await self.send(json.dumps({"type": "firewall_status", "iptables": "Ready to receive IPs."}))
        

        



        
        # Crée des tâches pour les scripts de surveillacnce
        
        self.port_monitor_task = asyncio.create_task(self.monitor_ports())
        self.system_monitor_task = asyncio.create_task(self.monitor_system())
        self.connection_monitor_task = asyncio.create_task(self.monitor_connections())
        self.network_monitor_task = asyncio.create_task(self.monitor_bandwidth())  
        self.cron_monitor_task = asyncio.create_task(self.monitor_cron_jobs())
        self.log_monitor_task = asyncio.create_task(self.monitor_logs())
        self.outbound_traffic_task = asyncio.create_task(self.monitor_outbound_traffic())
        self.monitor_startup_info_task = asyncio.create_task(self.monitor_startup_info())
        self.monitor_usb_task = asyncio.create_task(self.monitor_usb())
        self.get_disk_usage_task = asyncio.create_task(self.get_disk_usage())
        self.get_sorted_processes_by_memory_task = asyncio.create_task(self.get_sorted_processes_by_memory())
        self.RubberDuckyMonitor_task = asyncio.create_task(self.RubberDuckyMonitor())
        self.allow_connection_task = asyncio.create_task(self.allow_connection())
        self.check_firewall_status_task = asyncio.create_task(self.check_firewall_status())
        self.check_internet_connection_task = asyncio.create_task(self.check_internet_connection())
        self.get_active_ssh_sessions_task = asyncio.create_task(self.get_active_ssh_sessions())

      



    async def disconnect(self, close_code):
        # Annule les tâches
        self.port_monitor_task.cancel()
        self.system_monitor_task.cancel()
        self.connection_monitor_task.cancel()
        self.network_monitor_task.cancel()
        self.cron_monitor_task.cancel()
        self.outbound_traffic_task.cancel()
        self.monitor_startup_info_task.cancel()
        self.monitor_usb_task.cancel()
        self.get_disk_usage_task.cancel()
        self.get_sorted_processes_by_memory_task.cancel()
        self.RubberDuckyMonitor_task.cancel()
        self.allow_connection_task.cancel()
        self.check_firewall_status_task.cancel()
        self.check_internet_connection_task.cancel()
        self.get_active_ssh_sessions_task.cancel()

        
    """
    WINDOWS
    import json
import subprocess
import platform

async def receive(self, text_data):
    data = json.loads(text_data)
    type_action = data.get("type")

    if platform.system() != "Windows":
        await self.send(json.dumps({
            "type": "firewall_status",
            "iptables": "Ce système n'est pas Windows. Utilisez iptables pour Linux."
        }))
        return

    if type_action == "add_ip":
        ip = data.get("ip")
        if self.is_valid_ip(ip):
            try:
                cmd1 = ["netsh", "advfirewall", "firewall", "add", "rule", "name=Allow_In_{}".format(ip),
                        "dir=in", "action=allow", "remoteip={}".format(ip), "protocol=any"]
                cmd2 = ["netsh", "advfirewall", "firewall", "add", "rule", "name=Allow_Out_{}".format(ip),
                        "dir=out", "action=allow", "remoteip={}".format(ip), "protocol=any"]
                subprocess.run(cmd1, check=True, shell=True)
                subprocess.run(cmd2, check=True, shell=True)

                await self.send(json.dumps({
                    "type": "firewall_status",
                    "iptables": f"L'adresse IP {ip} a été autorisée dans le pare-feu Windows."
                }))
            except Exception as e:
                await self.send(json.dumps({
                    "type": "firewall_status",
                    "iptables": f"Erreur lors de l'ajout de l'IP : {str(e)}"
                }))
        else:
            await self.send(json.dumps({
                "type": "firewall_status",
                "iptables": "Adresse IP invalide."
            }))

    elif type_action == "set_policy":
        try:
            # Désactiver toutes les règles existantes (optionnel et dangereux si mal utilisé)
            subprocess.run(["netsh", "advfirewall", "reset"], check=True, shell=True)

            # Bloquer tout sauf localhost
            subprocess.run(["netsh", "advfirewall", "set", "allprofiles", "firewallpolicy", "blockinbound,allowoutbound"], check=True, shell=True)
            subprocess.run(["netsh", "advfirewall", "firewall", "add", "rule", "name=Allow_Localhost", "dir=in",
                            "action=allow", "remoteip=127.0.0.1", "protocol=any"], check=True, shell=True)

            await self.send(json.dumps({
                "type": "firewall_status",
                "iptables": "Politique pare-feu Windows définie : tout bloqué sauf localhost."
            }))
        except subprocess.CalledProcessError as e:
            await self.send(json.dumps({
                "type": "firewall_status",
                "iptables": f"Erreur lors de l'application de la politique : {str(e)}"
            }))

    """






    async def get_active_ssh_sessions(self):
        try:
            proc = await asyncio.create_subprocess_exec(
                'ss', '-tnp',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await proc.communicate()

            if proc.returncode != 0:
                print("ERROR: :", stderr.decode())
                return

            print("SSH connection actives :\n")
            for line in stdout.decode().splitlines():
                if ':22' in line and 'ESTAB' in line and 'sshd' in line:
                    # Extraction IP distante (peer)
                    peer_match = re.search(r'\s(\[::ffff:(\d+\.\d+\.\d+\.\d+)\]|(\d+\.\d+\.\d+\.\d+)):(\d+)\s+users', line)
                    if peer_match:
                        ip = peer_match.group(2) if peer_match.group(2) else peer_match.group(3)
                    else:
                        ip = "remote IP unknown"

                    # Extraction PID du premier sshd dans users
                    pid_match = re.search(r'users:\(\("sshd",pid=(\d+)', line)
                    if pid_match:
                        pid = pid_match.group(1)

                        ps_proc = await asyncio.create_subprocess_exec(
                            'ps', '-o', 'user=', '-p', pid,
                            stdout=asyncio.subprocess.PIPE
                        )
                        user_out, _ = await ps_proc.communicate()
                        user = user_out.decode().strip()
                    else:
                        pid = None
                        user = "user unknown"

                    print(f"➡️  users : {user} | IP : {ip} | PID : {pid}")

        except Exception as e:
            print("Erreur lors de l’analyse des connexions SSH :", e)

        await self.send(json.dumps({
            "type": "ssh_user",
            "user": user,
            "ip": ip,
            "pid":pid,
        }))
        await asyncio.sleep(5)







    async def check_internet_connection(self):
        while True:
            try:
                process = await asyncio.create_subprocess_exec(
                    "ping", "-c", "3", "8.8.8.8",
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                stdout, stderr = await process.communicate()

                status = "Up" if process.returncode == 0 else "Down"
            except Exception as e:
                status = "ERROR"

            await self.send(json.dumps({
                "type": "internet-status",
                "internet_status": status,
            }))

            await asyncio.sleep(5)


    async def run_cmd(*cmd):
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        if process.returncode != 0:
            raise Exception(stderr.decode())
        return stdout.decode()



#ALLOWED PORTS

    
    async def save_allowed_ports(self, ports):
        config = {"allowed_ports": ports}
        with open(CONFIG_PATH_PORTS, "w") as f:
            json.dump(config, f, indent=4)

    async def save_allowed_process(self, process):
        config = {"allowed_process": process}
        with open(CONFIG_PATH_PROCESSES, "w") as f:
            json.dump(config, f, indent=4)



    async def load_allowed_ports(self):
        try:
            if os.path.exists(CONFIG_PATH_PORTS):
                with open(CONFIG_PATH_PORTS, "r") as f:
                    config = json.load(f)
                    ports = config.get("allowed_ports", [])
                    if isinstance(ports, list) and all(isinstance(p, int) for p in ports):
                        self.allowed_ports = set(ports)
                        print("[Config load success] =>", self.allowed_ports)
                    else:
                        self.allowed_ports = set()
            else:
                self.allowed_ports = set()
        except Exception as e:
            print("[ERROR]", str(e))
            self.allowed_ports = set()


    async def load_allowed_process(self):
        try:
            if os.path.exists(CONFIG_PATH_PROCESSES):
                with open(CONFIG_PATH_PROCESSES, "r") as f:
                    config = json.load(f)
                    process = config.get("allowed_process", [])
                    if isinstance(process, list) and all(isinstance(p, str) for p in process):
                        self.allowed_processes = set(process)
                        print("[Config load success] =>", self.allowed_processes)
                    else:
                        self.allowed_processes = set()
            else:
                self.allowed_processes = set()
        except Exception as e:
            print("[ERROR]", str(e))
            self.allowed_processes = set()






    async def receive(self, text_data):
        data = json.loads(text_data)
        type_action = data.get("type")

        if type_action == "add_ip":
            ip = data.get("ip")

            if self.is_valid_ip(ip):
                try:
                    cmd1 = ["sudo", "iptables", "-A", "INPUT", "-s", ip, "-j", "ACCEPT"]
                    cmd2 = ["sudo", "iptables", "-A", "OUTPUT", "-d", ip, "-j", "ACCEPT"]
                    subprocess.run(cmd1, check=True)
                    subprocess.run(cmd2, check=True)
                    await self.send(json.dumps({
                        "type": "firewall_status",
                        "iptables": f"Access Granted for {ip} "
                    }))
                except Exception as e:
                    await self.send(json.dumps({
                        "type": "firewall_status",
                        "iptables": f"ERROR : {str(e)}"
                    }))
            else:
                await self.send(json.dumps({
                    "type": "firewall_status",
                    "iptables": "IP NOT VALID"
                }))

        elif type_action == "set_policy":
            try:
                subprocess.run(["sudo", "iptables", "-F"], check=True)  # flush all rules
                subprocess.run(["sudo", "iptables", "-A", "INPUT", "-m", "conntrack", "--ctstate", "ESTABLISHED,RELATED", "-j", "ACCEPT"], check=True)
                subprocess.run(["sudo", "iptables", "-A", "INPUT", "-s", "127.0.0.1", "-j", "ACCEPT"], check=True)
                subprocess.run(["sudo", "iptables", "-P", "INPUT", "DROP"], check=True)
                subprocess.run(["sudo", "iptables", "-P", "FORWARD", "DROP"], check=True)
                subprocess.run(["sudo", "iptables", "-P", "OUTPUT", "ACCEPT"], check=True)
                        
                await self.send(json.dumps({
                    "type": "firewall_status",
                    "iptables": "All connection disabled"
                }))
            except subprocess.CalledProcessError as e:
                await self.send(json.dumps({
                    "type": "firewall_status",
                    "iptables": f"ERROR: {str(e)}"
                }))
        elif type_action == "clear_rules":  # attention à la casse et au nom ici
            try:
                
                reset1 = ["sudo", "iptables", "-P", "INPUT", "ACCEPT"]
                reset2 = ["sudo", "iptables", "-P", "OUTPUT", "ACCEPT"]
                reset3 = ["sudo", "iptables", "-F"]  # flush all rule
                subprocess.run(reset1, check=True)
                subprocess.run(reset2, check=True)
                subprocess.run(reset3, check=True)


                await self.send(json.dumps({
                    "type": "firewall_status",
                    "iptables": "clear success!"
                }))
            except subprocess.CalledProcessError as e:
                await self.send(json.dumps({
                    "type": "firewall_status",
                    "iptables": f"ERROR : Try again: {str(e)}"
                }))

        elif type_action == "shutdown":
            try:

                shutdown = ["sudo", "init", "0"]
                subprocess.run(shutdown, check=True)




            except error as e:
                print(f'ERROR: {e}')
        elif type_action == "kill-process":
            print("KILL PROCESS")
            pid = data["pid"]
            try:
                p = psutil.Process(pid)
                p.kill()  # ou p.kill() si tu veux forcer  / p.terminate()
                await self.send(json.dumps({
                    "type": "process-killed",
                    "pid": pid,
                    "status": "success"
                }))
            except Exception as e:
                await self.send(json.dumps({
                    "type": "process-killed",
                    "pid": pid,
                    "status": "error",
                    "message": str(e)
                }))



        elif type_action == "upload_port_config":
            global authorized_ports
            try:
                # Récupérer le contenu JSON brut envoyé depuis le front (ex: {type: ..., allowed_ports: [...]})
                ports = data.get("allowed_ports", [])

                # Vérifier que c'est bien une liste d'entiers
                if isinstance(ports, list) and all(isinstance(p, int) for p in ports):
                    # Sauvegarder dans un fichier (optionnel mais utile)
                    await self.save_allowed_ports(ports)

                    # Mettre à jour les ports autorisés dans l'objet WebSocket consumer
                    self.allowed_ports = set(ports)
                    authorized_ports = set(ports)

                    # 🔥 Print dans la console du serveur pour debug
                    print("[🔐 PORTS AUTORISÉS MAJ] =>", authorized_ports)

                    # Réponse au client WebSocket
                    await self.send(json.dumps({
                        "type": "upload_response",
                        "status": "success",
                        "message": "Ports autorisés mis à jour en live."
                    }))
                else:
                    await self.send(json.dumps({
                        "type": "upload_response",
                        "status": "error",
                        "message": "Format des ports invalide. Liste d'entiers attendue."
                    }))
                    
            except Exception as e:
                print("[❌ ERREUR upload_port_config] =>", str(e))
                await self.send(json.dumps({
                    "type": "upload_response",
                    "status": "error",
                    "message": f"Erreur côté serveur: {str(e)}"
                }))


        elif type_action == "upload_process_config":
            global authorized_process
            try:
                # Récupérer le contenu JSON brut envoyé depuis le front (ex: {type: ..., allowed_ports: [...]})
                process = data.get("allowed_process", [])

                # Vérifier que c'est bien une liste d'entiers
                if isinstance(process, list) and all(isinstance(p, str) for p in process):
                    # Sauvegarder dans un fichier (optionnel mais utile)
                    await self.save_allowed_process(process)

                    # Mettre à jour les ports autorisés dans l'objet WebSocket consumer
                    self.allowed_process = set(process)
                    authorized_process = set(process)

                    # 🔥 Print dans la console du serveur pour debug
                    print("[🔐 PROCESS AUTORISÉS MAJ] =>", authorized_process)

                    # Réponse au client WebSocket
                    await self.send(json.dumps({
                        "type": "upload_response",
                        "status": "success",
                        "message": "Process updated."
                    }))
                else:
                    await self.send(json.dumps({
                        "type": "upload_response",
                        "status": "error",
                        "message": "Error when updating process"
                    }))
                    
            except Exception as e:
                print("[❌ ERREUR upload_port_config] =>", str(e))
                await self.send(json.dumps({
                    "type": "upload_response",
                    "status": "error",
                    "message": f"ERROR 500: {str(e)}"
                }))








    def is_valid_ip(self, ip):
        try:
            ipaddress.ip_address(ip)
            return True
        except ValueError:
            return False




    async def check_firewall_status(self):
        system = platform.system()
        firewall_status = {
            "type": "firewall_status",
            "windows": "Yes",
            "iptables": "Vrai",
            
            }


        try:
            if system == "Windows":
                result = subprocess.check_output(
                    'netsh advfirewall show allprofiles',
                    shell=True, text=True
                )
                if "État du pare-feu actuel : ON" in result or "State ON" in result:
                    firewall_status["windows"] = "FIREWALL ON"
                else:
                    firewall_status["windows"] = "FIREWALL OFF"

            elif system == "Linux":
                result = subprocess.run(['which', 'iptables'], stdout=subprocess.PIPE)
                if result.stdout.decode().strip():
                    firewall_status["iptables"] = ""
                else:
                    firewall_status["iptables"] = "Iptables Not installed"

        except Exception as e:
            print(f"ERROR:FATAL {e}")
            firewall_status["error"] = str(e)

        await self.send(json.dumps(firewall_status))







    async def allow_connection(self):
        allowed_processes = getattr(self, "allowed_processes", set())
        print(f"PROCESSUS ALLOWED DE CYBERGORAD : {allowed_processes}")

        seen = set()

        while True:
            unauthorized_processes = []

            for conn in psutil.net_connections(kind='inet'):
                pid = conn.pid
                if pid and pid not in seen:
                    try:
                        proc = psutil.Process(pid)
                        name = proc.name().lower()

                        if name not in allowed_processes:
                            unauthorized_processes.append({
                                "pid": pid,
                                "name": name,
                                "status": "unauthorized"
                            })
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue

                    seen.add(pid)

            if unauthorized_processes:
                data_to_send = {
                    "type": "unauthorized_processes_alert",
                    "processes": unauthorized_processes,
                }

                # Envoi async (attention : self.send doit être une coroutine fonctionnelle)
                await self.send(json.dumps(data_to_send))

                # Log dans fichier (création dossier si besoin)
                try:
                    log_dir = "log"
                    os.makedirs(log_dir, exist_ok=True)
                    log_path = os.path.join(log_dir, "network_alerts.log")

                    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                    with open(log_path, "a", encoding="utf-8") as logfile:
                        logfile.write(f"[{timestamp}] {json.dumps(data_to_send)}\n")

            

                except Exception as e:
                    print(f"[ERROR LOG NETWORKS : {e}")

            await asyncio.sleep(2)




    async def RubberDuckyMonitor(self):
        MAX_KEYS = 15
        TIME_WINDOW = 1
        keystrokes = []
        queue = asyncio.Queue()

        # Récupère la loop principale avant de démarrer le thread
        main_loop = asyncio.get_running_loop()

        def on_press(key):
            current_time = time.time()

            if key == Key.backspace:
                return

            keystrokes.append(current_time)
            keystrokes[:] = [t for t in keystrokes if current_time - t <= TIME_WINDOW]

            if len(keystrokes) >= MAX_KEYS:
                keystrokes.clear()

                # ✅ Appelle put dans la bonne loop via call_soon_threadsafe
                main_loop.call_soon_threadsafe(
                    lambda: queue.put_nowait({
                        "type": "rubber_ducky",
                        "message": "Alert ! BOT DETECTED ...",
                    })
                )

        def start_listener():
            print("[*] RUBBER DUCKY MONITOR ACTIVATED SUCCESSFULLY ")
            with Listener(on_press=on_press) as listener:
                listener.join()

        threading.Thread(target=start_listener, daemon=True).start()

        # Boucle async qui reçoit les alertes
        while True:
            data = await queue.get()

            try:
                log_dir = "log"
                os.makedirs(log_dir, exist_ok=True)
                log_path = os.path.join(log_dir, "rubber_alerts.log")

                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                with open(log_path, "a", encoding="utf-8") as logfile:
                    logfile.write(f"[{timestamp}] {json.dumps(data)}\n")
            except error as e:
                print(f'ERROR RUBBER DUCKY {e}')

            

            await self.send(json.dumps(data))




                    

    async def get_sorted_processes_by_memory(self, threshold_mb=100):
        while True:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'memory_info', 'memory_percent']):
                try:
                    mem_mb = bytes_to_mb(proc.info['memory_info'].rss)
                    processes.append({
                        'pid': proc.info['pid'],
                        'name': proc.info['name'],
                        'memory_mb': mem_mb,
                        'memory_percent': round(proc.info['memory_percent'], 2),
                        'alert': mem_mb > threshold_mb
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue

            # Tri décroissant
            processes.sort(key=lambda p: p['memory_mb'], reverse=True)

            await self.send(json.dumps({
                "type": "all_process",
                "processes": processes,
            }))

            await asyncio.sleep(5)  


    
    async def monitor_system(self):
        while True:
            cpu_usage = psutil.cpu_percent(interval=1)
            ram_usage = psutil.virtual_memory().percent
            uptime_seconds = time.time() - psutil.boot_time()
            uptime_str = str(datetime.timedelta(seconds=int(uptime_seconds)))
            bandwith_usage = await get_bandwidth_usage()

            disk_usage = await get_disk_usage()
            #battery section
            #battery = psutil.sensors_battery()
            #battery_percent = battery.percent()

            await self.send(json.dumps({
                "type": "cpu",
                "ram_usage": ram_usage,
                "cpu_usage": cpu_usage,
                "disk_usage": disk_usage,
                "bandwith_usage": bandwith_usage,
                "uptime": uptime_str,
            }))
            await asyncio.sleep(1)




#authorized_ports = [22, 80, 443, 53, 8000, 2610, 953, 1716, 33293, 5432]
    async def monitor_ports(self):


        reported_ports = set()
        alert_responses = []

        while True:
            open_ports = []
            for conn in psutil.net_connections(kind='inet'):
                if conn.status == psutil.CONN_LISTEN:
                    process_name = psutil.Process(conn.pid).name() if conn.pid else "Inconnu"
                    open_ports.append({"port": conn.laddr.port, "pid": conn.pid, "process": process_name})

            authorized_ports = getattr(self, "allowed_ports", set())

            unauthorized_ports = [
                port for port in open_ports if port["port"] not in authorized_ports
            ]

            total_open_ports = len(open_ports)
            total_unauthorized_ports = len(unauthorized_ports)

            for port in unauthorized_ports:
                if port["port"] not in reported_ports:
                    reported_ports.add(port["port"])


                    alert_text = (
                        f"Alerte : Port non autorisé détecté - "
                        f"Port: {port['port']}, Processus: {port['process']}"
                    )

                    try:
                        log_dir = "log"
                        os.makedirs(log_dir, exist_ok=True)  # Crée le dossier s'il n'existe pas
                        port_log_path = os.path.join(log_dir, "ports_alerts.log")

                        # 🕒 Formatage de l'horodatage
                        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                        # 📂 Écriture append dans le fichier log
                        with open(port_log_path, "a", encoding="utf-8") as logfile:
                            logfile.write(f"[{timestamp}] {alert_text}\n")

                    except Exception as e:
                        print(f"[ERROR] WRITE FILE PORT  : {e}")



                    # Appel async non-bloquant
                    curl_cmd = f"""
                    curl -H "Content-Type: application/json" -X POST -d '{json.dumps({
                        "contents": [{
                            "parts": [{"text": alert_text}]
                        }]
                    })}' https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=AIzaSyDUzu9hIkc6hfh5GGZUjov8V8BMgK6yDgg
                    """
                    alert_response = await run_command_async(curl_cmd)

                    if alert_response:
                        try:
                            response_data = json.loads(alert_response)
                            response_content = (
                                response_data.get("candidates", [{}])[0]
                                .get("content", {})
                                .get("parts", [{}])[0]
                                .get("text", "Aucun contenu trouvé.")
                            )
                            #print(f"Contenu de l'alerte : {response_content}")

                            alert_responses.append({
                                "port": port["port"],
                                "response": response_content
                            })
                        except json.JSONDecodeError:
                            print("Erreur : Réponse JSON invalide reçue.")
                            alert_responses.append({
                                "port": port["port"],
                                "response": "Erreur : Réponse JSON invalide."
                            })

            # Envoi WebSocket async
            await self.send(json.dumps({
                "type": "ports",
                "total_open_ports": total_open_ports,
                "total_unauthorized_ports": total_unauthorized_ports,
                "open_ports": open_ports,
                "alerts": unauthorized_ports,
                "alert_responses": alert_responses,
            }))

            await asyncio.sleep(5)










    async def get_disk_usage(self):
        usage = {}
        for part in psutil.disk_partitions(all=False):
            try:
                mountpoint = part.mountpoint
                percent = psutil.disk_usage(mountpoint).percent
                usage[mountpoint] = percent
            except PermissionError:
                continue

        await self.send(json.dumps({
            "type": "disk",
            "disk_usage": usage,
        }))
        await asyncio.sleep(1)

 
 
 
        


    async def monitor_usb(self):
        context = pyudev.Context()
        monitor = pyudev.Monitor.from_netlink(context)
        monitor.filter_by(subsystem='usb')
        loop = asyncio.get_running_loop()

        print("[*] Surveillance asynchrone des périphériques USB lancée...")

        try:
            while True:
                try:
                    # timeout de 1 seconde pour rendre la boucle réactive à l'annulation
                    device = await asyncio.wait_for(
                        loop.run_in_executor(None, monitor.poll),
                        timeout=1.0
                    )
                    if device:
                        event_data = {
                            "type": "usb",
                            "action": device.action,
                            "timestamp": str(datetime.datetime.now()),
                            "model": device.get("ID_MODEL", "Inconnu"),
                            "vendor": device.get("ID_VENDOR", "Inconnu"),
                            "serial": device.get("ID_SERIAL_SHORT", "N/A"),
                            "devpath": device.device_path,
                            "node": device.device_node
                        }

                        try:
                            log_dir = "log"
                            os.makedirs(log_dir, exist_ok=True)  # Crée le dossier s'il n'existe pas
                            port_log_path = os.path.join(log_dir, "usb_alerts.log")

                            # 🕒 Formatage de l'horodatage
                            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                            # 📂 Écriture append dans le fichier log
                            with open(port_log_path, "a", encoding="utf-8") as logfile:
                                logfile.write(f"[{timestamp}] {event_data}\n")

                        except Exception as e:
                            print(f"[ERROR] WRITE FILE USB  : {e}")


                        await self.send(json.dumps(event_data))
                except asyncio.TimeoutError:
                    # Pas d'événement : boucle continue, permet cancel propre
                    continue
        except asyncio.CancelledError:
            print("[*] Arrêt propre de la surveillance USB.")
            raise

            
        

    async def monitor_connections(self):

        while True:
            connections = get_established_connections()
            await self.send(json.dumps({
                "machine_id": get_machine_id(), 
                "type": "connections",
                "connections": connections,
            }))
            await asyncio.sleep(5)





    async def monitor_bandwidth(self):
        """Surveille la bande passante réseau."""
        old_data = psutil.net_io_counters()

        total_sent_bytes = 0
        total_recv_bytes = 0

        while True:
            await asyncio.sleep(1)  # Intervalle de surveillance
            new_data = psutil.net_io_counters()

            sent_bytes = new_data.bytes_sent - old_data.bytes_sent
            recv_bytes = new_data.bytes_recv - old_data.bytes_recv
            total_bytes = sent_bytes + recv_bytes

            old_data = new_data

            total_sent_bytes += sent_bytes
            total_recv_bytes += recv_bytes
            total_data_bytes = total_sent_bytes + total_recv_bytes

            sent_kb = sent_bytes / 1024.0
            recv_kb = recv_bytes / 1024.0
            total_kb = total_bytes / 1024.0
            total_data_mb = total_data_bytes / (1024.0 * 1024.0)

            await self.send(json.dumps({
                "type": "bandwidth",
                "sent": round(sent_kb, 2),
                "received": round(recv_kb, 2),
                "total": round(total_kb, 2),
                "total_data_mb": round(total_data_mb, 2)
            }))





    async def monitor_cron_jobs(self):
        """Surveille les cron jobs sous Linux ou les tâches planifiées sous Windows."""

        if platform.system().lower() == "linux":
            cron_dir = "/var/spool/cron/crontabs"
            if not os.path.exists(cron_dir):
                return  # Si le dossier n'existe pas, on skip

            last_mod_times = {}
            for user_cron in os.listdir(cron_dir):
                path = os.path.join(cron_dir, user_cron)
                if os.path.isfile(path):
                    last_mod_times[user_cron] = os.path.getmtime(path)

            while True:
                await asyncio.sleep(5)
                for user_cron in os.listdir(cron_dir):
                    path = os.path.join(cron_dir, user_cron)
                    if not os.path.isfile(path):
                        continue

                    current_mtime = os.path.getmtime(path)
                    if user_cron not in last_mod_times or current_mtime != last_mod_times[user_cron]:
                        last_mod_times[user_cron] = current_mtime
                        cron_content = run_command(f"crontab -l -u {user_cron}")
                        if cron_content:


                            alert_message = {
                                "type": "cron_modification",
                                "os": "linux",
                                "user": user_cron,
                                "message": f"Modification detected in cron jobs for user '{user_cron}'",
                                "details": cron_content.strip()
                            }
                            try:
                                log_dir = "log"
                                os.makedirs(log_dir, exist_ok=True)
                                cron_log_path = os.path.join(log_dir, "cron_alerts.log")

                                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                                with open(cron_log_path, "a", encoding="utf-8") as logfile:
                                    logfile.write(f"[{timestamp}] {json.dumps(alert_message)}\n")
                            except error as e:
                                print(f'ERROR CRON LOG {e}')


                            
                            await self.send(json.dumps(alert_message))



        elif platform.system().lower() == "windows":
            previous_output = ""
            while True:
                await asyncio.sleep(5)
                current_output = run_command("schtasks /Query /FO LIST /V")
                if current_output and current_output.strip() != previous_output.strip():
                    previous_output = current_output
                    alert_message = {
                        "type": "scheduled_task_modification",
                        "os": "windows",
                        "message": "Modification detected in scheduled tasks",
                        "details": current_output.strip()
                    }
                    await self.send(json.dumps(alert_message))




    async def monitor_startup_info(self):
        """Surveille et envoie les apps/services de démarrage selon l'OS détecté."""
        os_type = platform.system()

        if os_type == "Linux":
            startup_info = get_linux_startup_info()
        elif os_type == "Windows":
            startup_info = get_windows_startup_info()
        else:
            startup_info = {"error": f"Système d'exploitation {os_type} non pris en charge"}

        # Envoie les données via WebSocket
        await self.send(json.dumps({
            "type": "startup_info",
            "os": os_type,
            "data": startup_info
        }))

        # Pause (tu peux mettre ça dans une boucle si tu veux des checks récurrents)
        await asyncio.sleep(5)







    async def monitor_logs(self):
        log_file_path = '/var/log/log_system' 
        try:
            with open(log_file_path, 'r') as log_file:
                log_file.seek(0, 2) 

                while True:
                    line = log_file.readline()
                    if line:
                 
                        await self.send(text_data=json.dumps({
                            'type': 'log',
                            'message': line.strip()
                        }))
                    else:
                        await asyncio.sleep(3)  #intervalle

        except Exception as e:
            print(f"Erreur de lecture du fichier de log: {e}")










    async def monitor_outbound_traffic(self):
        while True:
            connections = []
            for conn in psutil.net_connections(kind='inet'):
                if conn.raddr:
                    try:
                        pid = conn.pid
                        process = psutil.Process(pid) if pid else None

                        if process:
                            name = process.name()
                            uptime_sec = int(time.time() - process.create_time())
                            uptime = format_duration(uptime_sec)
                        else:
                            name = "Unknown"
                            uptime = "0h 0min 0s"

                        proto = {
                            socket.SOCK_STREAM: "TCP",
                            socket.SOCK_DGRAM: "UDP"
                        }.get(conn.type, "Unknown")

                        net_io = psutil.net_io_counters(pernic=False)
                        sent = net_io.bytes_sent
                        recv = net_io.bytes_recv

                        connections.append({
                            'local_address': f"{conn.laddr.ip}:{conn.laddr.port}",
                            'remote_address': f"{conn.raddr.ip}:{conn.raddr.port}",
                            'remote_port': conn.raddr.port,
                            'process': name,
                            'protocol': proto,
                            'packets_sent': sent,
                            'packets_received': recv,
                            'uptime': uptime  # maintenant lisible
                        })
                    except (psutil.NoSuchProcess, psutil.AccessDenied, AttributeError):
                        pass

            await self.send(json.dumps({
                "type": "outbound_traffic",
                "connections": connections,
            }))
            await asyncio.sleep(5)


                


