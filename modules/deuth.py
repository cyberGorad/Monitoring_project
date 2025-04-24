from scapy.all import *
import os

# Fonction pour détecter les paquets de déauthentication
def detect_deauth(pkt):
    if pkt.haslayer(Dot11Deauth):
        # Affiche les détails du paquet de déauthentication
        print(f"[!] Attaque de DEAUTH détectée!")
        print(f"De: {pkt[Dot11].addr2} vers: {pkt[Dot11].addr1}")
        print(f"Essid du réseau: {pkt[Dot11Elt].info.decode()}")
        print("-" * 50)

# Fonction pour commencer la capture des paquets sur une interface donnée
def start_monitor_mode(interface):
    # Mettre l'interface en mode monitoring
    os.system(f"sudo ip link set {interface} down")
    os.system(f"sudo ip link set {interface} up")
    os.system(f"sudo iw dev {interface} set type monitor")
    os.system(f"sudo ip link set {interface} up")

    print(f"[+] Mode monitoring activé sur l'interface {interface}")
    sniff(iface=interface, prn=detect_deauth, store=0)

if __name__ == "__main__":
    # Remplacer par l'interface réseau de ton appareil
    interface = "wlo1mon"  # ou l'interface adaptée à ton système
    start_monitor_mode(interface)
