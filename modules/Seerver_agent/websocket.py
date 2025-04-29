import asyncio
import websockets
from datetime import datetime

connected_clients = {}

async def handler(websocket):
    """Gestionnaire de connexion simplifié"""
    client_ip = websocket.remote_address[0]
    print(f"Nouvelle connexion depuis {client_ip}")

    connected_clients[websocket] = client_ip
    await broadcast_clients_list()

    try:
        async for message in websocket:
            print(f"Reçu de {client_ip}: {message}")
            
            timestamp = datetime.now().strftime("%H:%M:%S")
            response = f"[{timestamp}] Serveur a reçu: {message}"
            await websocket.send(response)
            
    except websockets.exceptions.ConnectionClosed:
        print(f"Connexion fermée avec {client_ip}")
    finally:
        if websocket in connected_clients:
            del connected_clients[websocket]
            await broadcast_clients_list()

async def broadcast_clients_list():
    if not connected_clients:
        return
        
    clients_list = "Clients connectés:\n" + "\n".join(
        f"- {ip}" for ip in connected_clients.values()
    )
    
    # Créer une liste des tâches d'envoi seulement pour les clients actifs
    tasks = []
    for client in list(connected_clients.keys()):  # Utiliser une copie de la liste
        try:
            if client.open:  # Utiliser 'open' au lieu de 'closed'
                tasks.append(client.send(clients_list))
        except:
            # Si erreur, supprimer le client
            if client in connected_clients:
                del connected_clients[client]
    
    if tasks:
        await asyncio.gather(*tasks, return_exceptions=True)

async def main():
    async with websockets.serve(
        handler,
        "0.0.0.0",
        8000,
        ping_interval=20,
        ping_timeout=20,
        close_timeout=10
    ):
        print("Serveur WebSocket démarré sur ws://localhost:8000")
        await asyncio.Future()  # Lancer le serveur indéfiniment

if __name__ == "__main__":
    asyncio.run(main())
