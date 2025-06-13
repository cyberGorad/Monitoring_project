
import os
import sqlite3
import platform
import datetime
import shutil # Nécessaire pour copier le fichier de base de données
import asyncio # Nécessaire pour asyncio.to_thread
import json # Pour l'intégration dans le payload JSON si vous l'ajoutez à votre agent

# --- Fonction pour récupérer l'historique du navigateur (avec Edge, Chrome, Firefox) ---
async def get_browser_history():
    """
    Récupère l'historique de navigation de Chrome, Edge et Firefox.
    Gère les différents chemins d'OS et le verrouillage de la base de données en copiant le fichier DB.
    Retourne une liste de dictionnaires contenant les URLs visitées.
    """
    history_entries = []
    
    # Définir les chemins pour les navigateurs courants sur différents OS
    browser_paths = {
        "Windows": {
            "Chrome": os.path.join(os.environ.get('LOCALAPPDATA', ''), r"Google\Chrome\User Data\Default\History"),
            "Edge": os.path.join(os.environ.get('LOCALAPPDATA', ''), r"Microsoft\Edge\User Data\Default\History"),
            "Firefox_Root": os.path.join(os.environ.get('APPDATA', ''), r"Mozilla\Firefox\Profiles"),
        },
        "Linux": {
            "Chrome": os.path.expanduser("~/.config/google-chrome/Default/History"),
            "Firefox_Root": os.path.expanduser("~/.mozilla/firefox"),
        }
        # Ajoutez les chemins macOS si nécessaire (ex: Chrome: ~/Library/Application Support/Google/Chrome/Default/History)
    }

    os_type = platform.system()
    
    # Choisir les chemins corrects en fonction de l'OS
    current_os_paths = browser_paths.get(os_type)
    if not current_os_paths:
        print(f"La récupération de l'historique du navigateur n'est pas prise en charge sur {os_type}")
        return {"error": f"La récupération de l'historique du navigateur n'est pas prise en charge sur {os_type}"}

    print(f"--- Tentative de récupération de l'historique du navigateur sur {os_type} ---")

    for browser_name, db_path_template in current_os_paths.items():
        if browser_name.endswith("_Root"): # Gestion spéciale pour les navigateurs qui utilisent des dossiers de profil
            if browser_name == "Firefox_Root":
                try:
                    firefox_profiles_root = db_path_template
                    if await asyncio.to_thread(os.path.exists, firefox_profiles_root):
                        # Chercher les dossiers de profil (ex: xxxxxx.default-release)
                        # os.listdir peut être bloquant, donc l'exécuter dans un thread
                        for profile_dir in await asyncio.to_thread(os.listdir, firefox_profiles_root):
                            # Prioriser default-release ou default, mais vérifier n'importe quel si besoin
                            if "default" in profile_dir.lower() and await asyncio.to_thread(os.path.isdir, os.path.join(firefox_profiles_root, profile_dir)):
                                firefox_db_path = os.path.join(firefox_profiles_root, profile_dir, "places.sqlite")
                                if await asyncio.to_thread(os.path.exists, firefox_db_path):
                                    print(f"Base de données de profil Firefox trouvée : {firefox_db_path}")
                                    await _read_history_from_sqlite(firefox_db_path, "Firefox", history_entries)
                                else:
                                    print(f"places.sqlite de Firefox non trouvé dans {profile_dir}")
                    else:
                        print(f"Racine des profils Firefox non trouvée : {firefox_profiles_root}")
                except Exception as e:
                    print(f"Erreur lors de la lecture des profils Firefox : {e}")
            continue # Passer au navigateur suivant après avoir tenté les navigateurs basés sur la racine

        # Pour Chrome et Edge, utiliser directement le chemin
        # os.path.exists peut être bloquant, donc l'exécuter dans un thread
        if await asyncio.to_thread(os.path.exists, db_path_template):
            print(f"Base de données d'historique {browser_name} trouvée : {db_path_template}")
            await _read_history_from_sqlite(db_path_template, browser_name, history_entries)
        else:
            print(f"Base de données d'historique {browser_name} non trouvée à : {db_path_template}")

    return {"browser_history": history_entries}

async def _read_history_from_sqlite(db_path, browser_name, history_entries_list):
    """
    Fonction d'aide interne pour lire l'historique à partir d'un fichier de base de données SQLite.
    Copie le fichier pour éviter les problèmes de verrouillage.
    Toutes les opérations SQLite sont maintenant encapsulées dans asyncio.to_thread.
    """
    temp_db_path = db_path + ".temp_copy"
    
    try:
        # Vérifier l'existence et copier dans un thread
        if await asyncio.to_thread(os.path.exists, db_path):
            print(f"Copie de la base de données d'historique {browser_name} vers {temp_db_path}...")
            await asyncio.to_thread(lambda: shutil.copy2(db_path, temp_db_path))

            # Fonction pour encapsuler toutes les opérations de base de données dans un thread
            def db_operations():
                _conn = None
                rows_data = []
                try:
                    _conn = sqlite3.connect(temp_db_path)
                    _cursor = _conn.cursor()

                    # Définir la requête en fonction du navigateur
                    # Suppression de la clause LIMIT pour récupérer toutes les entrées
                    if browser_name in ["Chrome", "Edge"]: # Chrome et Edge utilisent le même schéma d'historique (Chromium)
                        query = "SELECT url, title, last_visit_time FROM urls ORDER BY last_visit_time DESC"
                    elif browser_name == "Firefox":
                        query = "SELECT url, title, last_visit_date FROM moz_places ORDER BY last_visit_date DESC"
                    else:
                        print(f"Navigateur non pris en charge pour l'analyse SQLite : {browser_name}")
                        return [] # Retourner une liste vide si non pris en charge

                    _cursor.execute(query)
                    rows_data = _cursor.fetchall()
                    return rows_data
                finally:
                    if _conn:
                        _conn.close() # Fermer la connexion dans le même thread où elle a été ouverte

            rows = await asyncio.to_thread(db_operations) # Exécuter toutes les opérations DB dans un thread

            for row in rows:
                url = row[0]
                title = row[1]
                timestamp_val = row[2]

                last_visit_time = "Unknown"
                try:
                    if browser_name in ["Chrome", "Edge"]:
                        # Chrome/Edge utilise des microsecondes depuis le 1er janvier 1601 UTC
                        # (11644473600000000 est la différence en microsecondes entre 1601-01-01 et 1970-01-01)
                        last_visit_time = datetime.datetime(1601, 1, 1) + datetime.timedelta(microseconds=timestamp_val)
                    elif browser_name == "Firefox":
                        # Firefox utilise des microsecondes depuis l'époque Unix (1er janvier 1970 UTC)
                        last_visit_time = datetime.datetime.fromtimestamp(timestamp_val / 1_000_000)
                except (ValueError, TypeError) as e:
                    print(f"Erreur de conversion de l'horodatage pour {browser_name} ({url}) : {e}")
                    last_visit_time = "Horodatage Invalide"

                history_entries_list.append({
                    "browser": browser_name,
                    "url": url,
                    "title": title,
                    "last_visit": str(last_visit_time)
                })
        else:
            print(f"Fichier de base de données non trouvé : {db_path}")

    except sqlite3.OperationalError as e:
        print(f"[{browser_name}] Base de données verrouillée ou corrompue : {e}")
        history_entries_list.append({"error": f"[{browser_name}] Base de données verrouillée ou corrompue. Veuillez vous assurer que le navigateur est fermé ou réessayez."})
    except Exception as e:
        print(f"[{browser_name}] Une erreur inattendue s'est produite : {e}")
        history_entries_list.append({"error": f"[{browser_name}] Échec de la lecture de l'historique : {e}"})
    finally:
        # Assurez-vous que le fichier temporaire est supprimé, également dans un thread
        if await asyncio.to_thread(os.path.exists, temp_db_path):
            try:
                await asyncio.to_thread(os.remove, temp_db_path)
                print(f"Fichier temporaire nettoyé : {temp_db_path}")
            except PermissionError as e:
                print(f"ATTENTION: Impossible de supprimer le fichier temporaire {temp_db_path}. Il est peut-être encore utilisé: {e}")


async def main_test_history():
    """Fonction principale pour exécuter le test de récupération de l'historique."""
    print("Démarrage du test de l'historique du navigateur...")
    history_data = await get_browser_history()
    
    if "browser_history" in history_data:
        if history_data["browser_history"]:
            for entry in history_data["browser_history"]:
                print(f"Navigateur: {entry.get('browser', 'N/A')}")
                print(f"  URL: {entry.get('url', 'N/A')}")
                print(f"  Titre: {entry.get('title', 'N/A')}")
                print(f"  Dernière visite: {entry.get('last_visit', 'N/A')}\n")
        else:
            print("Aucune entrée d'historique de navigateur trouvée (ou erreurs rencontrées pour tous les navigateurs).")
    elif "error" in history_data:
        print(f"Erreur globale : {history_data['error']}")
    
    print("Test de l'historique du navigateur terminé.")

if __name__ == "__main__":
    asyncio.run(main_test_history())
