# generator.py

def generate_full_agent():
    print("🔧 Générateur de script Python (agent WebSocket)")
    ip = input("💬 IP serveur WebSocket (ex: 192.168.10.232): ").strip()
    port = input("💬 Port WebSocket (ex: 9000): ").strip()

    url = f"ws://{ip}:{port}"
    output_filename = "agent.py"

    agent_code = f'''\
import asyncio
import websockets

SERVER_URL = "{url}"

async def connect():
    try:
        async with websockets.connect(SERVER_URL) as ws:
            print(f"🔌 Connecté à {{SERVER_URL}}")
            await ws.send("Hello from agent!")
            while True:
                message = await ws.recv()
                print(f"📩 Message reçu : {{message}}")
    except Exception as e:
        print(f"❌ Erreur de connexion WebSocket : {{e}}")

if __name__ == "__main__":
    asyncio.run(connect())
'''

    with open(output_filename, "w") as f:
        f.write(agent_code)

    print(f"\n✅ Agent généré avec succès : {output_filename}")
    print(f'📡 Connecte-toi à : "{url}"')


if __name__ == "__main__":
    generate_full_agent()
