
    // Attendre 3 secondes avant de masquer le loader
    window.onload = function() {
        setTimeout(function() {
            // Cacher le loader après 3 secondes
            document.getElementById('loader').style.display = 'none';


            playAudio('/static/bonjour.mp3');
        }, 3000); // Durée du loader en millisecondes (3 secondes)
    };
