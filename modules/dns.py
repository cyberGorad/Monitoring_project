from scapy.all import sniff, DNS, DNSQR

def dns_monitor(packet):
    if packet.haslayer(DNS) and packet.getlayer(DNS).qr == 0:  # qr == 0 => requête DNS
        dns_query = packet[DNSQR].qname.decode()
        src_ip = packet[0][1].src  # IP source
        print(f"[DNS Request] {src_ip} queried {dns_query}")

if __name__ == "__main__":
    print("Démarrage du sniffing DNS en temps réel... (CTRL+C pour stopper)")
    # Sniffer les paquets UDP sur le port 53 (DNS)
    sniff(filter="udp port 53", prn=dns_monitor, store=False)
