import subprocess
import concurrent.futures

# CONFIG
BASE_IP = "192.168"
RANGE_START = 10
RANGE_END = 30
MAX_THREADS = 200  # Augmente le nombre de threads pour aller plus vite


def ping(ip: str) -> str | None:
    # Ping rapide avec 1 seul paquet et timeout de 1 seconde (Linux)
    proc = subprocess.run(
        ["ping", "-c", "1", "-W", "1", ip],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    if proc.returncode == 0:
        return ip
    return None


def scan_subnet(subnet_base: str) -> list[str]:
    ips = [f"{subnet_base}.{i}" for i in range(1, 255)]
    reachable = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        futures = executor.map(ping, ips)
        for result in futures:
            if result:
                reachable.append(result)
    return reachable


def main():
    all_hosts = []

    for net in range(RANGE_START, RANGE_END + 1):
        subnet = f"{BASE_IP}.{net}"
        hosts = scan_subnet(subnet)
        if hosts:
            print(f"🟢 {subnet}.0/24 - Hosts joignables: {len(hosts)}")
            all_hosts.extend(hosts)
        else:
            print(f"🔴 {subnet}.0/24 - Aucun hôte joignable")

    print("\n🎯 Résumé des hôtes détectés :")
    for host in all_hosts:
        print(f"➡️ {host}")

    print("\n✅ Scan terminé.")


if __name__ == "__main__":
    main()
