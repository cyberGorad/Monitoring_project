import websocket
import json

# Fonction pour envoyer des messages au serveur
def on_open(ws):
    print("Connexion au serveur WebSocket établie")
    # Exemple de message simple que l'agent va envoyer au serveur
    message = "Message de l'agent: Hello Cybergorad"
    ws.send(message)

# Fonction pour recevoir les messages du serveur
def on_message(ws, message):
    print(f"Message reçu du serveur: {message}")

# Fonction pour gérer les erreurs
def on_error(ws, error):
    print(f"Erreur WebSocket: {error}")

# Fonction pour gérer la fermeture de la connexion
def on_close(ws, close_status_code, close_msg):
    print("Connexion fermée avec le serveur")

# URL du serveur WebSocket
server_url = "ws://localhost:9000"

# Créer la connexion WebSocket et définir les callbacks
ws = websocket.websockets(server_url,
                            on_open=on_open,
                            on_message=on_message,
                            on_error=on_error,
                            on_close=on_close)

# Lancer la boucle d'écoute des messages
ws.run_forever()
