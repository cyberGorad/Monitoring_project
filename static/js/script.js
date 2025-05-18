function evaluateSystemState(cpu, ram, disks, bandwidth = null) {
    let score = 0;
    let statusDetails = {};
    let overallStatusText;
    // Analyse CPU
    if (cpu < 50) {
        score += 1;
    } else if (cpu < 80) {
        score += 0.5;
    } else {
        score -= 1;
    }

    // Analyse RAM
    if (ram < 50) {
        score += 1;
    } else if (ram < 80) {
        score += 0.5;
    } else {
        score -= 1;
    }

    // Analyse DISQUE
    if (disks && typeof disks === "object" && Object.keys(disks).length > 0) {
        const values = Object.values(disks);
        const avg = values.reduce((a, b) => a + b, 0) / values.length;
        if (avg < 50) {
            score += 1;
        } else if (avg < 80) {
            score += 0.5;
        } else {
            score -= 1;
        }
    } else {
        score -= 1; // Pénalise si pas de données disque
    }

    let overallIcon;
    let overallColor;
    // Évaluation finale avec les icônes et le texte
    if (score >= 2.5) {
        overallIcon = "fa-leaf";
        overallColor = "green";
        overallStatusText = "Good";
    } else if (score >= 1) {
        overallIcon = "fa-lightbulb"; // Icône d'ampoule pour l'inspiration orange
        overallColor = "orange";
        overallStatusText = "Medium";
    } else {
        overallIcon = "fa-skull-crossbones";
        overallColor = "red";
        overallStatusText = "Critical";
    }

    return {
        overall: { icon: overallIcon, color: overallColor, text: overallStatusText },
        details: statusDetails
    };
}



// WebSocket initialization
let socket;
let reconnectInterval = 5000; // 5 secondes avant de retenter

function connectWebSocket() {
    socket = new WebSocket('ws://192.168.43.226:8000/ws/monitor/');

    socket.onopen = () => {
        console.log('%c[+] WebSocket connected', 'color: lime');
    };

    socket.onmessage = (event) => {
        console.log('%c[DATA]', 'color: cyan', event.data);
        // Traite tes données ici
    };

    socket.onerror = (error) => {
        console.error('%c[!] WebSocket error:', 'color: red', error);
    };

    socket.onclose = (event) => {
        console.warn('%c[-] WebSocket closed. Retrying in 5 seconds...', 'color: orange');
        setTimeout(connectWebSocket, reconnectInterval);
    };
}

// Démarrage initial
connectWebSocket();




function sendIP() {
    const ip = document.getElementById("ip-input").value.trim();

    if (!ip) {
        alert("Adresse IP invalide.");
        return;
    }

    const payload = {
        type: "add_ip",   // type attendu dans consumers.py
        ip: ip
    };

    if (socket && socket.readyState === WebSocket.OPEN) {
        socket.send(JSON.stringify(payload));
        console.log('%c[>] IP envoyée au backend: ' + ip, 'color: gold');
    } else {
        alert("WebSocket non connecté.");
    }
}


function setDefaultPolicy() {
    socket.send(JSON.stringify({
        type: "set_policy"
    }));
}





socket.onmessage = function (e) {
    const data = JSON.parse(e.data);

    switch (data.type) {


        case "firewall_status":
            const firewallStatus = document.getElementById("firewall-status");
            const status = data.iptables;
            firewallStatus.textContent = `${status}`;



        case "rubber_ducky":
            const typerElement = document.getElementById("typer-alert");
            const typerAlert = data.message;
            const botTime = data.timestamp;

            // Crée un nouvel élément <div> ou <li> pour chaque alerte
            const alertItem = document.createElement("div"); // ou "li" si tu veux une <ul>
            alertItem.textContent = ` ${typerAlert}`;

            // Ajoute au conteneur
            typerElement.appendChild(alertItem);




        case "unauthorized_processes_alert":
            const alertProcess = document.getElementById("unauthorised_process");
            const alert = data.processes;

            // Option 1: Utilisation de JSON.stringify pour afficher l'objet complet
            alertProcess.textContent = JSON.stringify(alert, null, 2);  // Formatage pour une meilleure lisibilité

            // Option 2: Affichage d'informations spécifiques sur les processus
            alertProcess.innerHTML = '';  // Réinitialiser le contenu
            alert.forEach(process => {
                const processInfo = document.createElement('div');
                processInfo.textContent = `PID: ${process.pid}, Name: ${process.name}, Status: ${process.status}`;
                processInfo.style.color = "red";
                processInfo.style.fontSize = "10px";
                alertProcess.appendChild(processInfo);
            });
            break;





        case "cpu":
            // HEADER COLOR SELECTION
            const headerStatus = document.getElementById("head-status");
            // Sélection de l'élément HTML où afficher l'état du système (sera l'icône)
            const systemStatus = document.getElementById("system_status");

            const cpuTextElement = document.getElementById('cpu-text');
            const ramTextElement = document.getElementById('ram-text');
            const uptimeTextElement = document.getElementById('uptime-text');
            const cpuUsage = data.cpu_usage;
            const ramUsage = data.ram_usage;
            const diskUsage = data.disk_usage;
            const bandwidthUsage = data.bandwidth_usage;
            const uptime = data.uptime;
            cpuTextElement.textContent = `CPU  ${cpuUsage}%`;
            ramTextElement.textContent = `RAM ${ramUsage}%`;
            uptimeTextElement.textContent = `UPTIME ${uptime}`;

            const state = evaluateSystemState(cpuUsage, ramUsage, diskUsage, bandwidthUsage);
            // systemStatus.textContent = `${state}`; // Supprimer l'affichage du texte

            if (cpuUsage > 80) {
                cpuTextElement.style.color = "red";
            }
            else if (cpuUsage >= 60 && cpuUsage < 80) {
                cpuTextElement.style.color = "orange";
            } else {
                cpuTextElement.style.color = "green";
            }


            if (ramUsage > 80) {
                ramTextElement.style.color = "red";

            } else if (ramUsage >= 60 && ramUsage < 80) {
                ramTextElement.style.color = "orange";
            } else {
                ramTextElement.style.color = "green";
            }



            /* COLOR FOR SYSTEM STATUS (ICON) */


            if (state && state.overall && state.overall.icon && state.overall.color && state.overall.text) {
                systemStatus.innerHTML = `<i class="fas ${state.overall.icon}" style="color: ${state.overall.color}; margin-right: 5px;"></i> <span style="color: ${state.overall.color};">${state.overall.text}</span>`;
                headerStatus.style.boxShadow = `0 5px 5px ${state.overall.color}`;
            } else {
                systemStatus.textContent = "N/A";
                headerStatus.style.boxShadow = "none";
            }

            break;







        case "all_process":
            const processElement = document.getElementById("process");
            const newProcessDetails = data.processes;
            window.currentVisibleProcessDetails = newProcessDetails;

            // Injecter CSS une seule fois
            if (!document.getElementById("process-style")) {
                const style = document.createElement("style");
                style.id = "process-style";
                style.innerHTML = `
                            .process-table {
                                width: 100%;
                                border-collapse: collapse;
                                font-family: "Courier New", monospace;
                                font-size: 10px;
                                box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                            }
                            .process-table th, .process-table td {
                                border: 1px solid #ccc;
                                padding: 8px 10px;
                                text-align: center;
                                word-break: break-word;
                            }
                            .process-table th {
                                color: #fff;
                                text-transform: uppercase;
                                font-size: 12px;
                            }
                            .process-table tr:hover {
                                background-color: black;
                                color:#00ff00;
                            }
                            .process-table td:last-child {
                                font-weight: bold;
                                color: red;
                            }
                            .search-input {
                                width: 100%;
                                padding: 8px;
                                margin-bottom: 10px;
                                font-size: 12px;
                                font-family: monospace;
                                background: #111;
                                color: #0f0;
                                border: 1px solid #444;
                            }
                            .analyze-button {
                                padding: 8px 16px;
                                background-color: black;
                                color: lime;
                                border: 1px solid #0f0;
                                cursor: pointer;
                                font-family: monospace;
                                margin-bottom: 10px;
                            }
                            .modal {
                                display: none;
                                position: fixed;
                                z-index: 999;
                                left: 0; top: 0;
                                width: 100%; height: 100%;
                                overflow: auto;
                                background-color: rgba(0, 0, 0, 0.9);
                            }
                            .modal-content {
                                background-color: #111;
                                margin: 10% auto;
                                padding: 20px;
                                border: 1px solid #0f0;
                                width: 90%;
                                max-width: 800px;
                                color: #0f0;
                                font-family: monospace;
                                font-size: 14px;
                                white-space: pre-wrap;
                                position: relative;
                            }
                            .close {
                                color: red;
                                position: absolute;
                                right: 10px;
                                top: 10px;
                                font-size: 28px;
                                font-weight: bold;
                                cursor: pointer;
                            }
                        `;
                document.head.appendChild(style);
            }



            // Vérifier et afficher l'alerte pour les processus multiples
            const processNameCounts = {};
            newProcessDetails.forEach(p => {
                processNameCounts[p.name] = (processNameCounts[p.name] || 0) + 1;
            });

            const multipleProcessNames = Object.keys(processNameCounts).filter(name => processNameCounts[name] > 7);

            let alertDiv = document.getElementById("multiple-process-alert");
            if (multipleProcessNames.length > 0) {
                if (!alertDiv) {
                    alertDiv = document.createElement("div");
                    alertDiv.id = "multiple-process-alert";
                    alertDiv.classList.add("alert-message");
                    alertDiv.style.fontSize = "10px";
                    alertDiv.style.color = "red";
                    processElement.insertBefore(alertDiv, processElement.firstChild); // Afficher en haut
                }
                alertDiv.textContent = `ALERT : Multiple Process found : ${multipleProcessNames.map(name => `${name}`).join(', ')}. `;
            } else if (alertDiv) {
                alertDiv.remove(); // Supprimer l'alerte si la condition n'est plus remplie
            }



            // Ajout zone input et bouton
            if (!document.getElementById("process-search-input")) {
                const input = document.createElement("input");
                input.id = "process-search-input";
                input.type = "text";
                input.placeholder = "search..";
                input.classList.add("search-input");
                // Style direct intégré
                input.style.display = "block";
                input.style.position = "relative";
                input.style.left = "20px";
                input.style.width = "20%";
                input.style.padding = "6px 12px";
                input.style.fontSize = "10px";
                input.style.borderRadius = "6px";
                input.style.backgroundColor = "#0a0a0a";
                input.style.color = "#00FFOO";
                input.style.fontFamily = "Orbitron, monospace";
                input.addEventListener("input", () => {
                    const filter = input.value.toLowerCase();
                    const rows = document.querySelectorAll("#live-process-table tr:not(:first-child)");
                    rows.forEach(row => {
                        const nameCell = row.cells[1];
                        row.style.display = nameCell && nameCell.textContent.toLowerCase().includes(filter) ? "" : "none";
                    });
                });
                processElement.appendChild(input);
            }

            if (!document.getElementById("process-analyze-button")) {
                const button = document.createElement("button");
                button.id = "process-analyze-button";
                button.textContent = "AI SCAN";
                button.style.float = "right";
                button.style.marginTop = "-50px";
                button.style.position = "position";
                button.classList.add("analyze-button")
                button.addEventListener("click", async () => {
                    const details = window.currentVisibleProcessDetails;
                    if (!details || !details.length) return alert("Aucun processus à analyser");
                    const originalText = button.textContent;
                    button.textContent = "SCAN IN PROGRESS...";
                    button.disabled = true;

                    const processData = details.map(p =>
                        `- PID: ${p.pid}, Nom: ${p.name}, RAM: ${p.memory_mb}MB (${p.memory_percent}%), Alerte active: ${p.alert ? 'Oui' : 'Non'}`
                    ).join('\n');




                    const promptText = `
                Agis en tant qu'analyste système expert. Analyse les processus suivants :
                ${processData}
                Tu es un agent de maintenance IA dans un IDS. Si le système est lent, propose une commande shell à exécuter pour libérer la mémoire ou CPU. Retourne uniquement les commandes bash sans explication.
                `;

                    const apiKey = "AIzaSyDUzu9hIkc6hfh5GGZUjov8V8BMgK6yDgg";
                    const response = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=${apiKey}`, {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ contents: [{ parts: [{ text: promptText }] }] }),
                    });

                    const data = await response.json();
                    const content = data?.candidates?.[0]?.content?.parts?.[0]?.text || "Analyse non disponible";

                    const modal = document.getElementById("modal") || (() => {
                        const m = document.createElement("div");
                        m.id = "modal";
                        m.className = "modal";
                        button.textContent = "SCAN";
                        button.disabled = false;
                        m.innerHTML = `
                                    <div class="modal-content">
                                        <span class="close">&times;</span>
                                        <h2>Result</h2>
                                        <pre id="modal-analysis-text">Chargement...</pre>
                                    </div>`;
                        document.body.appendChild(m);
                        m.querySelector(".close").onclick = () => m.style.display = "none";
                        m.onclick = e => { if (e.target === m) m.style.display = "none"; };
                        return m;

                    })();

                    document.getElementById("modal-analysis-text").textContent = content;
                    modal.style.display = "block";
                });
                processElement.appendChild(button);






            }

            // Table
            let wrapper = document.getElementById("process-table-wrapper");
            if (!wrapper) {
                wrapper = document.createElement("div");
                wrapper.id = "process-table-wrapper";
                processElement.appendChild(wrapper);
            }
            wrapper.innerHTML = "";

            const table = document.createElement("table");
            table.id = "live-process-table";
            table.className = "process-table";
            table.innerHTML = `
                        <tr>
                            <th>PID</th><th>Name</th><th>RAM (MB)</th><th>% RAM</th><th>⚠️</th>
                        </tr>
                    `;
            newProcessDetails.forEach(p => {
                const row = document.createElement("tr");
                if (p.alert) {
                    row.style.backgroundColor = "darkred";
                    row.style.color = "white";
                }
                row.innerHTML = `
                            <td>${p.pid}</td>
                            <td>${p.name.replace(/</g, "&lt;").replace(/>/g, "&gt;")}</td>
                            <td>${p.memory_mb}</td>
                            <td>${p.memory_percent}</td>
                            <td>${p.alert ? "⚠️" : ""}</td>
                        `;
                table.appendChild(row);
            });
            wrapper.appendChild(table);








            let canvas = document.getElementById("process-chart-canvas");
            const ct = canvas.getContext("2d");

            // Canvas encore plus grand pour meilleure visibilité
            canvas.width = 4200;
            canvas.height = 1500;

            const backgroundColor = "transparent";
            const axisColor = "#5a6a7a";
            const gridColor = "#2a3a4a";
            const barColorStart = "#00d2ff";
            const barColorEnd = "#3a9bdc";
            const alertBarColor = "#ff5555";
            const textColor = "#00ff00";
            const titleColor = "#00ff00";

            function drawFutureVerticalBarChart(processes) {
                ct.clearRect(0, 0, canvas.width, canvas.height);
                ct.fillStyle = backgroundColor;
                ct.fillRect(0, 0, canvas.width, canvas.height);
                ct.lineWidth = 3;

                if (!processes || processes.length === 0) {
                    ct.fillStyle = textColor;
                    ct.font = "140px Orbitron, monospace";
                    ct.textAlign = "center";
                    ct.fillText("No data to show", canvas.width / 2, canvas.height / 2);
                    return;
                }

                const topProcesses = processes
                    .filter(p => p.memory_mb > 0)
                    .sort((a, b) => b.memory_mb - a.memory_mb)
                    .slice(0, 10);

                if (topProcesses.length === 0) {
                    ct.fillStyle = textColor;
                    ct.font = "140px Orbitron, monospace";
                    ct.textAlign = "center";
                    ct.fillText("No higher process", canvas.width / 2, canvas.height / 2);
                    return;
                }

                const padding = 300; // Padding augmenté pour éviter superposition
                const chartWidth = canvas.width - 2 * padding;
                const chartHeight = canvas.height - 2 * padding;
                const barPadding = 100; // Espacement plus large entre barres
                const numBars = topProcesses.length;
                const barWidth = (chartWidth - (numBars - 1) * barPadding) / numBars;
                const maxMemory = Math.max(...topProcesses.map(p => p.memory_mb), 0);

                if (maxMemory === 0) {
                    ct.fillStyle = textColor;
                    ct.font = "140px Orbitron, monospace";
                    ct.textAlign = "center";
                    ct.fillText("This Process use 0 MB of RAM", canvas.width / 2, canvas.height / 2);
                    return;
                }


                // Axe X
                ct.beginPath();
                ct.moveTo(padding, canvas.height - padding);
                ct.lineTo(canvas.width - padding, canvas.height - padding);
                ct.strokeStyle = axisColor;
                ct.stroke();

                topProcesses.forEach((p, index) => {
                    const barHeight = (p.memory_mb / maxMemory) * chartHeight;
                    const x = padding + index * (barWidth + barPadding);
                    const y = canvas.height - padding - barHeight;

                    // Gradient néon vertical plus lumineux
                    const gradient = ct.createLinearGradient(x, y, x, y + barHeight);
                    gradient.addColorStop(0, barColorEnd);
                    gradient.addColorStop(1, barColorStart);

                    ct.shadowColor = p.alert ? "#ff5555" : "#00ffc6";
                    ct.shadowBlur = 30;
                    ct.fillStyle = p.alert ? alertBarColor : gradient;
                    ct.fillRect(x, y, barWidth, barHeight);
                    ct.shadowBlur = 0;

                    // Nom du process horizontal sous la barre, rotation légère (-30°)
                    ct.save();
                    ct.translate(x + barWidth / 2, canvas.height - padding + 130);
                    ct.rotate(-Math.PI / 6); // -30 degrés
                    ct.fillStyle = textColor;
                    ct.font = "80px Orbitron, monospace";
                    ct.textAlign = "right";

                    // Limite dynamique selon la largeur de la barre (adapté au style futuriste)
                    let processName = p.name;
                    const maxTextWidth = barWidth + 80; // Marge pour ne pas dépasser (tu peux ajuster)

                    while (ct.measureText(processName + "…").width > maxTextWidth && processName.length > 0) {
                        processName = processName.slice(0, -1);
                    }
                    if (processName !== p.name) {
                        processName += "…";
                    }

                    ct.fillText(processName, 0, 0);
                    ct.restore();


                    // Valeur mémoire au-dessus de la barre avec glow
                    if (barHeight > 60) {
                        ct.shadowColor = "#00ffc6";
                        ct.shadowBlur = 25;
                        ct.fillStyle = textColor;
                        ct.font = "80px Orbitron, monospace";
                        ct.textAlign = "center";
                        ct.fillText(p.memory_mb.toFixed(1), x + barWidth / 2, y - 60);
                        ct.shadowBlur = 0;
                    }
                });

                // Titre avec glow plus marqué
                ct.shadowColor = "#00ffc6";
                ct.shadowBlur = 35;
                ct.fillStyle = titleColor;
                ct.font = "bold 150px Orbitron, monospace";
                ct.textAlign = "center";
                ct.fillText("Top Processes", canvas.width / 2, 150);
                ct.shadowBlur = 0;
            }
            drawFutureVerticalBarChart(newProcessDetails);



        case "disk":
            const diskTextElement = document.getElementById('disk-text');

            // 🔁 Construction HTML pour les disques avec couleur par usage
            var diskDetails = '';
            for (const [mount, percent] of Object.entries(data.disk_usage)) {
                let color;
                if (percent > 80) {
                    color = 'red';
                } else if (percent >= 60) {
                    color = 'orange';
                } else {
                    color = 'green';
                }

                diskDetails += `<span style="color:${color}">${mount}: ${percent}%</span><br>`;
            }

            diskTextElement.innerHTML = diskDetails;
            break;





        case "usb":
            const usbList = document.getElementById("usb");
            const usbInfo = document.createElement("li");

            usbInfo.innerHTML = `
                                <span style="color: #aaa; font-size: 0.8em;">[${data.timestamp}]</span>
                                <strong style="color: #00ccff;">Action:</strong> <span style="color: #00FF00;">${data.action}</span>,
                                <strong style="color: #00ccff;">Modèle:</strong> <span style="color: #ee;">${data.model}</span>,
                                <strong style="color: #00ccff;">Node:</strong> <span style="color: #ee;">${data.node}</span>
                            `;

            usbInfo.style.cssText = `
                                padding: 8px 12px;
                                margin-bottom: 4px;
                                background-color: #0a0a0a;
                                color: #00FF00;
                                border-left: 4px solid #00FF00;
                                border-radius: 4px;
                                font-family: monospace;
                                font-size: 10px;
                                white-space: nowrap;
                                overflow-X: scroll;
                                text-overflow: ellipsis;
                            `;

            usbList.appendChild(usbInfo);
            break;








        case "ports":
            const openPortsList = document.getElementById('open-ports');
            openPortsList.innerHTML = ''; // Effacer la liste existante

            // Créer l'élément d'en-tête s'il n'existe pas
            let headerLi = openPortsList.querySelector('.ports-header');
            if (!headerLi) {
                headerLi = document.createElement('li');
                headerLi.classList.add('ports-header');
                headerLi.style.cssText = `
                                        padding: 2px 15px 2px 15px;
                                        margin-bottom: 1px;
                                        color: #fff;
                                        background-color: black;
                                        border-bottom: 2px solid #00FF00;
                                        border-radius: 4px 4px 0 0;
                                        font-family: 'Courier New', monospace;
                                        font-size: 8px;
                                        display: flex;
                                        align-items: center;
                                        justify-content: space-between;
                                        font-weight: bold;
                                    `;

                const portHeaderSpan = document.createElement('span');
                portHeaderSpan.style.textAlign = 'left';
                portHeaderSpan.textContent = 'Port';

                const pidHeaderSpan = document.createElement('span');
                pidHeaderSpan.style.textAlign = 'center';
                pidHeaderSpan.textContent = 'PID';

                const processHeaderSpan = document.createElement('span');
                processHeaderSpan.style.textAlign = 'right';
                processHeaderSpan.textContent = 'Process';

                headerLi.appendChild(portHeaderSpan);
                headerLi.appendChild(pidHeaderSpan);
                headerLi.appendChild(processHeaderSpan);
                openPortsList.appendChild(headerLi);
            }

            data.open_ports.forEach(port => {
                const li = document.createElement('li');
                li.style.cssText = `
                                        padding: 6px 10px;
                                        margin: 4px 0;
                                        color: #00FF00;
                                        background-color: #0a0a0a;
                                        border-left: 4px solid #00FF00;
                                        border-radius: 4px;
                                        font-family: 'Courier New', monospace;
                                        font-size: 11px;
                                        display: flex;
                                        align-items: center;
                                        justify-content: space-between;
                                        box-shadow: 0 0 5px #00FF00;
                                    `;

                const portSpan = document.createElement('span');
                portSpan.style.textAlign = 'left';
                portSpan.textContent = `${port.port}`;

                const pidSpan = document.createElement('span');
                pidSpan.style.textAlign = 'center';
                pidSpan.style.color = '#00ccff';
                pidSpan.textContent = `${port.pid}`;

                const processSpan = document.createElement('span');
                processSpan.style.textAlign = 'right';
                processSpan.style.color = '#ff00ff';
                processSpan.textContent = port.process;

                li.appendChild(portSpan);
                li.appendChild(pidSpan);
                li.appendChild(processSpan);

                openPortsList.appendChild(li);
            });



            // Mise à jour de la liste des ports non autorisés
            const unauthorizedPortsList = document.getElementById('unauthorized-ports');
            unauthorizedPortsList.innerHTML = '';

            data.alerts.forEach(alert => {
                const alertDiv = document.createElement('div');
                alertDiv.classList.add('alert');
                alertDiv.textContent = `⚠️ Unauthorized Port ${alert.port} -  ${alert.pid} ${alert.process}`;
                alertDiv.style.cssText = `
                        background-color: #2c0b0e;
                        color: #f28b82;
                        padding: 8px 12px;
                        margin: 6px 0;
                        border-left: 4px solid #ff1744;
                        border-radius: 4px;
                        font-family: monospace;
                        font-size: 10px;
                    `;


                // Sélectionner l'image existante
                const existingImage = document.querySelector('img[src="/static/IA.jpeg"]');

                if (existingImage) {
                    // Cloner l'image existante pour ne pas la modifier dans le DOM global
                    const imgClone = existingImage.cloneNode(true);
                    imgClone.style.cursor = 'pointer'; // S'assurer que l'image est cliquable

                    // Ajouter l'événement de clic pour afficher la réponse de Gemini
                    imgClone.onclick = () => {
                        // Recherche de la réponse de Gemini pour ce port
                        const geminiResponse = data.alert_responses.find(res => res.port === alert.port);

                        const modal = document.getElementById('gemini-modal');
                        const responseText = document.getElementById('gemini-response-text');

                        if (geminiResponse) {
                            responseText.textContent = geminiResponse.response;

                        } else {
                            responseText.textContent = "Gora is offline , check your connection Internet";
                        }

                        // Afficher la modale
                        modal.style.display = "flex";
                    };

                    // Ajouter l'image clonée à l'alerte
                    alertDiv.appendChild(imgClone);
                } else {
                    alertDiv.textContent += " (Image non trouvée)";
                }

                // Ajouter l'alerte au conteneur des ports non autorisés
                unauthorizedPortsList.appendChild(alertDiv);

                playAudio('/static/alerte.mp3');
            });

            // Ajouter l'événement de fermeture de la modale
            const closeModal = document.getElementById('close-modal');
            closeModal.onclick = () => {
                const modal = document.getElementById('gemini-modal');
                modal.style.display = "none"; // Masquer la modale
            };

            // Fermer la modale si l'utilisateur clique en dehors de la fenêtre
            window.onclick = (event) => {
                const modal = document.getElementById('gemini-modal');
                if (event.target === modal) {
                    modal.style.display = "none"; // Masquer la modale
                }
            };
            break;


        case "connections":
            const connectionsList = document.getElementById('connections-list');
            const machineIdElement = document.getElementById('machine-id');
            const seenConnections_etablished = new Set(); // Utiliser un Set pour suivre les connexions uniques

            // Mettre à jour l'identifiant de la machine
            if (data.machine_id) {
                machineIdElement.innerHTML = `<i class="fas fa-server"></i> Server address: ${data.machine_id}`;
                machineIdElement.style.color = '#00ff00';
            } else {
                machineIdElement.innerHTML = '<i class="fas fa-server"></i> Offline';
                machineIdElement.style.color = 'red';
            }

            // Nettoyer la liste des connexions
            connectionsList.innerHTML = '';

            if (!data.connections || data.connections.length === 0) {
                const offlineMessage = document.createElement('li');
                offlineMessage.textContent = 'No active connections';
                offlineMessage.style.color = 'orange';
                connectionsList.appendChild(offlineMessage);
            } else {
                data.connections.forEach(conn => {
                    // Créer une clé unique pour identifier une connexion (combinaison IP et hostname)
                    const connectionKey = `${conn.ip}-${conn.hostname}`;

                    // Vérifier si cette connexion a déjà été affichée
                    if (!seenConnections_etablished.has(connectionKey)) {
                        seenConnections_etablished.add(connectionKey); // Ajouter la connexion au Set des connexions vues

                        const li = document.createElement('li');
                        li.innerHTML = `
                                <span style="color: #00ff00;"> ${conn.ip}</span><br>
                                <span style="color: #ff9800;"><i class="fas fa-desktop"></i> ${conn.hostname}</span>
                            `;
                        li.style.cssText = `
                                padding: 8px 12px;
                                margin-bottom: 6px;
                                background-color: #0a0a0a;
                                color: #cfd8dc;
                                border-left: 5px solid #00FF00;
                                border-radius: 6px;
                                font-family: 'Courier New', monospace;
                                font-size: 11px;
                                white-space: nowrap;
                                overflow: hidden;
                                text-overflow: ellipsis;
                            `;
                        connectionsList.appendChild(li);
                    }
                });
            }
            break;





        case "startup_info":
            const startupContainer = document.getElementById('startup-info');
            startupContainer.innerHTML = ''; // Reset le container à chaque update

            // Ajoute l'OS détecté
            const osHeader = document.createElement('h3');
            const toogle = document.createElement('span');
            osHeader.innerHTML = `<i class="fas fa-desktop"></i> System : ${data.os} <button id="startup-button" onmouseover="StartupFunction()" style="float:right;background-color:transparent;border:none;color:white;margin-bottom:30px;"><i class="fas fa-expand" title="Réduire" style="font-size: 14px;"></i></button>`;
            osHeader.style.cssText = `
                        color: #00ffcc;
                        font-family: 'Courier New', Courier, monospace;
                        margin-bottom: 10px;
                        text-shadow: 0 0 5px #00ffcc;
                    `;
            startupContainer.appendChild(osHeader);

            const dataList = document.createElement('ul');
            dataList.style.cssText = `
                        list-style: none;
                        padding: 0;
                        font-family: 'Courier New', Courier, monospace;
                        background-color: #111;
                        border: 1px solid #333;
                        border-radius: 10px;
                        padding: 15px;
                        color: #00ff00;
                        box-shadow: 0 0 15px rgba(0, 255, 204, 0.2);
                    `;

            for (const key in data.data) {
                const item = document.createElement('li');
                item.style.cssText = `
                            margin-bottom: 10px;
                        `;

                const formattedKey = key.replace(/_/g, ' ').toUpperCase();

                item.innerHTML = `<strong style="color:#00ff00">${formattedKey}:</strong><pre style="margin:5px 0 0;padding:5px;background-color:#222;color:#0f0;border-radius:5px;overflow:auto;">${data.data[key]}</pre>`;
                dataList.appendChild(item);
            }

            startupContainer.appendChild(dataList);
            break;






        case "bandwidth":
            const bandwidthContainer = document.getElementById('bandwidth-container');
            const dosElement = document.getElementById('dos');

            // Initialisation du graphe s'il n'existe pas
            if (!window.bandwidthChartInitialized) {
                const canvas = document.createElement('canvas');
                canvas.id = 'bandwidth-canvas';
                canvas.width = 400;
                canvas.height = 150;
                document.getElementById('bandwidth-info').appendChild(canvas);

                const ctx = canvas.getContext('2d');

                window.bandwidthChartData = {
                    labels: [],
                    datasets: [
                        {
                            label: 'Sent',
                            data: [],
                            borderColor: '#4CAF50',
                            borderWidth: 2,
                            fill: false,
                            tension: 0.3,
                            pointRadius: 0
                        },
                        {
                            label: 'Received',
                            data: [],
                            borderColor: '#FF7043',
                            borderWidth: 2,
                            fill: false,
                            tension: 0.3,
                            pointRadius: 0
                        },
                        {
                            label: 'Total',
                            data: [],
                            borderColor: '#2196F3',
                            borderWidth: 2,
                            fill: false,
                            tension: 0.3,
                            pointBackgroundColor: [],
                            pointRadius: [],
                        }
                    ]
                };

                window.bandwidthChart = new Chart(ctx, {
                    type: 'line',
                    data: window.bandwidthChartData,
                    options: {
                        animation: false,
                        plugins: {
                            legend: { display: false }
                        },
                        scales: {
                            x: { display: false },
                            y: { display: false }
                        }
                    }
                });

                window.bandwidthChartInitialized = true;
            }

            const chartData = window.bandwidthChartData;
            const changeThreshold = 2000;  // seuil de changement brusque
            const previousTotal = chartData.datasets[2].data.slice(-1)[0] || 0;
            const delta = Math.abs(data.total - previousTotal);

            chartData.labels.push('');
            chartData.datasets[0].data.push(data.sent);
            chartData.datasets[1].data.push(data.received);
            chartData.datasets[2].data.push(data.total);

            // Pour surbrillance du pic
            chartData.datasets[2].pointBackgroundColor.push(
                delta > changeThreshold ? 'red' : 'transparent'
            );
            chartData.datasets[2].pointRadius.push(
                delta > changeThreshold ? 5 : 0
            );

            if (chartData.labels.length > 20) {
                chartData.labels.shift();
                chartData.datasets.forEach(ds => ds.data.shift());
                chartData.datasets[2].pointBackgroundColor.shift();
                chartData.datasets[2].pointRadius.shift();
            }

            window.bandwidthChart.update();

            // Alerte DoS
            if (data.total > 10000) {
                dosElement.textContent = "Alert High Traffic";
                dosElement.style.color = 'red';
                dosElement.style.fontSize = '15px';
                playAudio('/static/flood.mp3');
            }
            else if (data.total > 100) {
                dosElement.textContent = "Activity on Network";
                dosElement.style.color = 'orange';
                dosElement.style.fontSize = '15px';
            } else {
                dosElement.textContent = "Traffic Normal";
                dosElement.style.color = 'green';
            }

            // Création du bloc texte s'il n'existe pas encore
            let textDiv = document.getElementById('bandwidth-text');
            if (!textDiv) {
                textDiv = document.createElement('div');
                textDiv.id = 'bandwidth-text';
                textDiv.style.marginTop = '10px';
                textDiv.style.color = '#ccc';
                textDiv.style.fontFamily = 'monospace';
                textDiv.style.fontSize = '10px';
                textDiv.style.display = 'flex';
                textDiv.style.justifyContent = 'center';
                textDiv.style.flexBasis = 'column';
                textDiv.style.gap = '5px';
                document.getElementById('bandwidth-info').appendChild(textDiv);
            }

            // Met à jour les valeurs dans le bloc texte
            textDiv.innerHTML = `
                        <span style="color:#4CAF50;">Sent ${data.sent} KB</span> 
                        <span style="color:#FF7043;">Received ${data.received} KB</span> 
                        <span style="color:#2196F3;">Total ${data.total} KB</span>
                    `;

            break;




        case "outbound_traffic":
            const outboundContainer = document.getElementById('outbound-container');
            outboundContainer.innerHTML = ""; // Nettoie avant de réafficher

            let compteur = 1;
            const seenConnections = new Set();

            if (data.connections && data.connections.length > 0) {
                data.connections.forEach((connection) => {
                    const { process, remote_address, remote_port, protocol } = connection;

                    // Ignore process inconnus
                    if (!process || process === "Unknown") return;

                    // Crée une clé unique pour chaque combinaison process + ip + port
                    const uniqueKey = `${process}_${remote_address}_${remote_port}`;

                    if (seenConnections.has(uniqueKey)) return;
                    seenConnections.add(uniqueKey);

                    const connectionDiv = document.createElement('div');
                    connectionDiv.classList.add('connection-item');

                    connectionDiv.innerHTML = `
                                        <div class="connection-row">
                                            <span><strong class="connection-title">${compteur}</strong></span>
                                            <span><i class="fas fa-cogs"></i> ${process}</span>
                                            <span><i class="fas fa-globe"></i> <span class="label">Dest:</span> ${remote_address}</span>
                                            <span><i class="fas fa-exchange-alt"></i> <span class="label">Proto:</span> ${protocol}</span>
                                            <span> ${connection.uptime}</span>
                                        </div>
                                        <hr>
                                    `;







                    // Style en ligne pour les rows
                    const style = document.createElement('style');
                    style.innerHTML = `
                            .connection-row {
                                display: flex;
                                justify-content: space-between;
                                flex-wrap: wrap;
                                margin-bottom: 10px;
                                font-size: 10px;
                                color: #ffffff;
                            }
                            .connection-title {
                                color: #00ff00;
                                font-weight: bold;
                            }
                            .connection-row span {
                                margin-right: 20px;
                                text-align: left;
                            }
                            .connection-row i {
                                margin-right: 5px;
                                color: #00ff00;
                            }
                            hr {
                                margin-top: 10px;
                                border-top: 1px solid #444444;
                            }
                            .label {
                                color: #00FF00;
                                font-weight: bold;
                            }
                            
                        `;
                    document.head.appendChild(style);

                    outboundContainer.appendChild(connectionDiv);
                    compteur++;
                });
            } else {
                outboundContainer.innerHTML = "<p>No outbound traffic detected.</p>";
            }




            // Regroupe le trafic par processus
            const processTrafficMap = {};

            data.connections.forEach((connection) => {
                if (!connection.process || connection.process === "Unknown") return;

                const totalTraffic = connection.packets_sent + connection.packets_received;

                if (processTrafficMap[connection.process]) {
                    processTrafficMap[connection.process] += totalTraffic;
                } else {
                    processTrafficMap[connection.process] = totalTraffic;
                }
            });

            const labels = Object.keys(processTrafficMap);
            const trafficData = Object.values(processTrafficMap);

            const darkHackerColors = [
                '#0f3b21', // vert sombre
                '#1b5e20', // vert foncé intense
                '#00695c', // turquoise foncé
                '#003049', // bleu nuit
                '#0d47a1', // bleu profond
                '#1e3a8a', // bleu indigo dark
                '#4e342e', // marron-noir (base orange)
                '#bf360c', // orange brûlé
                '#ff6f00', // orange foncé
                '#6d4c41', // brun fumé
                '#263238', // noir bleuté
                '#212121', // charbon classique
            ];

            const backgroundColors = labels.map((_, i) => darkHackerColors[i % darkHackerColors.length]);





            const ctx = document.getElementById('outboundTrafficChart').getContext('2d');
            if (window.outboundChart) window.outboundChart.destroy(); // empêche doublons

            window.outboundChart = new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: labels,
                    datasets: [{
                        label: '-',
                        data: trafficData,
                        backgroundColor: backgroundColors,
                        borderColor: 'transparent', // Aucune bordure
                        borderWidth: 0,
                        hoverOffset: 20
                    }]
                },
                options: {
                    responsive: true,
                    backgroundColor: 'transparent', // pas de fond
                    plugins: {
                        legend: {
                            position: 'right', // change la position si besoin
                            labels: {
                                color: '#0ff',
                                boxWidth: 10,
                                padding: 10,
                                font: {
                                    family: 'Orbitron',
                                    size: 8
                                }
                            }
                        },
                        title: {
                            display: true,
                            text: 'Outbound',
                            color: '#0ff',
                            font: {
                                family: 'Orbitron',
                                size: 14
                            }
                        },
                        datalabels: {
                            color: '#fff',
                            font: {
                                family: 'Orbitron',
                                weight: 'bold'
                            },
                            formatter: (value, ctx) => {
                                const total = ctx.chart.data.datasets[0].data.reduce((a, b) => a + b, 0);
                                const percent = ((value / total) * 100);
                                return percent < 10 ? '' : `${percent.toFixed(1)}%`;
                            }
                        }
                    }
                },
                plugins: [ChartDataLabels]

            });











        case "cron_modification":
            const cronDetails = data.message;
            const cronListContainer = document.getElementById('cron-jobs-list');

            // Vérifie si le message "monitoring ..." est déjà dans la liste
            const existingNoCronMessage = Array.from(cronListContainer.children).find(child => child.textContent.includes('monitoring ...'));


            function getFormattedDate() {
                const now = new Date();
                return now.toLocaleString(); // personnalier
            }


            if (cronDetails) {
                const cronJobs = cronDetails.split("\n");
                playAudio('/static/cron.mp3');

                // Supprime l'ancien message "monitoring  si il existe
                if (existingNoCronMessage) {
                    cronListContainer.removeChild(existingNoCronMessage);
                }

                // Afficher cron
                cronJobs.forEach(job => {
                    const li = document.createElement('li');
                    li.textContent = `${getFormattedDate()} - ${job}`; // Ajouter la date et l'heure à chaque cron job
                    li.style.color = "red";
                    cronListContainer.appendChild(li);
                });
            } else {
                // Si aucun cron job trouvé et que le message n'est pas déjà dans la liste
                if (!existingNoCronMessage) {
                    const noCronMessage = document.createElement('li');
                    noCronMessage.textContent = `monitoring ...`; // Ajouter la date et l'heure au message "monitoring ..."
                    noCronMessage.style.color = 'green';
                    noCronMessage.style.listStyleType = 'none';
                    cronListContainer.appendChild(noCronMessage);
                }
            }
            break;

        default:
            console.error('Unknown data type:', data.type);
    }
};





async function scanFile() {
    const fileInput = document.getElementById('file-upload');
    const scanResults = document.getElementById('scan-results');
    if (fileInput.files.length === 0) {
        scanResults.innerHTML = '<p>No file selected.</p>';
        return;
    }

    const file = fileInput.files[0];
    scanResults.innerHTML = `<p>Scanning file: ${file.name}...</p>`;
    playAudio('/static/scan.mp3');

    const formData = new FormData();
    formData.append("file", file);

    try {

        const response = await fetch("https://www.virustotal.com/api/v3/files", {
            method: 'POST',
            headers: {
                'x-apikey': 'b36cecf797239b46e00bb9d17c71573ddfd3ccd2d345076dfcae0c23a3c7e20e', // 
            },
            body: formData,
        });

        if (!response.ok) {
            throw new Error("File upload failed.");
        }

        const data = await response.json();
        const scanId = data.data.id; // Récupérer l'ID du fichier scanné


        await getScanResults(scanId, scanResults);

    } catch (error) {
        scanResults.innerHTML = `<p>Error: ${error.message}</p>`;
        playAudio('/static/error.mp3');
    }
}

//resultat
async function getScanResults(scanId, scanResults) {
    try {
        const response = await fetch(`https://www.virustotal.com/api/v3/analyses/${scanId}`, {
            method: 'GET',
            headers: {
                'x-apikey': 'b36cecf797239b46e00bb9d17c71573ddfd3ccd2d345076dfcae0c23a3c7e20e', // Remplacez par votre clé API
            },
        });

        if (!response.ok) {
            throw new Error("Failed to retrieve scan results.");
        }

        const data = await response.json();
        const scanData = data.data.attributes;

        // Afficher les résultats du scan
        const scanDetails = scanData.stats;
        playAudio('/static/resultat.mp3');
        scanResults.innerHTML = `
            <p>Scan results for file</p>
            <ul>
                <li>Malicious: ${scanDetails.malicious}</li>
                <li>Undetected: ${scanDetails.undetected}</li>
                <li>Harmless: ${scanDetails.harmless}</li>
            </ul>
        `;

    } catch (error) {
        scanResults.innerHTML = `<p>Error: ${error.message}</p>`;
    }
}




// Fonction pour démarrer la musique de fond
function startBackgroundMusic(src, volume = 0.1) {
    const audio = document.createElement('audio');
    audio.src = src;
    audio.loop = true; // La musique tourne en boucle
    audio.volume = volume; // Ajuste le volume (0.0 à 1.0)
    audio.autoplay = true; // Démarre automatiquement
    audio.style.display = 'none'; // Cache l'élément audio pour un rendu propre

    // Ajout à la page
    document.body.appendChild(audio);

    // Facultatif : Afficher un contrôle si besoin
    console.log('Musique de fond en cours de lecture.');
}

// Appeler la fonction avec la source de votre musique et le volume
startBackgroundMusic('/static/background.mp3', 0.1);










