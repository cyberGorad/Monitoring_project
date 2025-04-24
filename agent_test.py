import websockets
import asyncio

async def send_data():
    uri = "ws://localhost:9000"

    # Connexion au serveur WebSocket
    async with websockets.connect(uri) as websocket:
        while True:
            # Exemple de message simple
            message = "Hello Cybergorad"

            # Envoi du message
            await websocket.send(message)
            print(f"Message envoyé: {message}")

            # Attendre 5 secondes avant le prochain envoi
            await asyncio.sleep(5)

# Lancer la fonction en boucle
async def main():
    while True:
        await send_data()

# Démarrer la boucle principale
asyncio.run(main())
