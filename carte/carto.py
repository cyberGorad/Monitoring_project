import subprocess
import nmap
import networkx as nx
import matplotlib
matplotlib.use('Agg')  # Utilisation d'un backend sans interface graphique
import matplotlib.pyplot as plt
from ipaddress import ip_network
from datetime import datetime
import time
import threading
from collections import defaultdict

class NetworkMapper:
    def __init__(self, base_ip="192.168.1.0/24"):
        self.base_ip = base_ip
        self.network_graph = nx.Graph()
        self.devices = defaultdict(dict)
        self.running = False
        self.update_interval = 300  # 5 minutes par défaut

    def discover_network(self):
        """Découvre les hôtes actifs sur le réseau"""
        nm = nmap.PortScanner()
        print(f"Scanning network {self.base_ip}...")
        
        # Scan rapide pour découvrir les hôtes actifs
        nm.scan(hosts=self.base_ip, arguments='-sn')
        
        for host in nm.all_hosts():
            if host not in self.devices:
                self.devices[host] = {
                    'first_seen': datetime.now(),
                    'last_seen': datetime.now(),
                    'ports': [],
                    'os': 'unknown',
                    'hostname': nm[host].hostname()
                }
                print(f"New device found: {host} ({self.devices[host]['hostname']})")
            else:
                self.devices[host]['last_seen'] = datetime.now()
                
            # Ajout au graphe réseau
            self.network_graph.add_node(host, 
                                       hostname=self.devices[host]['hostname'],
                                       last_seen=self.devices[host]['last_seen'])

    def scan_ports(self, host):
        """Scan des ports ouverts sur un hôte spécifique"""
        nm = nmap.PortScanner()
        nm.scan(hosts=host, arguments='-sS -T4')
        
        if host in nm.all_hosts():
            self.devices[host]['ports'] = list(nm[host]['tcp'].keys())
            if 'osmatch' in nm[host]:
                self.devices[host]['os'] = nm[host]['osmatch'][0]['name']

    def update_network_graph(self):
        """Met à jour la topologie du réseau"""
        gateway = "192.168.1.1"  # À remplacer par votre passerelle réelle
        
        for host in self.devices:
            if host != gateway:
                self.network_graph.add_edge(gateway, host)

    def visualize_network(self):
        """Visualise le réseau sous forme de graphe et sauvegarde en image"""
        plt.figure(figsize=(12, 8))
        
        # Position des nœuds
        pos = nx.spring_layout(self.network_graph)
        
        # Dessin du graphe
        nx.draw(self.network_graph, pos, with_labels=True, node_size=2000, font_size=10)
        labels = nx.get_node_attributes(self.network_graph, 'hostname')
        nx.draw_networkx_labels(self.network_graph, pos, labels=labels)

        plt.title("Topologie du réseau - " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        plt.subplots_adjust(hspace=0.5, wspace=0.5)  # Ajustement sans tight_layout()
        
        # Sauvegarde au lieu d'afficher
        filename = f"network_map_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        plt.savefig(filename)
        print(f"Graph saved as {filename}")

    def continuous_monitoring(self):
        """Surveillance continue du réseau"""
        while self.running:
            self.discover_network()
            self.update_network_graph()
            
            # Sauvegarde périodique de la visualisation
            if len(self.devices) > 0:
                self.visualize_network()
            
            time.sleep(self.update_interval)

    def start(self):
        """Démarre la surveillance du réseau"""
        if not self.running:
            self.running = True
            monitor_thread = threading.Thread(target=self.continuous_monitoring)
            monitor_thread.daemon = True
            monitor_thread.start()
            print("Network monitoring started...")

    def stop(self):
        """Arrête la surveillance du réseau"""
        self.running = False
        print("Network monitoring stopped.")

if __name__ == "__main__":
    # Exemple d'utilisation
    mapper = NetworkMapper("192.168.1.0/24")  # Remplacer par votre plage IP
    
    try:
        mapper.start()
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        mapper.stop()
