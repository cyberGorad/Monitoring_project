    // Fonction pour mettre à jour le nombre d'agents connectés
    function updateAgentCount() {
      const count = Object.keys(machines).length;
      agentCount.textContent = `${count} Machines${count !== 1 ? 's' : ''} connected${count !== 1 ? 's' : ''}`;
    }
const loaderContainer = document.querySelector('.loader-container');
const content = document.querySelector('.content');
const dashboard = document.getElementById('dashboard');
const agentCount = document.getElementById('agent-count');
const noMachine = document.getElementById('no-machine');

let ws;
const SERVER_URL = 'ws://192.168.43.225:9000';
const machines = {}; // { hostname: { card, lastSeen } }
const TIMEOUT = 30000; // 30 secondes d'inactivité avant suppression
let reconnectInterval = 5000; // Intervalle de reconnexion (5 secondes)



function connectWebSocket() {
  ws = new WebSocket(SERVER_URL);

  ws.onopen = () => {
    console.log('✅ Connexion WebSocket ouverte');
    reconnectInterval = 5000; // Réinitialiser le délai de reconnexion
  };

  ws.onmessage = async (event) => {
    let textData = '';

    

    if (event.data instanceof Blob) {
      textData = await event.data.text();
    } else {
      textData = event.data;
    }

    let data;
    try {
      data = JSON.parse(textData);
    } catch (e) {
      console.warn("❌ Message non-JSON :", textData);
      dashboard.innerHTML += `
        <div class="card error">
          Message non reconnu : ${textData}
        </div>
      `;
      return;
    }

    const hostname = data.local_ip || 'Inconnu';

    if (machines[hostname]) {
      // Mise à jour des cartes existantes comme dans ton code
      updateMachineCard(data, hostname);
    } else {
      // Création d'une nouvelle carte pour une machine non encore présente
      createNewMachineCard(data, hostname);
    }
  };

  ws.onerror = (err) => {
    console.log('⚠️ Erreur WebSocket:', err.message);
    noMachine.textContent = "Tentative de reconnexion...";
    setTimeout(connectWebSocket, reconnectInterval); // Essayer de se reconnecter
    reconnectInterval = Math.min(reconnectInterval * 2, 30000); // Double le délai de reconnexion (jusqu'à 30 secondes)
  };

  ws.onclose = () => {
    console.warn('⚠️ Connexion WebSocket fermée');
    noMachine.textContent = "WebSocket fermé. Tentative de reconnexion...";
    setTimeout(connectWebSocket, reconnectInterval); // Essayer de se reconnecter
    reconnectInterval = Math.min(reconnectInterval * 2, 30000); // Double le délai de reconnexion
  };
}

// Fonction de mise à jour d'une carte machine existante
function updateMachineCard(data, hostname) {
  const openPortsDetails = buildOpenPortsDetails(data.open_ports);
  const diskDetails = buildDiskDetails(data.disk);
  const outboundTrafficDetails = buildOutboundTrafficDetails(data.outbound_traffic);
  const batteryStatus = buildBatteryStatus(data.battery_data);

  machines[hostname].card.innerHTML = `


    <strong>System status:</strong> ${data.system_state}<br>
    <strong>System:</strong> ${data.os}<br> 
    <strong>INTERNET STATUS:</strong> ${data.internet_status}<br>
    <strong>🖥️ IP locale :</strong> ${data.local_ip}<br>
    <strong>🖥️ Temp :</strong> ${data.temperature}<br>
    <strong>⚙️ CPU :</strong> ${data.cpu ?? 'N/A'} %<br>
    <strong>⚙️ RAM :</strong> ${data.ram ?? 'N/A'} %<br>
    <strong>⚙️ DISQUES :</strong><br>${diskDetails}
    ${batteryStatus}
    <strong>🌐 Connexions :</strong> ${data.connections.length} établies<br>
    <strong>💾 Ports ouverts :</strong> ${data.open_ports.length} ouverts<br>
    ${openPortsDetails}
    <strong>📶 Bande passante :</strong> ${data.bandwidth.sent_kb} Ko envoyés, ${data.bandwidth.received_kb} Ko reçus<br>
    <span class="section-title">⏲️ Cron Jobs :</span><br>${data.cron_jobs}<br>
    <span class="section-title">📜 Journaux système :</span><br>${data.logs}<br>
    <span class="section-title">📡 Trafic sortant :</span><br>${data.outbound_traffic.length} connexions sortantes<br>
    ${outboundTrafficDetails}
  `;
  machines[hostname].lastSeen = Date.now();
}

// Fonction de création d'une nouvelle carte pour une machine
function createNewMachineCard(data, hostname) {
  const card = document.createElement('div');
  card.className = 'card';
  const openPortsDetails = buildOpenPortsDetails(data.open_ports);
  const diskDetails = buildDiskDetails(data.disk);
  const outboundTrafficDetails = buildOutboundTrafficDetails(data.outbound_traffic);
  const batteryStatus = buildBatteryStatus(data.battery_data);

  card.innerHTML = `
    <strong>System status:</strong> ${data.system_state}<br>
    <strong>System:</strong> ${data.os}<br> 
    <strong>INTERNET STATUS:</strong> ${data.internet_status}<br>
    <strong>🖥️ IP locale :</strong> ${data.local_ip}<br>
    <strong>🖥️ Temp :</strong> ${data.temperature}<br>
    <strong>⚙️ CPU :</strong> ${data.cpu ?? 'N/A'} %<br>
    <strong>⚙️ RAM :</strong> ${data.ram ?? 'N/A'} %<br>
    <strong>⚙️ DISQUES :</strong><br>${diskDetails}
    ${batteryStatus}
    <strong>🌐 Connexions :</strong> ${data.connections.length} établies<br>
    <strong>💾 Ports ouverts :</strong> ${data.open_ports.length} ouverts<br>
    ${openPortsDetails}
    <strong>📶 Bande passante :</strong> ${data.bandwidth.sent_kb} Ko envoyés, ${data.bandwidth.received_kb} Ko reçus<br>
    <span class="section-title">⏲️ Cron Jobs :</span><br>${data.cron_jobs}<br>
    <span class="section-title">📜 Journaux système :</span><br>${data.logs}<br>
    <span class="section-title">📡 Trafic sortant :</span><br>${data.outbound_traffic.length} connexions sortantes<br>
    ${outboundTrafficDetails}
  `;
  dashboard.appendChild(card);
  machines[hostname] = {
    card,
    lastSeen: Date.now()
  };
  updateAgentCount(); // 🔁 Met à jour le compteur
}





// Fonction pour construire la liste des ports ouverts
function buildOpenPortsDetails(openPorts) {
  let openPortsDetails = '<ul>';
  openPorts.forEach(p => {
    openPortsDetails += `<li>Port: ${p.port} | PID: ${p.pid ?? "N/A"} | Processus: ${p.process}</li>`;
  });
  openPortsDetails += '</ul>';
  return openPortsDetails;
}

// Fonction pour construire les détails des disques
function buildDiskDetails(disk) {
  let diskDetails = '<ul>';
  for (const [mount, percent] of Object.entries(disk)) {
    diskDetails += `<li>${mount} : ${percent}% utilisé</li>`;
  }
  diskDetails += '</ul>';
  return diskDetails;
}

// Fonction pour construire les détails du trafic sortant
function buildOutboundTrafficDetails(outboundTraffic) {
  let outboundTrafficDetails = '<ul>';
  outboundTraffic.forEach(c => {
    outboundTrafficDetails += `<li>Local: ${c.local} → Remote: ${c.remote} | Processus: ${c.process}</li>`;
  });
  outboundTrafficDetails += '</ul>';
  return outboundTrafficDetails;
}

// Fonction pour construire les détails de la batterie
function buildBatteryStatus(batteryData) {
  return `
    <strong>🔋 Batterie :</strong> ${batteryData.battery_percent}%<br>
    <strong>Statut de la batterie :</strong> ${batteryData.battery_status}<br>
  `;
}

// Connexion initiale
connectWebSocket();

// Supprimer les machines inactives
setInterval(() => {
  const now = Date.now();
  for (const [hostname, machine] of Object.entries(machines)) {
    if (now - machine.lastSeen > TIMEOUT) {
      dashboard.removeChild(machine.card);
      delete machines[hostname];
      console.log(`❌ Machine "${hostname}" retirée pour inactivité`);
      updateAgentCount(); // 🔁 Met à jour le compteur
    }
  }
}, 2000);
