import requests

# L'URL de l'API PHP qui retourne l'adresse du serveur WebSocket
API_URL = "https://tsilavina.alwaysdata.net/urls.php"  # Adapte ce chemin selon ton setup

try:
    # Requête GET vers le PHP
    response = requests.get(API_URL)
    data = response.json()

    # Récupère l'URL WebSocket
    SERVER_URL = data["url"].replace("http://", "ws://")  # si le serveur renvoie http
    print(f"{SERVER_URL}")

except Exception as e:
    print(f"[!] Erreur : {e}")
