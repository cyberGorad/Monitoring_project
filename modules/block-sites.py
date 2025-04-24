import os
import platform

# Liste de sites adultes à bloquer (exemples)
blocked_sites = [
    "tsilavina.alwaysdata.net",  # Remplacez par les domaines réels à bloquer
    "another-adultsite.com",
    "adult-site.com"
]

# Fonction pour obtenir le chemin du fichier hosts
def get_hosts_file_path():
    system_os = platform.system()
    if system_os == "Windows":
        return r"C:\Windows\System32\drivers\etc\hosts"
    elif system_os == "Linux":
        return "/etc/hosts"
    else:
        raise Exception("Système non supporté.")

# Fonction pour bloquer les sites
def block_sites():
    hosts_file_path = get_hosts_file_path()
    
    # Si le fichier hosts existe, continuez
    if os.path.exists(hosts_file_path):
        with open(hosts_file_path, "a") as file:
            for site in blocked_sites:
                # Rediriger les sites vers localhost
                file.write(f"127.0.0.1 {site}\n")
            print(f"Sites bloqués : {', '.join(blocked_sites)}")
    else:
        print(f"Le fichier {hosts_file_path} n'existe pas.")

# Fonction pour vérifier les sites bloqués
def check_blocked_sites():
    hosts_file_path = get_hosts_file_path()
    if os.path.exists(hosts_file_path):
        with open(hosts_file_path, "r") as file:
            content = file.read()
            for site in blocked_sites:
                if site in content:
                    print(f"{site} est bloqué.")
                else:
                    print(f"{site} n'est pas bloqué.")
    else:
        print(f"Le fichier {hosts_file_path} n'existe pas.")

# Exemple d'utilisation
block_sites()
check_blocked_sites()
