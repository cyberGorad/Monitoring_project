from gtts import gTTS
import os

texte = "Système compromis. Vos données sont maintenant sous notre contrôle. Ne tentez aucune action. Surveillance active."

# Convertir le texte en audio
tts = gTTS(text=texte, lang='fr')
tts.save("cyber.mp3")

# Lire le fichier
os.system("mpg123 hacked.mp3")
