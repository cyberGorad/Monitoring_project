import socket
import threading

# Liste des clients connectés
clients = []

def handle_client(client_socket):
    """ Gère l'envoi de messages au client """
    while True:
        try:
            message = input("Message à envoyer à tous les clients : ")  # Message de l'admin
            # Envoie le message à tous les clients connectés
            for client in clients:
                try:
                    client.send(message.encode('utf-8'))
                except:
                    clients.remove(client)
        except Exception as e:
            print(f"Erreur avec le client : {e}")
            break
    client_socket.close()
    clients.remove(client_socket)

def start_server():
    """ Démarre le serveur et écoute les messages des clients """
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', 9999))  # L'écoute sur toutes les interfaces réseau
    server.listen(5)
    print("Serveur démarré. En attente de connexions...")

    while True:
        client_socket, addr = server.accept()
        print(f"Connexion de {addr}")
        clients.append(client_socket)
        client_handler = threading.Thread(target=handle_client, args=(client_socket,))
        client_handler.start()

if __name__ == "__main__":
    start_server()
