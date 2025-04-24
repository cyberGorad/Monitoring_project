import socket
import tkinter as tk
from tkinter import messagebox

def receive_message():
    """ Reçoit un message du serveur et l'affiche dans une fenêtre """
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if message:
                print(f"Message reçu : {message}")
                # Affiche une fenêtre popup avec le message reçu
                show_popup(message)
        except:
            print("Erreur lors de la réception du message.")
            break

def show_popup(message):
    """ Affiche un message dans une boîte de dialogue Tkinter """
    root = tk.Tk()
    root.withdraw()  # Masque la fenêtre principale
    messagebox.showinfo("Notification de l'Admin", message)

def start_client():
    """ Démarre le client et se connecte au serveur """
    global client_socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('localhost', 9999))  # Adresse et port du serveur

    print("Connecté au serveur. Attente des messages...")
    
    receive_message()

if __name__ == "__main__":
    start_client()
