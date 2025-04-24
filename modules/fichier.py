import os
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Liste des répertoires à ignorer
IGNORED_DIRS = ['/proc', '/sys', '/dev', '/run', '/tmp', '/var/run', '/var/lock']

class FileChangeHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.is_directory:
            return
        print(f"📂 Modifié : {event.src_path}")

    def on_created(self, event):
        if event.is_directory:
            return
        print(f"🆕 Créé : {event.src_path}")

    def on_deleted(self, event):
        if event.is_directory:
            return
        print(f"❌ Supprimé : {event.src_path}")

    def on_moved(self, event):
        if event.is_directory:
            return
        print(f"➡️ Déplacé : {event.src_path} vers {event.dest_path}")

def monitor_file_changes(root_dir="/"):
    # Vérifier si le répertoire existe
    if not os.path.exists(root_dir):
        print(f"Erreur: Le répertoire {root_dir} n'existe pas.")
        return
    
    # Observer la modification des fichiers dans tous les répertoires
    event_handler = FileChangeHandler()
    observer = Observer()

    # Exclure les répertoires à ignorer
    for ignored_dir in IGNORED_DIRS:
        if root_dir.startswith(ignored_dir):
            print(f"⚠️ Le répertoire {ignored_dir} est ignoré.")
            return

    try:
        # Ajouter un contrôle pour vérifier l'existence de chaque répertoire avant de l'ajouter à l'observateur
        for dirpath, dirnames, filenames in os.walk(root_dir, topdown=True):
            for dirname in dirnames:
                full_path = os.path.join(dirpath, dirname)
                if not os.path.exists(full_path):
                    print(f"⚠️ Le répertoire {full_path} n'existe pas.")
                    continue
                # Ajouter le répertoire à l'observateur
                observer.schedule(event_handler, full_path, recursive=False)

        # Démarrer l'observateur et vérifier s'il a démarré correctement
        observer.start()
        print(f"🔍 Surveillance des fichiers dans {root_dir} en cours...")

        # Garder le script en fonctionnement
        while True:
            time.sleep(1)

    except OSError as e:
        print(f"⚠️ Erreur de système de fichiers : {str(e)}")
    except KeyboardInterrupt:
        print("🔴 Surveillance arrêtée par l'utilisateur.")
    finally:
        # S'assurer que l'observateur s'arrête proprement
        if observer.is_alive():
            observer.stop()
            observer.join()

# Lancer la surveillance de l'intégralité du système
monitor_file_changes("/")
