const WebSocket = require('ws');
const TOTAL_CLIENTS = 50;

for (let i = 0; i < TOTAL_CLIENTS; i++) {
    const ws = new WebSocket('ws://192.168.43.225:9000');

    ws.on('open', () => {
        ws.send(`Client ${i} connecté`);
    });

    ws.on('message', (data) => {
        console.log(`🔁 Client ${i} a reçu: ${data}`);
    });

    ws.on('close', () => {
        console.log(`❌ Client ${i} déconnecté`);
    });
}
