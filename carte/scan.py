import nmap

def scan_network(network):
    nm = nmap.PortScanner()
    nm.scan(hosts=network, arguments="-sn")  # Scan sans port (-sn)
    return {host: nm[host] for host in nm.all_hosts()}

print(scan_network("192.168.1.0/24"))
