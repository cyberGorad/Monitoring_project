const http = require('http');
const WebSocket = require('ws');

// Serveur HTTP minimal
const server = http.createServer((req, res) => {
  res.writeHead(404);
  res.end("WebSocket Server Only");
});

// Serveur WebSocket
const wss = new WebSocket.Server({ server });

wss.on('connection', (ws, req) => {
  const ip = req.socket.remoteAddress;
  console.log(`Client connecté depuis ${ip}`);

  // Écouter les messages venant du client
  ws.on('message', (msg) => {
    console.log('📩 Reçu:', msg);
    
    // Par exemple, faire une broadcast à tous les clients
    wss.clients.forEach(client => {
      if (client.readyState === WebSocket.OPEN) {
        client.send(msg);
      }
    });
  });

    // Gérer la fermeture propre du WebSocket
    ws.on('close', () => {
        console.log('Client déconnecté');
    });


  // Envoi d'une commande après la connexion du client
  setTimeout(() => {
    const command = {
      type: 'command',
      command: 'caja /' // Commande à exécuter côté client
    };
    ws.send(JSON.stringify(command)); // Envoie la commande au client
    console.log('📤 Commande envoyée:', command.command);
  }, 5000); // Envoie la commande après 5 secondes de connexion
});

// Écoute sur le port 9000
server.listen(9000, '192.168.43.225', () => {
  console.log('🚀 Serveur WebSocket disponible sur : ws://192.168.43.225:9000');
});
