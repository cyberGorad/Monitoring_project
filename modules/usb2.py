import pyudev
import datetime
import json
import asyncio

# Fonction principale pour surveiller les événements USB et envoyer les données
async def monitor_usb():
    context = pyudev.Context()
    monitor = pyudev.Monitor.from_netlink(context)
    monitor.filter_by(subsystem='usb')
    loop = asyncio.get_running_loop()

    print("[*] Surveillance asynchrone des périphériques USB lancée...")

    while True:
        # Récupération de l'événement USB
        device = await loop.run_in_executor(None, monitor.poll)
        if device:
            # Création des données à envoyer
            event_data = {
                "type": "usb",
                "action": device.action,
                "timestamp": str(datetime.datetime.now()),
                "model": device.get("ID_MODEL", "Inconnu"),
                "vendor": device.get("ID_VENDOR", "Inconnu"),
                "serial": device.get("ID_SERIAL_SHORT", "N/A"),
                "devpath": device.device_path,
                "node": device.device_node
            }

            # Affichage des données dans la console
            print(json.dumps(event_data, indent=4))  # Pour afficher joliment les données

            # Si tu veux envoyer les données via un autre moyen, tu peux appeler une fonction ici
            # Exemple :
            # await send_data(event_data)  # Remplace par ta propre fonction d'envoi

# Lancer la surveillance
if __name__ == '__main__':
    asyncio.run(monitor_usb())
