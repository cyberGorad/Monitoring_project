
    // Attendre 3 secondes avant de masquer le loader
    window.onload = function() {
        setTimeout(function() {


            playAudio('/static/bonjour.mp3');
        }, 5000); // Durée du loader en millisecondes (3 secondes)
    };
