
function etablishedFunction() {
    const card = document.getElementById("connections-info");
    const button = document.getElementById("connection-button");
    
    // Si la card a la classe 'full-card', on la remet à 'card'
    if (card.classList.contains("card")) {
        card.classList.remove("card");
        card.classList.add("hover-card");
        button.innerHTML = '<i class="fas fa-expand" title="agrandir" style="font-size:14px;"></i>'; 
    } else {
        // Sinon, on passe à 'full-card'
        card.classList.remove("hover-card");
        card.classList.add("card");
        button.innerHTML = '<i class="fas fa-compress" title="Réduire" style="font-size:14px;"></i>'; 
    }
}
