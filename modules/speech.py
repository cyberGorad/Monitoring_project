import pyttsx3

# Initialisation du moteur TTS
engine = pyttsx3.init()

# Texte à lire
text = "Bonjour, comment ça va?"

# Conversion du texte en parole
engine.say(text)

# Attendre que la parole soit terminée
engine.runAndWait()
