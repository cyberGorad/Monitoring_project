


// WebSocket initialization
const socket = new WebSocket('ws://0.0.0.0:8000/ws/monitor/');



    socket.onmessage = function (e) {
        const data = JSON.parse(e.data);

        switch (data.type) {
            case "cpu":
                    // Sélection de l'élément HTML où afficher l'utilisation du CPU
                const cpuTextElement = document.getElementById('cpu-text');
                const diskTextElement = document.getElementById('disk-text');
                const ramTextElement = document.getElementById('ram-text');
                const uptimeTextElement = document.getElementById('uptime-text');
                const cpuUsage = data.cpu_usage;
                const diskUsage = data.disk_usage;
                const ramUsage = data.ram_usage;
                const uptime = data.uptime;
                cpuTextElement.textContent = `CPU : ${cpuUsage}%`;
                diskTextElement.textContent = `Disque: ${diskUsage}%`;
                ramTextElement.textContent = `RAM: ${ramUsage}%`;
                uptimeTextElement.textContent = `UPTIME: ${uptime}`;

                if (cpuUsage > 80) {
                    cpuTextElement.style.color = "red";
                } 
                else {
                    cpuTextElement.style.color = "green";
                }

                if (diskUsage >80) {
                    diskTextElement.style.color = "red";
                } else {
                    diskTextElement.style.color = "green";
                }
                if (ramUsage > 80) {
                    ramTextElement.style.color = "red";

                } else {
                    ramTextElement.style.color = "green";
                }

                break;
    




            case "ports":
// Mise à jour de la liste des ports ouverts
            const openPortsList = document.getElementById('open-ports');
            openPortsList.innerHTML = '';
            data.open_ports.forEach(port => {
                const li = document.createElement('li');
                li.innerHTML = `
                <i class="fas fa-plug" style="color: #4CAF50; margin-right: 8px;"></i> 
                Port ${port.port} (PID: ${port.pid}) - Process: ${port.process}
            `;
                openPortsList.appendChild(li);
            });

            // Mise à jour de la liste des ports non autorisés
            const unauthorizedPortsList = document.getElementById('unauthorized-ports');
            unauthorizedPortsList.innerHTML = '';

            data.alerts.forEach(alert => {
                const alertDiv = document.createElement('div');
                alertDiv.classList.add('alert');
                alertDiv.textContent = `Unauthorized port: ${alert.port} (PID: ${alert.pid}) - Process: ${alert.process}`;

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

                // Mettre à jour le machine_id
                machineIdElement.innerHTML = `<i class="fas fa-server"></i> Server address: ${data.machine_id}`;

                
                // Nettoyer la liste des connexions
                connectionsList.innerHTML = '';
                if (data.connections.length === 0) {
                    const offlineMessage = document.createElement('li');
                    offlineMessage.textContent = 'Offline';
                    offlineMessage.style.color = 'red';
                    connectionsList.appendChild(offlineMessage);
                } else {
                    data.connections.forEach(conn => {
                        const li = document.createElement('li');
                        li.textContent = `IP: ${conn.ip} - Hostname: ${conn.hostname}`;
                        connectionsList.appendChild(li);
                    });
                }
                break;


                
                case "startup_info":
                    const startupContainer = document.getElementById('startup-info');
                    startupContainer.innerHTML = ''; // Reset le container à chaque update
                
                    // Ajoute l'OS détecté
                    const osHeader = document.createElement('h3');
                    osHeader.innerHTML = `<i class="fas fa-desktop"></i> Système : ${data.os}`;
                    startupContainer.appendChild(osHeader);
                
                    const dataList = document.createElement('ul');
                    for (const key in data.data) {
                        const item = document.createElement('li');
                
                        // Formatage lisible
                        const formattedKey = key.replace(/_/g, ' ').toUpperCase();
                
                        item.innerHTML = `<strong>${formattedKey}:</strong><pre>${data.data[key]}</pre>`;
                        dataList.appendChild(item);
                    }
                
                    startupContainer.appendChild(dataList);
                    break;
                





            case "bandwidth":
                const bandwidthContainer = document.getElementById('bandwidth-container');
                const bandwidthInfo = document.getElementById('bandwidth-info');
                const dosElement = document.getElementById('dos');  // Sélectionne l'élément dos
                
            // Mise à jour des informations de la bande passante
            bandwidthInfo.innerHTML = `
                <div class="bandwidth-info-row">
                    <span><i class="fas fa-arrow-up"></i> ${data.sent} KB</span>
                    <span><i class="fas fa-arrow-down"></i>${data.received} KB</span>
                    <span><i class="fas fa-tachometer-alt"></i> Total: ${data.total} KB</span>
                </div>
            `;

            // Style pour formater les informations de bande passante
            const style = document.createElement('style');
            style.innerHTML = `
                .bandwidth-info-row {
                    display: flex;
                    flex-direction:column;
                    justify-content: center;
                    align-items:center;
                    margin-bottom: 15px;
                    font-size: 16px;
                    color: #ffffff; /* Couleur du texte pour tout le bloc */
                }
                .bandwidth-info-row span {
                    margin-right: 20px;
                    text-align: left;
                }
                .bandwidth-info-row i {
                    margin-right: 5px;  /* Espacement entre l'icône et le texte */
                    color: #00ff00;  /* Icônes en vert pour uniformité */
                }
                .bandwidth-info-row span:first-child {
                    color: #4CAF50; /* Couleur verte pour "Sent" */
                }
                .bandwidth-info-row span:nth-child(2) {
                    color: #2196F3; /* Couleur bleue pour "Received" */
                }
                .bandwidth-info-row span:last-child {
                    color: #FFEB3B; /* Couleur jaune pour "Total" */
                }
            `;
            document.head.appendChild(style);



            if (data.total > 10000) {
                // Affiche une alerte sur l'élément dos en rouge
            
                dosElement.textContent = "Warning commander: ATTACK DETECTED !";
                dosElement.style.color = 'red';
                dosElement.style.fontSize = '15px';
                playAudio('/static/flood.mp3');
            } else {
                // Affiche normalement si le seuil de 7000 KB n'est pas dépassé
                dosElement.textContent = " normal.";
                dosElement.style.color = 'green';  // Ou la couleur par défaut que vous souhaitez
            }
            break;





            case "outbound_traffic":
                const outboundContainer = document.getElementById('outbound-container');
                outboundContainer.innerHTML = ""; // Nettoie avant de réafficher
            
                if (data.connections && data.connections.length > 0) {
                    data.connections.forEach((connection, index) => {
                        const totalTraffic = connection.packets_sent + connection.packets_received;
            
                        const connectionDiv = document.createElement('div');
                        connectionDiv.classList.add('connection-item');
            
                        connectionDiv.innerHTML = `
                            <div class="connection-row">
                                <span><strong class="connection-title">${index + 1} </strong></span>
                                <span><i class="fas fa-cogs"></i> ${connection.process}</span>
                                <span><i class="fas fa-globe"></i> Dest: ${connection.remote_address}</span>
                                <span><i class="fas fa-exchange-alt"></i> Proto: ${connection.protocol}</span>
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
                                font-size: 14px;
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
                        `;
                        document.head.appendChild(style);
            
                        outboundContainer.appendChild(connectionDiv);
                    });
                } else {
                    outboundContainer.innerHTML = "<p>No outbound traffic detected.</p>";
                }
                break;
            








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
                    noCronMessage.textContent = `${getFormattedDate()} - monitoring ...`; // Ajouter la date et l'heure au message "monitoring ..."
                    noCronMessage.style.color = 'green';
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
                'x-apikey': 'b36cecf797239b46e00bb9d17c71573ddfd3ccd2d345076dfcae0c23a3c7e20e', // Remplacez par votre clé API
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
