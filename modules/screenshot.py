from PIL import ImageGrab

# Capture écran (Windows & macOS)
image = ImageGrab.grab()

# Sauvegarde
image.save("capture_ecran.png")
