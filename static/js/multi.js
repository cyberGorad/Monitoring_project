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
const SERVER_URL = 'ws://192.168.10.232:9000';
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


function sendMessageAll() {
  const msgInput = document.getElementById('messageInputAll');
  const msgText = msgInput.value.trim();

  if (!msgText) {
    alert("Print correct text");
    return;
  }

  if (ws.readyState !== WebSocket.OPEN) {
    alert("Cannot send message yet!");
    return;
  }

  const message = {
    type: 'message',
    message: msgText
  };

  ws.send(JSON.stringify(message));
  console.log("[🟢] Messsage sent to all:", msgText);

  msgInput.value = '';
}


function getCpuColor(cpu) {
  if (cpu >= 80) return 'red';
  if (cpu >= 60) return 'orange';
  return 'green';
}

function getRamColor(ram) {
  if (ram >= 80) return 'red';
  if (ram >= 60) return 'orange';
  return 'green';
}



function displayCommandResult(result) {
  const container = document.getElementById("commandOutput");

  const resultBox = document.createElement("div");
  resultBox.className = "command-result";
  resultBox.style.cssText = `
    background: #000;
    color: #0f0;
    border: 1px solid #444;
    padding: 10px;
    margin-top: 10px;
    font-family: monospace;
    white-space: pre-wrap;
    border-radius: 5px;
  `;
  resultBox.textContent = result;

  container.prepend(resultBox); // Ajoute en haut
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
     document.getElementById('goodMachinesCount').innerHTML = `<i class="fas fa-leaf"></i> Good: ${goodCount}`;
     document.getElementById('goodMachinesCount').style.marginRight = "5px";  
     document.getElementById('goodMachinesCount').style.color = "green"; 
     document.getElementById('goodMachinesCount').style.fontSize = "14px";    

   }
   if (document.getElementById('mediumMachinesCount')) {
     document.getElementById('mediumMachinesCount').innerHTML = `<i class="fas fa-lightbulb"></i> Medium: ${mediumCount}`;
     document.getElementById('mediumMachinesCount').style.marginRight = '5px';
     document.getElementById('mediumMachinesCount').style.color = 'orange';
     document.getElementById('mediumMachinesCount').style.fontSize = "14px";
     
   }
   if (document.getElementById('criticalMachinesCount')) {
     document.getElementById('criticalMachinesCount').innerHTML= `<i class="fas fa-skull-crossbones"></i> Critical: ${criticalCount}`;
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



      if (data.type === "command_result") {
        displayCommandResult(data.result);
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
    noMachine.textContent = "[Waiting for machines]";
    noMachine.style.fontSize = "12px";
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
  const processalert = displayUnauthorizedProcesses(data.allow_connection?.processes);






    // Ajoutez cette ligne pour stocker l'état
    if (machines[hostname]) { // S'assurer que l'objet existe déjà
      machines[hostname].systemState = data.system_state;
    }

  machines[hostname].card.innerHTML = `


  <p style="position:absolute;"><i class="fas fa-globe"></i> ${
    data.agent_type === 'lan'
    ? 'LAN'
    :data.agent_type === 'wan'
    ? 'WAN'
    :'error'


}<p>



<div id="commandOutput">

</div>







      




<div style="display:flex;flex-direction:row;margin-left:100px;height:10px;margin-top:3px;">

  <i class="fas fa-arrow-up" style="color: #00FF00;font-size:10px;"></i> 
  <span style="color: #93c5fd;font-size:11px;">${data.bandwidth.sent_kb} KB</span>

  <i class="fas fa-arrow-down" style="color: white;margin-left:10px;font-size:10px;"></i> 
  <span style="color: #6ee7b7;font-size:11px;">${data.bandwidth.received_kb} KB</span>
</div>




<div class="batery">${batteryStatus}</div>

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

  <div class="column-card-inter">
      <div class="inter" style="
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
      ${data.system_state === 'Good'
    ? '<i class="fas fa-leaf"></i> Good'
    :data.system_state === 'Medium'
    ? '<i class="fas fa-lightbulb"></i> Medium'
    :data.system_state === 'Critical'
    ? '<i class="fas fa-skull-crossbones"></i> Critical'
    :'error'
    }
    </div>

    <div class="inter" style="font-size:10px;margin-right:1px;">${data.local_ip}</div>
  </div>


  <div class="column-card-inter">
    <div class="inter" style="color: ${data.internet_status === 'Up' ? 'green' : 'red'};">
    ${data.internet_status === 'Up'
    ? '<i class="fas fa-wifi"></i> Up'
    : '<i class="fas fa-times-circle"></i> Down'
  
  }
    </div>
      <div class="inter">${data.bandwidth.total_data_mb} Mb</div>
  </div>



  <div class="card-inter">${data.uptime}</div>



  



  <div class="card-inter"><p>Connection</p> ${data.connections.length} established</div>
 


  <div class="row-card-inter">
  <div class="circle-chart">
    <svg viewBox="0 0 36 36" class="circular-chart ${getCpuColor(data.cpu)}">
      <path class="circle-bg"
            d="M18 2.0845
               a 15.9155 15.9155 0 0 1 0 31.831
               a 15.9155 15.9155 0 0 1 0 -31.831" />
      <path class="circle"
            stroke-dasharray="${data.cpu}, 100"
            d="M18 2.0845
               a 15.9155 15.9155 0 0 1 0 31.831
               a 15.9155 15.9155 0 0 1 0 -31.831" />
      <text x="18" y="20.35" class="percentage">${data.cpu ?? 'N/A'}%</text>
    </svg>
    <p>CPU</p>
  </div>

  <div class="circle-chart">
    <svg viewBox="0 0 36 36" class="circular-chart ${getRamColor(data.ram)}">
      <path class="circle-bg"
            d="M18 2.0845
               a 15.9155 15.9155 0 0 1 0 31.831
               a 15.9155 15.9155 0 0 1 0 -31.831" />
      <path class="circle"
            stroke-dasharray="${data.ram}, 100"
            d="M18 2.0845
               a 15.9155 15.9155 0 0 1 0 31.831
               a 15.9155 15.9155 0 0 1 0 -31.831" />
      <text x="18" y="20.35" class="percentage">${data.ram ?? 'N/A'}%</text>
    </svg>
    <p>RAM</p>
  </div>
</div>


      



<div class="card-inter">${data.os}</div>



    
<div class="card-inter">${diskDetails}</div>



      <div class="middle-card-inter">open port :</p> ${data.open_ports.length}<br> ${openPortsDetails}</div>



      <div class="middle-card-inter">${processalert}</div>


      
      


      

    




    <div class="full-card-inter"><span class="section-title"></span>${outboundTrafficDetails}</div>
      
      <div class="full-card-inter"><span class="section-title">Cron</span><br>${data.cron_jobs}</div>

   
      


      


      <div style="margin-top: 20px;margin-bottom:20px;">
  <input id="commandInput_${hostname}" type="text" placeholder="[command for this machine]" style="width: 300px; padding: 5px;" />
  <button onclick="sendCommand('${hostname}')" style="background-color:black; border-radius:10px;color:#00FF00;padding: 5px 10px;">execute</button>
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

  const processalert = displayUnauthorizedProcesses(data.allow_connection?.processes);



  card.innerHTML = `

  
  
  <p style="position:absolute;"><i class="fas fa-globe"></i> ${
    data.agent_type === 'lan'
    ? 'LAN'
    :data.agent_type === 'wan'
    ? 'WAN'
    :'error'


}<p>



<div id="commandOutput">

</div>







      




<div style="display:flex;flex-direction:row;margin-left:100px;height:10px;margin-top:3px;">

  <i class="fas fa-arrow-up" style="color: #00FF00;font-size:10px;"></i> 
  <span style="color: #93c5fd;font-size:11px;">${data.bandwidth.sent_kb} KB</span>

  <i class="fas fa-arrow-down" style="color: white;margin-left:10px;font-size:10px;"></i> 
  <span style="color: #6ee7b7;font-size:11px;">${data.bandwidth.received_kb} KB</span>
</div>




<div class="batery">${batteryStatus}</div>

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

  <div class="column-card-inter">
      <div class="inter" style="
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
      ${data.system_state === 'Good'
    ? '<i class="fas fa-leaf"></i> Good'
    :data.system_state === 'Medium'
    ? '<i class="fas fa-lightbulb"></i> Medium'
    :data.system_state === 'Critical'
    ? '<i class="fas fa-skull-crossbones"></i> Critical'
    :'error'
    }
    </div>

    <div class="inter" style="font-size:10px;margin-right:1px;">${data.local_ip}</div>
  </div>


  <div class="column-card-inter">
    <div class="inter" style="color: ${data.internet_status === 'Up' ? 'green' : 'red'};">
    ${data.internet_status === 'Up'
    ? '<i class="fas fa-wifi"></i> Up'
    : '<i class="fas fa-times-circle"></i> Down'
  
  }
    </div>
      <div class="inter">${data.bandwidth.total_data_mb} Mb</div>
  </div>



  <div class="card-inter">${data.uptime}</div>



  



  <div class="card-inter"><p>Connection</p> ${data.connections.length} established</div>
 


  <div class="row-card-inter">
  <div class="circle-chart">
    <svg viewBox="0 0 36 36" class="circular-chart ${getCpuColor(data.cpu)}">
      <path class="circle-bg"
            d="M18 2.0845
               a 15.9155 15.9155 0 0 1 0 31.831
               a 15.9155 15.9155 0 0 1 0 -31.831" />
      <path class="circle"
            stroke-dasharray="${data.cpu}, 100"
            d="M18 2.0845
               a 15.9155 15.9155 0 0 1 0 31.831
               a 15.9155 15.9155 0 0 1 0 -31.831" />
      <text x="18" y="20.35" class="percentage">${data.cpu ?? 'N/A'}%</text>
    </svg>
    <p>CPU</p>
  </div>

  <div class="circle-chart">
    <svg viewBox="0 0 36 36" class="circular-chart ${getRamColor(data.ram)}">
      <path class="circle-bg"
            d="M18 2.0845
               a 15.9155 15.9155 0 0 1 0 31.831
               a 15.9155 15.9155 0 0 1 0 -31.831" />
      <path class="circle"
            stroke-dasharray="${data.ram}, 100"
            d="M18 2.0845
               a 15.9155 15.9155 0 0 1 0 31.831
               a 15.9155 15.9155 0 0 1 0 -31.831" />
      <text x="18" y="20.35" class="percentage">${data.ram ?? 'N/A'}%</text>
    </svg>
    <p>RAM</p>
  </div>
</div>


      



<div class="card-inter">${data.os}</div>



    
<div class="card-inter">${diskDetails}</div>



      <div class="middle-card-inter">open port :</p> ${data.open_ports.length}<br> ${openPortsDetails}</div>



      <div class="middle-card-inter">${processalert}</div>


      
      


      

    




    <div class="full-card-inter"><span class="section-title"></span>${outboundTrafficDetails}</div>
      
      <div class="full-card-inter"><span class="section-title">Cron</span><br>${data.cron_jobs}</div>

   
      


      


      <div style="margin-top: 20px;margin-bottom:20px;">
  <input id="commandInput_${hostname}" type="text" placeholder="[command for this machine]" style="width: 300px; padding: 5px;" />
  <button onclick="sendCommand('${hostname}')" style="background-color:black; border-radius:10px;color:#00FF00;padding: 5px 10px;">execute</button>
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





function buildOpenPortsDetails(openPorts) {
  let openPortsDetails = '<div style="display: flex; flex-direction: column; gap: 6px;">';

  openPorts.forEach(p => {
    openPortsDetails += `
      <div style="display: flex; align-items: center; gap: 10px; padding: 6px 10px; border-radius: 6px;">
        <i class="fas fa-plug" style="color:#00FF00;"></i>
        <span><p>Port</p> ${p.port}</span>

        <i class="fas fa-microchip" style="color:#00FF00;"></i>
        <span><p>pid</p> ${p.pid ?? "N/A"}</span>

        <i class="fas fa-cogs" style="color:#00FF00;"></i>
        <span><p>Proc</p> ${p.process}</span>
      </div>`;
  });

  openPortsDetails += '</div>';
  return openPortsDetails;
}


function displayUnauthorizedProcesses(processesparam) {
  // Sécurisation : si la donnée est null/undefined ou pas un tableau, on renvoie un message par défaut
  if (!Array.isArray(processesparam) || processesparam.length === 0) {
    return `<p>No process alert</p>`;
  }

  let alertprocess = '<div style="display: flex; flex-direction: column; gap: 6px;">';

  processesparam.forEach(proc => {
    alertprocess += `
      <div style="display: flex; align-items: center;font-size:9px;border-radius: 6px;color:red;justify-content:space-around;">
      <span> ${proc.name}</span>

      <span>PID: ${proc.pid?? "N/A"}</span>


    </div>`;
  });

  alertprocess += '</div>';
  return alertprocess;
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

    diskDetails += `<li style="color: ${color};font-size: 8px;margin-top:5px;"><p>${mount}</p> ${percent}%</li>`;
  }

  diskDetails += '</ul>';
  return diskDetails;
}


function buildOutboundTrafficDetails(outboundTraffic) {
  let outboundTrafficDetails = `
    <style>
      .process-small {
        font-size: 12px;
        color: #00FF00;
      }
      .process-icon {
        display: inline-block;
        width: 8px;
        height: 8px;
        background-color: #00FF00;
        border-radius: 50%;
        margin-right: 5px;
        vertical-align: middle;
      }
    </style>
    <ul>
  `;
  outboundTraffic.forEach(c => {
    outboundTrafficDetails += `
      <li>
        Local: ${c.local} → Remote: ${c.remote} | Processus: 
        <span class="process-icon"></span>
        <span class="process-small">${c.process}</span>
      </li>`;
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
    <div style="display:flex;justify-content:right; flex-direction: row;font-size:9px;margin-bottom:2px;">
      <p><i class="fas fa-battery-full"></i>:</p> <span style="color: ${percentColor};">${batteryData.battery_percent}%</span>
      <p style="margin-left:5px;"><i class="fas fa-plug"></i>:</p> <span style="color: ${statusColor};">${batteryData.battery_status}</span>
    </div>
  `;
}


// Connexion initiale
connectWebSocket();

// Supprimer les machines inactives avec animation de sortie
setInterval(() => {
  const now = Date.now();
  for (const [hostname, machine] of Object.entries(machines)) {
    if (now - machine.lastSeen > TIMEOUT) {
      const card = machine.card;
      
      // 🔁 Appliquer l'animation de sortie
      card.style.animation = 'futuristicExit 0.7s forwards'; // ou 'glitchExit'
      
      // ⏳ Supprimer après la durée de l’animation
      setTimeout(() => {
        if (card.parentNode) {
          card.parentNode.removeChild(card);
        }
        delete machines[hostname];
        console.log(`❌ Machine "${hostname}" retirée pour inactivité`);
        updateAgentCount();
      }, 700); // Correspond à la durée de l'animation
    }
  }
}, 2000);

