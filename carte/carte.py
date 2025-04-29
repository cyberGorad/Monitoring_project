import subprocess
import nmap
import networkx as nx
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
        self.update_interval = 10  # Rafraîchir toutes les 10 secondes

        # Mode interactif pour visualiser en temps réel
        plt.ion()
        self.fig, self.ax = plt.subplots(figsize=(12, 8))

    def discover_network(self):
        """Découvre les hôtes actifs sur le réseau"""
        nm = nmap.PortScanner()
        print(f"Scanning network {self.base_ip}...")

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

            self.network_graph.add_node(host, hostname=self.devices[host]['hostname'])

    def update_network_graph(self):
        """Met à jour la topologie du réseau"""
        gateway = "192.168.1.1"

        for host in self.devices:
            if host != gateway:
                self.network_graph.add_edge(gateway, host)

    def visualize_network(self):
        """Affiche la topologie du réseau en temps réel (doit être exécuté dans le thread principal)"""
        self.ax.clear()  # Efface le graphique précédent

        pos = nx.spring_layout(self.network_graph)  
        nx.draw(self.network_graph, pos, with_labels=True, node_size=2000, font_size=10, ax=self.ax)
        
        labels = nx.get_node_attributes(self.network_graph, 'hostname')
        nx.draw_networkx_labels(self.network_graph, pos, labels=labels, ax=self.ax)

        self.ax.set_title("Topologie du réseau - " + datetime.now().strftime("%H:%M:%S"))
        plt.draw()

    def continuous_monitoring(self):
        """Surveillance continue du réseau (sans Matplotlib pour éviter les erreurs de thread)"""
        while self.running:
            self.discover_network()
            self.update_network_graph()
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
    mapper = NetworkMapper("192.168.1.0/24")  

    try:
        mapper.start()
        while True:
            mapper.visualize_network()  # Exécute la visualisation uniquement dans le thread principal
            plt.pause(1)  # Pause pour éviter un plantage
    except KeyboardInterrupt:
        mapper.stop()
        plt.ioff()  # Désactiver le mode interactif à la fermeture
