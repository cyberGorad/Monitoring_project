import asyncio
import websockets
import json

# Adresse du serveur WebSocket
SERVER_HOST = "0.0.0.0"
SERVER_PORT = 8000

# Fonction pour gérer les connexions WebSocket
async def handle_client(websocket, path):
    print("Un client s'est connecté")
    try:
        async for message in websocket:
            data = json.loads(message)
            print("Données reçues de l'agent :")
            print(json.dumps(data, indent=4))
            # Ici, vous pouvez traiter les données, les enregistrer ou effectuer toute autre action
    except websockets.exceptions.ConnectionClosedError as e:
        print(f"Erreur de connexion: {e}")
    finally:
        print("Client déconnecté")

# Fonction pour démarrer le serveur WebSocket
async def start_server():
    server = await websockets.serve(handle_client, SERVER_HOST, SERVER_PORT)
    print(f"Serveur WebSocket démarré sur ws://{SERVER_HOST}:{SERVER_PORT}")
    await server.wait_closed()

# Démarrer le serveur
if __name__ == "__main__":
    asyncio.run(start_server())
