import os
import sys
import time
import platform
import asyncio
import json
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Exclusion des dossiers système sensibles sous Linux
EXCLUDED_DIRS = ["/proc", "/sys", "/dev", "/run", "/var/lib", "/tmp"]

class FileMonitorHandler(FileSystemEventHandler):
    """ Gère les événements de modification de fichiers """

    def on_modified(self, event):
        if not event.is_directory:
            print(f"📝 Fichier modifié : {event.src_path}")

    def on_created(self, event):
        if not event.is_directory:
            print(f"📂 Fichier créé : {event.src_path}")

    def on_deleted(self, event):
        if not event.is_directory:
            print(f"🗑️ Fichier supprimé : {event.src_path}")

class FileMonitor:
    """ Surveille les fichiers en temps réel """

    def __init__(self):
        self.observer = Observer()
        self.system_os = platform.system()

    def run(self):
        event_handler = FileMonitorHandler()

        if self.system_os == "Linux":
            root_dirs = ["/"]  # Surveiller tout le système
            for root_dir in root_dirs:
                if root_dir not in EXCLUDED_DIRS:
                    self.observer.schedule(event_handler, root_dir, recursive=True)

        elif self.system_os == "Windows":
            root_dir = "C:\\"  # Surveiller tout le disque C:
            self.observer.schedule(event_handler, root_dir, recursive=True)

        self.observer.start()
        print("🔍 Surveillance en temps réel activée...")

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.observer.stop()
            print("🛑 Surveillance arrêtée.")
        self.observer.join()

if __name__ == "__main__":
    monitor = FileMonitor()
    monitor.run()
