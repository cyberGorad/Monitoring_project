from pynput.keyboard import Listener, Key
import time

# Paramètres
MAX_KEYS = 15          # Nombre de frappes rapides à détecter
TIME_WINDOW = 1        # Fenêtre de temps (en secondes) pour détecter les frappes rapides

# Liste pour stocker les timestamps des frappes
keystrokes = []

# Fonction pour détecter la rapidité des frappes
def on_press(key):
    current_time = time.time()
    
    # Si c'est un Backspace, on l'ignore pour la détection rapide
    if key == Key.backspace:
        return  # Ignore cette touche
    
    # Ajoute l'horodatage de la frappe à la liste
    keystrokes.append(current_time)
    
    # Garde seulement les frappes dans la fenêtre de temps
    keystrokes[:] = [t for t in keystrokes if current_time - t <= TIME_WINDOW]
    
    # Si le nombre de frappes dans la fenêtre est supérieur à MAX_KEYS, c'est une frappe rapide
    if len(keystrokes) >= MAX_KEYS:
        print("🚨 Détection de frappes rapides ! Possible attaque Rubber Ducky ⚠️")
        keystrokes.clear()  # Réinitialiser les frappes pour ne pas déclencher plusieurs alertes

# Démarre l'écoute du clavier
with Listener(on_press=on_press) as listener:
    print("[*] Surveillance des frappes en cours...")
    listener.join()
