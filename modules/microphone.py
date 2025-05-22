import sounddevice as sd
from scipy.io.wavfile import write

def record_audio(duration=10, filename="audio_capture.wav"):
    fs = 44100  # Fréquence d’échantillonnage
    print("[*] Enregistrement audio en cours...")
    audio = sd.rec(int(duration * fs), samplerate=fs, channels=1)
    sd.wait()
    write(filename, fs, audio)
    print(f"[+] Audio enregistré : {filename}")

# Exemple : enregistre 10 secondes
record_audio(10)
