import time
import os
import platform
import json
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class FileMonitorHandler(FileSystemEventHandler):
    """Gère les événements de surveillance des fichiers."""
    
    def on_modified(self, event):
        if event.is_directory:
            return  # Ignorer les dossiers

        print(json.dumps({
            "type": "file_modification",
            "message": f"Le fichier '{event.src_path}' a été modifié.",
            "file_path": event.src_path,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }, indent=4))

    def on_created(self, event):
        if event.is_directory:
            return  

        print(json.dumps({
            "type": "file_creation",
            "message": f"Le fichier '{event.src_path}' a été créé.",
            "file_path": event.src_path,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }, indent=4))

    def on_deleted(self, event):
        if event.is_directory:
            return  

        print(json.dumps({
            "type": "file_deletion",
            "message": f"Le fichier '{event.src_path}' a été supprimé.",
            "file_path": event.src_path,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }, indent=4))

    def on_moved(self, event):
        if event.is_directory:
            return  

        print(json.dumps({
            "type": "file_move",
            "message": f"Le fichier '{event.src_path}' a été déplacé vers '{event.dest_path}'.",
            "src_path": event.src_path,
            "dest_path": event.dest_path,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }, indent=4))

class FileMonitor:
    """Lance le moniteur de fichiers compatible Linux & Windows."""
    
    def __init__(self, folder_to_watch):
        self.folder_to_watch = folder_to_watch
        self.observer = Observer()

    def run(self):
        """Démarre la surveillance."""
        event_handler = FileMonitorHandler()
        self.observer.schedule(event_handler, self.folder_to_watch, recursive=True)
        self.observer.start()
        print(f"🔍 Surveillance en temps réel des fichiers dans : {self.folder_to_watch}")

        try:
            while True:
                time.sleep(5)
        except KeyboardInterrupt:
            self.observer.stop()
            print("❌ Arrêt de la surveillance.")
        self.observer.join()

if __name__ == "__main__":
    system_os = platform.system()

    # 📂 Dossier à surveiller (ajuste selon ton OS)
    if system_os == "Windows":
        folder_to_watch = "C:\\Users\\Public"  # Chemin Windows
    else:
        folder_to_watch =   input("Entrer folder to watch? ->")

    monitor = FileMonitor(folder_to_watch)
    monitor.run()
