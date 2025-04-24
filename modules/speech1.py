from gtts import gTTS
import os

# Texte à lire
text = "tunnel demmaré avec succès"

# Langue de la parole (par exemple, "fr" pour français)
language = 'fr'

# Conversion du texte en parole
speech = gTTS(text=text, lang=language, slow=False)

# Sauvegarder le fichier audio
speech.save("success.mp3")

# Jouer le fichier audio (avec une application comme mpg321 ou VLC)
os.system("mpg123 success.mp3")
