import pyudev
import datetime
import time

def device_event(device):
    if device.action == 'add':
        print(f"\n[USB INSÉRÉ] - {datetime.datetime.now()}")
        print(f"  - Modèle : {device.get('ID_MODEL', 'Inconnu')}")
        print(f"  - Vendor : {device.get('ID_VENDOR', 'Inconnu')}")
        print(f"  - Numéro de série : {device.get('ID_SERIAL_SHORT', 'N/A')}")
        print(f"  - DevPath : {device.device_path}")
        print(f"  - Node : {device.device_node}")
    elif device.action == 'remove':
        print(f"\n[USB RETIRÉ] - {datetime.datetime.now()}")
        print(f"  - DevPath : {device.device_path}")

def start_monitor():
    context = pyudev.Context()
    monitor = pyudev.Monitor.from_netlink(context)
    monitor.filter_by(subsystem='usb')

    observer = pyudev.MonitorObserver(monitor, callback=device_event, name='usb-monitor')
    observer.start()

    print("[+] Surveillance des périphériques USB activée... (CTRL+C pour quitter)")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[-] Arrêt du moniteur USB.")
        observer.stop()

if __name__ == '__main__':
    start_monitor()
