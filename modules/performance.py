import psutil
import time

def monitor_system_performance():
    while True:
        # Surveillance de l'utilisation du CPU
        cpu_usage = psutil.cpu_percent(interval=1)  # Calcul de l'utilisation du CPU pendant 1 seconde
        print(f"Utilisation du CPU: {cpu_usage}%")

        # Surveillance de l'utilisation de la mémoire
        memory = psutil.virtual_memory()
        print(f"Utilisation de la mémoire: {memory.percent}% ({memory.used / (1024 ** 3):.2f} GB sur {memory.total / (1024 ** 3):.2f} GB)")

        # Surveillance de l'utilisation du disque
        disk_usage = psutil.disk_usage('/')
        print(f"Utilisation du disque: {disk_usage.percent}% ({disk_usage.used / (1024 ** 3):.2f} GB sur {disk_usage.total / (1024 ** 3):.2f} GB)")

        # Surveillance de l'activité réseau
        net_io = psutil.net_io_counters()
        print(f"Reçus: {net_io.bytes_recv / (1024 ** 2):.2f} MB, Envoyés: {net_io.bytes_sent / (1024 ** 2):.2f} MB")

        print("-" * 50)
        
        time.sleep(5)  # Attendre 5 secondes avant de recommencer

if __name__ == "__main__":
    monitor_system_performance()
