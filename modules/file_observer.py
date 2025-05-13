from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time

class SurveillanceHandler(FileSystemEventHandler):
    def on_created(self, event):
        print(f"[+] Fichier créé : {event.src_path}")

    def on_deleted(self, event):
        print(f"[-] Fichier supprimé : {event.src_path}")

    def on_modified(self, event):
        print(f"[~] Fichier modifié : {event.src_path}")

    def on_moved(self, event):
        print(f"[>] Fichier déplacé : de {event.src_path} vers {event.dest_path}")

if __name__ == "__main__":
    path = "/home/"  # Dossier à surveiller (à adapter)
    observer = Observer()
    observer.schedule(SurveillanceHandler(), path=path, recursive=True)

    print(f"[🎯] Surveillance activée sur : {path}")
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
