#!/usr/bin/env python

import asyncio
import websockets
import json
import logging

# Configuration du logging pour afficher les informations et erreurs
# Using a date format less likely to be confused (ISO 8601 style)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

# Dictionnaire pour stocker les informations sur les clients connectés (optionnel)
# La clé sera une représentation de l'adresse du client (ip:port)
connected_clients = {}

async def handler(websocket, path):
    """
    Gère la connexion d'un client WebSocket individuel.
    Reçoit les messages, les décode et les affiche.
    'path' est requis par la bibliothèque websockets même s'il n'est pas utilisé ici.
    """
    client_address = websocket.remote_address
    client_ip = client_address[0]
    client_port = client_address[1]
    client_key = f"{client_ip}:{client_port}"
    connected_clients[client_key] = websocket
    logging.info(f"Client connecté: {client_key}")

    try:
        # Boucle pour recevoir les messages du client
        async for message in websocket:
            try:
                # Tenter de décoder le message JSON
                data = json.loads(message)
                logging.info(f"Données reçues de {client_ip}:")
                # Afficher les données de manière lisible (avec indentation)
                print(json.dumps(data, indent=2))

                # --- Zone pour traitement supplémentaire ---
                # Ici, vous pourriez ajouter du code pour :
                # - Valider les données reçues
                # - Stocker les données dans une base de données
                # - Déclencher des alertes basées sur certaines métriques
                # - Envoyer une réponse au client si nécessaire (await websocket.send(...))
                # -----------------------------------------

            except json.JSONDecodeError:
                logging.error(f"Message non JSON reçu de {client_key}: {message[:100]}...") # Limite la taille du log
            except Exception as e:
                logging.error(f"Erreur lors du traitement du message de {client_key}: {e}", exc_info=True) # Ajoute la traceback au log

    except websockets.exceptions.ConnectionClosedOK:
        logging.info(f"Client {client_key} déconnecté proprement (ClosedOK).")
    except websockets.exceptions.ConnectionClosedError as e:
        # Log spécifique pour les erreurs de fermeture communes (peut être normal si le client coupe brutalement)
        logging.warning(f"Connexion fermée avec erreur pour {client_key}: {e}")
    except Exception as e:
        logging.error(f"Erreur inattendue avec le client {client_key}: {e}", exc_info=True) # Ajoute la traceback
    finally:
        # Nettoyer lorsque le client se déconnecte, quelle que soit la raison
        if client_key in connected_clients:
            del connected_clients[client_key]
        logging.info(f"Client {client_key} retiré. Clients connectés: {len(connected_clients)}")

async def main():
    """
    Fonction principale pour démarrer le serveur WebSocket.
    """
    # Écoute sur toutes les interfaces réseau (0.0.0.0) sur le port 8000
    # Assurez-vous que ce port correspond à celui utilisé par les clients (SERVER_URL)
    host = "0.0.0.0"
    port = 8000

    # Démarrer le serveur WebSocket en passant la fonction handler correcte
    # websockets.serve s'attend à un handler acceptant (websocket, path)
    server = await websockets.serve(handler, host, port)
    logging.info(f"Serveur WebSocket démarré et à l'écoute sur ws://{host}:{port}")

    # Garde le serveur en cours d'exécution jusqu'à ce qu'il soit arrêté
    try:
        await server.wait_closed()
    finally:
        # Assure la fermeture propre du serveur lors de l'arrêt
        server.close()
        await server.wait_closed() # Attend que la fermeture soit complète
        logging.info("Serveur WebSocket arrêté.")


if __name__ == "__main__":
    try:
        # Exécute la boucle d'événements asyncio avec la fonction main
        asyncio.run(main())
    except KeyboardInterrupt:
        # Gère l'arrêt manuel via Ctrl+C
        logging.info("Arrêt demandé par l'utilisateur (KeyboardInterrupt)...")
    except OSError as e:
        # Gère les erreurs courantes comme le port déjà utilisé
        if "Address already in use" in str(e):
             logging.critical(f"Erreur: Le port {8000} est déjà utilisé. Arrêtez l'autre application ou choisissez un autre port.")
        else:
             logging.critical(f"Erreur système (OS Error) lors du démarrage du serveur: {e}", exc_info=True)
    except Exception as e:
        # Capture toute autre erreur critique au démarrage
        logging.critical(f"Erreur critique non gérée lors de l'exécution: {e}", exc_info=True)
