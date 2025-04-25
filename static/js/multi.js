const loaderContainer = document.querySelector('.loader-container');
const content = document.querySelector('.content');
const ws = new WebSocket('ws://localhost:9000');
const dashboard = document.getElementById('dashboard');
const agentCount = document.getElementById('agent-count');

// Simuler un chargement de 4 secondes
setTimeout(() => {
  loaderContainer.style.display = 'none'; // Cacher le loader
  content.style.display = 'flex';         // Afficher le contenu
}, 4000);

const machines = {}; // { hostname: { card, lastSeen } }
const TIMEOUT = 10000; // 10 secondes d'inactivité avant suppression

// Met à jour le nombre d'agents connectés
function updateAgentCount() {
  const count = Object.keys(machines).length;
  agentCount.textContent = `🧍 Agents connectés : ${count}`;
}

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
    // Création du HTML détaillé pour les ports ouverts
    let openPortsDetails = '<ul>';
    data.open_ports.forEach(p => {
      openPortsDetails += `<li>Port: ${p.port} | PID: ${p.pid ?? "N/A"} | Processus: ${p.process}</li>`;
    });
    openPortsDetails += '</ul>';

      // 🔁 Construction HTML pour les disques
    let diskDetails = '<ul>';
    for (const [mount, percent] of Object.entries(data.disk)) {
      diskDetails += `<li>${mount} : ${percent}% utilisé</li>`;
    }
    diskDetails += '</ul>';

  
    // Création du HTML détaillé pour le trafic sortant
    let outboundTrafficDetails = '<ul>';
    data.outbound_traffic.forEach(c => {
      outboundTrafficDetails += `<li>Local: ${c.local} → Remote: ${c.remote} | Processus: ${c.process}</li>`;
    });
    outboundTrafficDetails += '</ul>';

      // Création du HTML détaillé pour le statut de la batterie
    let batteryStatus =  `
    <strong>🔋 Batterie :</strong> ${data.battery_data.battery_percent}%<br>
    <strong>Statut de la batterie :</strong> ${data.battery_data.battery_status}<br>
  `;

  
    // Contenu final de la carte machine
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
  } else {
    // Nouvelle machine, création de carte
    const card = document.createElement('div');
    card.className = 'card';
    card.innerHTML = `
      <strong>state:</strong> ${data.system_state}<br>
      <strong>system:</strong>${data.os}<br>  
      <strong>🖥️ IP locale :</strong> ${data.local_ip}<br>
      <strong>⚙️ CPU :</strong> ${data.cpu ?? 'N/A'} %<br>
      <strong>🌐 Connexions :</strong> ${data.connections.length} établies<br>
      <strong>💾 Ports ouverts :</strong> ${data.open_ports.length} ouverts<br>
      <strong>📶 Bande passante :</strong> ${data.bandwidth.sent_kb} Ko envoyés, ${data.bandwidth.received_kb} Ko reçus<br>
      <span class="section-title">⏲️ Cron Jobs :</span><br>${data.cron_jobs}<br>
      <span class="section-title">📜 Journaux système :</span><br>${data.logs}<br>
      <span class="section-title">📡 Trafic sortant :</span><br>${data.outbound_traffic.length} connexions sortantes
    `;
    dashboard.appendChild(card);
    machines[hostname] = {
      card,
      lastSeen: Date.now()
    };
    updateAgentCount(); // 🔁 Met à jour le compteur
  }
};

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

ws.onopen = () => console.log('✅ Connexion WebSocket ouverte');
ws.onerror = (err) => console.error('❌ Erreur WebSocket :', err);
ws.onclose = () => console.warn('⚠️ Connexion WebSocket fermée');
