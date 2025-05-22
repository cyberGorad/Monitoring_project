from scapy.all import sniff
import time

# Variables globales pour compter les paquets
packet_count = 0
start_time = time.time()

def packet_callback(packet):
    global packet_count
    packet_count += 1

def monitor_packet_frequency(interval=1):
    global packet_count, start_time
    while True:
        # Sniffer les paquets sans stockage, callback direct
        sniff(prn=packet_callback, timeout=interval, store=False)

        # Calcul fréquence
        elapsed = time.time() - start_time
        freq = packet_count / elapsed if elapsed > 0 else 0
        print(f"Paquets capturés: {packet_count} | Fréquence: {freq:.2f} paquets/s")

        # Reset compteur et timer pour le prochain intervalle
        packet_count = 0
        start_time = time.time()

if __name__ == "__main__":
    print("Démarrage du monitoring de la fréquence des paquets réseau...")
    monitor_packet_frequency(interval=1)
