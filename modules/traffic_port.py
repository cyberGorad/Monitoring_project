from scapy.all import sniff, IP, TCP

WATCH_PORT = 22

def is_ssh_connection_init(packet):
    """Détecte une tentative de connexion SSH (SYN vers port 22)."""
    if packet.haslayer(IP) and packet.haslayer(TCP):
        tcp_layer = packet[TCP]
        ip_layer = packet[IP]

        if tcp_layer.dport == WATCH_PORT and tcp_layer.flags == 'S':
            print("🚨 Tentative de connexion SSH détectée !")
            print(f"   De {ip_layer.src}:{tcp_layer.sport} vers {ip_layer.dst}:{tcp_layer.dport}")
            print("   (Flag SYN détecté - début de handshake)")
            print("-" * 60)

print("[*] Surveillance des tentatives de connexion SSH (port 22)... CTRL+C pour stopper.")
sniff(filter="tcp", iface="wlo1", prn=is_ssh_connection_init, store=0)
