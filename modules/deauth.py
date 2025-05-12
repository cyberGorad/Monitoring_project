from scapy.all import *

def packet_handler(pkt):
    # Vérifie si le paquet est un paquet de désauthentification (Deauth)
    if pkt.haslayer(Dot11Deauth):
        print(f"Packet de désauthentification détecté: {pkt.addr2} -> {pkt.addr1}")

# Interface sans fil à surveiller (ex: wlan0)
sniff(iface="wlo1mon", prn=packet_handler)
