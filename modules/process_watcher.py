import psutil
from datetime import datetime

def bytes_to_mb(bytes_value):
    return round(bytes_value / (1024 * 1024), 2)

def get_sorted_processes_by_memory(threshold_mb=100):
    processes = []

    for proc in psutil.process_iter(['pid', 'name', 'memory_info', 'memory_percent']):
        try:
            mem_mb = bytes_to_mb(proc.info['memory_info'].rss)
            processes.append({
                'pid': proc.info['pid'],
                'name': proc.info['name'],
                'memory_mb': mem_mb,
                'memory_percent': round(proc.info['memory_percent'], 2)
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue

    # Tri décroissant par consommation mémoire
    processes.sort(key=lambda p: p['memory_mb'], reverse=True)

    print(f"{'PID':<10} {'Process Name':<30} {'Memory (MB)':<15} {'% RAM Used':<12}")
    print("=" * 70)
    for p in processes:
        alert = "⚠️" if p['memory_mb'] > threshold_mb else ""
        print(f"{p['pid']:<10} {p['name']:<30} {p['memory_mb']:<15} {p['memory_percent']:<12} {alert}")

if __name__ == "__main__":
    print("📊 Process Watcher - Sorted by Memory -", datetime.now())
    get_sorted_processes_by_memory(threshold_mb=150)
