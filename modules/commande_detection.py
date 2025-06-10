import psutil
import time
import os

def detect_commands_auto():
    print("🚨 Surveillance des commandes lancées (mode automatique)")
    seen = set()

    while True:
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                pid = proc.info['pid']
                cmdline = proc.info['cmdline']
                name = proc.info['name']

                # Filtrer les processus déjà vus ou sans commande claire
                if pid not in seen and cmdline and len(cmdline) > 1:
                    full_cmd = ' '.join(cmdline)
                    print(f"\n[🧠 COMMANDE DÉTECTÉE] PID={pid} | NAME={name}")
                    print(f"📜 ➤ {full_cmd}")

                    # Log dans un fichier
                    with open("log/command_exec.log", "a", encoding="utf-8") as f:
                        f.write(f"[{time.ctime()}] {name} ({pid}): {full_cmd}\n")

                    seen.add(pid)

            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        time.sleep(1)

if __name__ == "__main__":
    os.makedirs("log", exist_ok=True)
    detect_commands_auto()
