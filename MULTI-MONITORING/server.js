const http = require('http');
const fs = require('fs');
const WebSocket = require('ws');

const server = http.createServer((req, res) => {
    if (req.url === '/') {
        fs.readFile('dashboard.html', (err, data) => {
            if (err) {
                res.writeHead(500);
                return res.end('Erreur serveur');
            }
            res.writeHead(200, {'Content-Type': 'text/html'});
            res.end(data);
        });
    }
});

const wss = new WebSocket.Server({ server });

wss.on('connection', (ws) => {
    console.log('Client connecté');

    ws.on('message', (msg) => {
        console.log('Reçu:', msg);

        // Diffuser le message à tous les clients connectés
        wss.clients.forEach(client => {
            if (client.readyState === WebSocket.OPEN) {
                client.send(msg);
            }
        });
    });
});

server.listen(9000, () => {
    console.log('Serveur Web + WebSocket lancé sur http://localhost:9000');
});
