import psutil

def afficher_utilisation_swap():
    swap = psutil.swap_memory()
    
    print("=== Surveillance SWAP ===")
    print(f"Total     : {round(swap.total / (1024 * 1024), 2)} MB")
    print(f"Utilisé   : {round(swap.used / (1024 * 1024), 2)} MB")
    print(f"Libre     : {round(swap.free / (1024 * 1024), 2)} MB")
    print(f"Pourcentage utilisé : {swap.percent}%")

afficher_utilisation_swap()
