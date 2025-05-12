from scapy.all import sniff

def packet_callback(packet):
    print(packet.summary())

print("[*] Démarrage du sniffing réseau... CTRL+C pour arrêter.")
sniff(prn=packet_callback, store=0)
