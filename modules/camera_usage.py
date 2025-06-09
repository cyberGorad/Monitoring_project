import cv2
import platform

# Choisir le backend en fonction de l'OS
def get_backend():
    if platform.system() == "Windows":
        return cv2.CAP_DSHOW
    elif platform.system() == "Linux":
        return cv2.CAP_V4L2
    else:
        return 0  # Fallback

backend = get_backend()

# Vérifie si une caméra est présente (même inactive)
def is_camera_present():
    cam = cv2.VideoCapture(0, backend)
    present = cam.isOpened()
    if present:
        cam.release()
    return present

# Vérifie si la caméra est activement utilisée
def is_camera_active():
    cam = cv2.VideoCapture(0, backend)
    if cam.isOpened():
        ret, frame = cam.read()
        cam.release()
        return ret
    return False

# Analyse de la situation
if not is_camera_present():
    print("[❌] Aucun périphérique caméra détecté sur cette machine.")
elif is_camera_active():
    print("[✅] La caméra est activée (en cours d'utilisation).")
else:
    print("[🛑] Caméra détectée mais actuellement inactive.")
