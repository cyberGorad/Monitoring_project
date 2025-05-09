import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class MyHandler(FileSystemEventHandler):
    def on_modified(self, event):
        print(f"Modification détectée : {event.src_path}")
    
    def on_created(self, event):
        print(f"Fichier créé : {event.src_path}")
    
    def on_deleted(self, event):
        print(f"Fichier supprimé : {event.src_path}")

if __name__ == "__main__":
    path = "/"  # Remplace par le chemin de ton répertoire
    event_handler = MyHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    
    observer.join()

