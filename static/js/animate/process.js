
    function ProcessFunction() {
        const card = document.getElementById("process-info");
        const button = document.getElementById("toggle-button");
        
        // Si la card a la classe 'full-card', on la remet à 'card'
        if (card.classList.contains("hover-card")) {
            card.classList.remove("hover-card");
            card.classList.add("full-card");
            button.innerHTML = '<i class="fas fa-expand" title="agrandir" style="font-size:14px;"></i>'; 
        } else {
            // Sinon, on passe à 'full-card'
            card.classList.remove("full-card");
            card.classList.add("hover-card");
            button.innerHTML = '<i class="fas fa-compress" title="Réduire" style="font-size:14px;"></i>'; 
        }
    }
