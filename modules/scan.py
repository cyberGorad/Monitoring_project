from scapy.all import sniff, IP, TCP, UDP, ICMP

# Fonction de traitement des paquets capturés
def process_packet(packet):
    # Vérifier si le paquet contient une couche IP
    if IP in packet:
        ip_src = packet[IP].src
        ip_dst = packet[IP].dst
        protocol = packet[IP].proto  # Identifier le protocole (TCP, UDP, ICMP, etc.)

        # Affichage des informations de base sur le paquet
        print(f"Packet capturé: {ip_src} -> {ip_dst} | Protocole: {protocol}")

        # Vérifier si le paquet est un paquet TCP, UDP ou ICMP et afficher des informations supplémentaires
        if TCP in packet:
            print(f"  Port source: {packet[TCP].sport} | Port destination: {packet[TCP].dport}")
        elif UDP in packet:
            print(f"  Port source: {packet[UDP].sport} | Port destination: {packet[UDP].dport}")
        elif ICMP in packet:
            print(f"  Type ICMP: {packet[ICMP].type}")

        print("-" * 50)

# Fonction pour commencer la capture en temps réel
def start_sniffing(interface="wlo1", filter="ip"):
    print(f"[*] Démarrage de la capture du trafic réseau sur {interface}...")
    sniff(iface=interface, filter=filter, prn=process_packet, store=0)

# Démarrer la capture sur l'interface réseau par défaut
if __name__ == "__main__":
    # Modifier 'eth0' selon l'interface réseau de votre système
    start_sniffing(interface="wlo1")
