
    function toggleCardSize() {
        const card = document.getElementById("process-info");
        const button = document.getElementById("toggle-button");
        
        // Si la card a la classe 'full-card', on la remet à 'card'
        if (card.classList.contains("hover-card")) {
            card.classList.remove("hover-card");
            card.classList.add("full-card");
            button.textContent = "FULL";  // Changer le texte du bouton
        } else {
            // Sinon, on passe à 'full-card'
            card.classList.remove("full-card");
            card.classList.add("hover-card");
            button.textContent = "Réduire";  // Changer le texte du bouton
        }
    }
