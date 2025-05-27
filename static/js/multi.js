    // Fonction pour mettre à jour le nombre d'agents connectés
    function updateAgentCount() {
      const count = Object.keys(machines).length;
      agentCount.textContent = `${count} Machine${count !== 1 ? 's' : ''} connected${count !== 1 ? 's' : ''}`;
    }
const loaderContainer = document.querySelector('.loader-container');
const content = document.querySelector('.content');
const dashboard = document.getElementById('dashboard');
const agentCount = document.getElementById('agent-count');
const noMachine = document.getElementById('no-machine');

let ws;
const SERVER_URL = 'ws://192.168.10.167:9000';
const machines = {}; // { hostname: { card, lastSeen } }
const TIMEOUT = 30000; // 30 secondes d'inactivité avant suppression
let reconnectInterval = 5000; // Intervalle de reconnexion (5 secondes)



function sendCommand(hostname) {
  const input = document.getElementById(`commandInput_${hostname}`);
  const cmd = input.value.trim();

  if (cmd && ws && ws.readyState === WebSocket.OPEN) {
    const payload = {
      type: 'command',
      command: cmd,
      target: hostname  // Agent a envoyer du commande 
    };
    ws.send(JSON.stringify(payload));
    console.log(`[🟢] Command sent to ${hostname} ->`, cmd);
    input.value = ''; // Reset input
  } else {
    console.warn('Impossible to send command');
  }
}




function sendCommandAll() {
  const cmdInput = document.getElementById('commandInputAll');
  const commandText = cmdInput.value.trim();

  if (!commandText) {
    alert("Print correct command");
    return;
  }

  if (ws.readyState !== WebSocket.OPEN) {
    alert("WebSocket non connecté !");
    return;
  }

  const message = {
    type: 'broadcast_command',
    command: commandText
  };

  ws.send(JSON.stringify(message));
  console.log("[🟢] Command sent to all:", commandText);

  cmdInput.value = '';
}





function countMachineStates() {
  let goodCount = 0;
  let mediumCount = 0;
  let criticalCount = 0;

  // Parcourez toutes les machines enregistrées
  for (const hostname in machines) {
    if (machines.hasOwnProperty(hostname)) {
      const machineData = machines[hostname];
      // Utilisez la propriété 'systemState' que nous avons ajoutée
      if (machineData.systemState) {
        if (machineData.systemState === 'Good') {
          goodCount++;
        } else if (machineData.systemState === 'Medium') {
          mediumCount++;
        } else if (machineData.systemState === 'Critical') {
          criticalCount++;
        }
      }
    }
  }

  // Affichez les résultats (par exemple, dans la console)
  console.log(`Machines Good: ${goodCount}`);
  console.log(`Machines Medium: ${mediumCount}`);
  console.log(`Machines Critical: ${criticalCount}`);

  // Optionnel : Mettez à jour des éléments HTML si vous avez des emplacements pour afficher ces chiffres
  // Exemple (ajoutez ces éléments à votre HTML avec les IDs correspondants) :
   if (document.getElementById('goodMachinesCount')) {
     document.getElementById('goodMachinesCount').innerHTML = `<i class="fas fa-globe"></i> Good: ${goodCount}`;
     document.getElementById('goodMachinesCount').style.marginRight = "5px";  
     document.getElementById('goodMachinesCount').style.color = "green"; 
     document.getElementById('goodMachinesCount').style.fontSize = "14px";    

   }
   if (document.getElementById('mediumMachinesCount')) {
     document.getElementById('mediumMachinesCount').innerHTML = `<i class="fas fa-globe"></i> Medium: ${mediumCount}`;
     document.getElementById('mediumMachinesCount').style.marginRight = '5px';
     document.getElementById('mediumMachinesCount').style.color = 'orange';
     document.getElementById('mediumMachinesCount').style.fontSize = "14px";
     
   }
   if (document.getElementById('criticalMachinesCount')) {
     document.getElementById('criticalMachinesCount').innerHTML= `<i class="fas fa-globe"></i> Critical: ${criticalCount}`;
     document.getElementById('criticalMachinesCount').style.marginRight = "5px";
     document.getElementById('criticalMachinesCount').style.color = "red";
     document.getElementById('criticalMachinesCount').style.fontSize = "14px";
   }
}


function connectWebSocket() {
  ws = new WebSocket(SERVER_URL);

  ws.onopen = () => {
    console.log('CONNECTION WEBSOCKET OPENED ...');
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
      console.warn("❌ Message no JSON :", textData);
      dashboard.innerHTML += `
        <div class="card error">
          Message no clear : ${textData}
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
    console.log('⚠️ ERROR WEBSOCKET:', err.message);
    noMachine.textContent = "Reconnecting to server ...";
    setTimeout(connectWebSocket, reconnectInterval); // Essayer de se reconnecter
    reconnectInterval = Math.min(reconnectInterval * 2, 5000); // Double le délai de reconnexion (jusqu'à 30 secondes)
  };

  ws.onclose = () => {
    console.warn('⚠️ CONNECTION CLOSED');
    noMachine.textContent = "Waiting for machines ...";
    setTimeout(connectWebSocket, reconnectInterval); // Essayer de se reconnecter
    reconnectInterval = Math.min(reconnectInterval * 2, 5000); // Double le délai de reconnexion
  };
}








// Fonction de mise à jour d'une carte machine existante
function updateMachineCard(data, hostname) {
  const openPortsDetails = buildOpenPortsDetails(data.open_ports);
  const diskDetails = buildDiskDetails(data.disk);
  const outboundTrafficDetails = buildOutboundTrafficDetails(data.outbound_traffic);
  const batteryStatus = buildBatteryStatus(data.battery_data);


    // Ajoutez cette ligne pour stocker l'état
    if (machines[hostname]) { // S'assurer que l'objet existe déjà
      machines[hostname].systemState = data.system_state;
    }

  machines[hostname].card.innerHTML = `

  <div class="inter-container" style="
  box-shadow:  0 4px 8px ${
    data.system_state === 'Good'
      ? 'green'
      : data.system_state === 'Medium'
      ? 'orange'
      : data.system_state === 'Critical'
      ? 'red'
      : 'grey'
  };">


  <div class="card-inter" style="

  color: ${
    data.system_state === 'Good'
      ? 'green'
      : data.system_state === 'Medium'
      ? 'orange'
      : data.system_state === 'Critical' 
      ? 'red'
      :'grey'
  };
">
  ${data.system_state}
</div>


<div class="card-inter">${data.local_ip}</div>

<div class="card-inter" style="color: ${data.internet_status === 'Up' ? 'green' : 'red'};">
${data.internet_status}
</div>

  
  <div class="card-inter">${data.uptime}</div>

  <div class="card-inter">${data.bandwidth.total_data_mb} Mb</div>
 
  <div class="card-inter" style="

  color: ${
    data.cpu >= 80
      ? 'red'     // vert foncé
      : data.cpu > 60
      ? 'orange' 
      : data.cpu < 60
      ? 'green'    // orange foncé
      : 'white'     // rouge foncé
  };
">
  <strong>CPU</strong> ${data.cpu ?? 'N/A'} %
</div>




<div class="card-inter" style="

color: ${
data.ram < 60
  ? 'green'     // vert foncé
  : data.ram < 80
  ? 'orange'     // orange foncé
  : 'red'     // rouge foncé
};
">
<strong>RAM</strong> ${data.ram ?? 'N/A'} %
</div>


      <div class="card-inter">${data.os}</div>



      <div class="card-inter"><strong>🖥️ Temp :</strong> ${data.temperature}</div>



<div class="card-inter">DISK ${diskDetails}</div>



      <div class="middle-card-inter"><strong>Open Ports:</strong>${data.open_ports.length} open<br>${openPortsDetails}</div>
      <div class="card-inter"><strong>Bandwith</strong> ${data.bandwidth.sent_kb} kb, ${data.bandwidth.received_kb} kb</div>


      <div class="card-inter">${batteryStatus}</div>

      
      <div class="card-inter"><strong>Connection</strong> ${data.connections.length} established</div>
      <div class="card-inter"><span class="section-title">Cron</span><br>${data.cron_jobs}</div>

   
      <div class="full-card-inter"><span class="section-title"></span><br>${outboundTrafficDetails}</div>


      

      <div style="margin-top: 20px;">
  <input id="commandInput_${hostname}" type="text" placeholder="[command for this machine]" style="width: 300px; padding: 5px;" />
  <button onclick="sendCommand('${hostname}')" style="padding: 5px 10px;">execute</button>
</div>



</div>







  `;
  machines[hostname].lastSeen = Date.now();

  countMachineStates();
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
  <div class="inter-container" style="
  box-shadow:  0 4px 8px ${
    data.system_state === 'Good'
      ? 'green'
      : data.system_state === 'Medium'
      ? 'orange'
      : data.system_state === 'Critical'
      ? 'red'
      : 'grey'
  };">


  <div class="card-inter" style="

  color: ${
    data.system_state === 'Good'
      ? 'green'
      : data.system_state === 'Medium'
      ? 'orange'
      : data.system_state === 'Critical' 
      ? 'red'
      :'grey'
  };
">
  ${data.system_state}
</div>


<div class="card-inter">${data.local_ip}</div>

<div class="card-inter" style="color: ${data.internet_status === 'Up' ? 'green' : 'red'};">
${data.internet_status}
</div>

  
  <div class="card-inter">${data.uptime}</div>

  <div class="card-inter">${data.bandwidth.total_data_mb} Mb</div>
 
  <div class="card-inter" style="

  color: ${
    data.cpu >= 80
      ? 'red'     // vert foncé
      : data.cpu > 60
      ? 'orange' 
      : data.cpu < 60
      ? 'green'    // orange foncé
      : 'white'     // rouge foncé
  };
">
  <strong>CPU</strong> ${data.cpu ?? 'N/A'} %
</div>




<div class="card-inter" style="

color: ${
data.ram < 60
  ? 'green'     // vert foncé
  : data.ram < 80
  ? 'orange'     // orange foncé
  : 'red'     // rouge foncé
};
">
<strong>RAM</strong> ${data.ram ?? 'N/A'} %
</div>


      <div class="card-inter">${data.os}</div>



      <div class="card-inter"><strong>🖥️ Temp :</strong> ${data.temperature}</div>



<div class="card-inter">DISK ${diskDetails}</div>



      <div class="middle-card-inter"><strong>Open Ports:</strong>${data.open_ports.length} open<br>${openPortsDetails}</div>
      <div class="card-inter"><strong>Bandwith</strong> ${data.bandwidth.sent_kb} kb, ${data.bandwidth.received_kb} kb</div>


      <div class="card-inter">${batteryStatus}</div>

      
      <div class="card-inter"><strong>Connection</strong> ${data.connections.length} established</div>
      <div class="card-inter"><span class="section-title">Cron</span><br>${data.cron_jobs}</div>

   
      <div class="full-card-inter"><span class="section-title"></span><br>${outboundTrafficDetails}</div>


      

      <div style="margin-top: 20px;">
  <input id="commandInput_${hostname}" type="text" placeholder="[command for this machine]" style="width: 300px; padding: 5px;" />
  <button onclick="sendCommand('${hostname}')" style="padding: 5px 10px;">execute</button>
</div>



</div>




  `;

  
  dashboard.appendChild(card);
  machines[hostname] = {
    card,
    lastSeen: Date.now(),
    systemState: data.system_state // Stockez l'état ici lors de la création
  };



  updateAgentCount(); // 🔁 Met à jour le compteur
  countMachineStates();
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

// Fonction pour construire les détails des disques avec couleurs dynamiques
function buildDiskDetails(disk) {
  let diskDetails = '<ul>';

  for (const [mount, percent] of Object.entries(disk)) {
    const color =
      percent < 60
        ? 'green'
        : percent < 80
        ? 'orange'
        : percent > 80
        ? 'red'
        : 'white';

    diskDetails += `<li style="color: ${color};"><strong>${mount}</strong> : ${percent}% utilisé</li>`;
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

// Fonction pour construire les détails de la batterie avec double couleur dynamique
function buildBatteryStatus(batteryData) {
  // Couleur pour le pourcentage de batterie
  const percentColor =
    batteryData.battery_percent > 60
      ? 'green'
      : batteryData.battery_percent > 20
      ? 'orange'
      : batteryData.battery_percent <= 15
      ? 'red'
      : 'white';

  // Couleur pour le statut (prise secteur ou batterie)
  const statusColor = batteryData.battery_status === "On AC power" ? 'green' : 'white';



  return `
    <div>
      <strong>Battery:</strong> <span style="color: ${percentColor};">${batteryData.battery_percent}%</span><br>
      <strong>Battery Status:</strong> <span style="color: ${statusColor};">${batteryData.battery_status}</span><br>
    </div>
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
