import psutil
import time

# Liste blanche des noms de processus autorisés
allowed_processes = {"firefox", "chrome", "curl"}

def check_connections():
    seen = set()
    while True:
        for conn in psutil.net_connections(kind='inet'):
            pid = conn.pid
            if pid and pid not in seen:
                try:
                    proc = psutil.Process(pid)
                    name = proc.name().lower()
                    if name not in allowed_processes:
                        print(f"⚠️ ALERTE: Processus non autorisé a tenté une connexion -> {name} (PID: {pid})")
                        # Optionnel: kill ou log
                        # proc.kill()
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
                seen.add(pid)
        time.sleep(2)

check_connections()
