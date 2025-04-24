import subprocess

def check_camera_usage():
    try:
        # Utiliser fuser pour vérifier si le périphérique vidéo est ouvert
        result = subprocess.run(['fuser', '/dev/video0'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.stdout:
            print("La caméra est utilisée.")
        else:
            print("La caméra est disponible.")
    except Exception as e:
        print(f"Erreur lors de la vérification de la caméra: {e}")

check_camera_usage()
