
  function startVoice() {
    if (!('webkitSpeechRecognition' in window)) {
      alert("Ce navigateur ne supporte pas la reconnaissance vocale.");
      return;
    }

    const recognition = new webkitSpeechRecognition();
    recognition.lang = 'fr-FR';
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;
    document.getElementById('status').textContent = "Écoute en cours...";

    recognition.start();

    recognition.onresult = function(event) {
      const command = event.results[0][0].transcript.toLowerCase().trim();
      document.getElementById('status').textContent = "Command : " + command;
      handleCommand(command);
    };

    recognition.onerror = function(event) {
      document.getElementById('status').textContent = "Error : " + event.error;
    };

    recognition.onend = function() {
      document.getElementById('status').textContent += "finish";
    };
  }

  function handleCommand(cmd) {
    // Détecte "carte ville"
    if (cmd.startsWith("carte")) {
      let ville = cmd.replace("carte", "").trim();
      if (ville) {
        window.location.href = "map.php?location=" + encodeURIComponent(ville);
      }
    }

  // Ouvrir un dossier avec caja
  else if (cmd.includes("ouvre") && cmd.includes("/")) {
    const chemin = cmd.split("ouvre")[1].trim(); // extrait le chemin
    const encodedPath = encodeURIComponent(chemin); // sécurité basique
    fetch(`http://localhost:3000/open-folder?path=${encodedPath}`);
  }

    else if (cmd.includes("monte") || cDmd.includes("haut")) {
      window.scrollBy({ top: -300, behavior: "smooth" });
    }
    else if (cmd.includes("demmarer") || cmd.includes("tableau de bord")) {
      
      window.location.href="%2Fids";
    }

    // Refresh
    else if (cmd.includes("actualise") || cmd.includes("rafraîchis")) {
      location.reload();
    }
      // Retour en arrière
  else if (cmd.includes("retour") || cmd.includes("revenir")) {
    window.history.back(); // Commande navigateur native
  }

    // Aide
    else if (cmd.includes("aide")) {
      alert("Commandes disponibles :\n- carte [ville]\n- monte / descends\n- actualise\n- aide");
    }

    else {
      alert("Commande non reconnue : " + cmd);
    }



    
  }


