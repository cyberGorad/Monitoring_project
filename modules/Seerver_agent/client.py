import asyncio
import websockets
import platform
import psutil
import subprocess

async def send_cpu_info():
    uri = "ws://localhost:8765"
    
    try:
        async with websockets.connect(
            uri,
            ping_interval=20,
            ping_timeout=20,
            close_timeout=10
        ) as websocket:

            resultat = subprocess.run("ifconfig", shell= True, capture_output= True )
            system_info = f"cpu: {resultat}"
            await websocket.send(system_info)
            print(f"Envoyé: {system_info}")

            while True:
                try:
                    message = await websocket.recv()
                    print(f"Reçu du serveur: {message}")
                except websockets.exceptions.ConnectionClosed:
                    print("Connexion fermée proprement par le serveur")
                    break
                    
    except Exception as e:
        print(f"Erreur de connexion: {str(e)}")

async def main():
    await send_cpu_info()

if __name__ == "__main__":
    asyncio.run(main())
