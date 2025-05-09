from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time
import os

class FileHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return
        print(f"File created: {event.src_path}")

# Utilisation de la racine du système pour surveiller tout le système
path = "/"  # Cela couvre l'intégralité du système de fichiers

# Exclusion des répertoires sensibles comme /proc, /sys, /dev
def exclude_paths(path):
    return any(path.startswith(exclude) for exclude in ['/proc', '/sys', '/dev', '/run'])

event_handler = FileHandler()
observer = Observer()

# Surveillance récursive avec exclusions
def start_watching():
    for root, dirs, files in os.walk(path):
        # Filtrer les répertoires à ne pas surveiller
        dirs[:] = [d for d in dirs if not exclude_paths(os.path.join(root, d))]
        for file in files:
            observer.schedule(event_handler, os.path.join(root, file), recursive=False)

    observer.start()
    print(f"Starting to watch the entire filesystem.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()

start_watching()
