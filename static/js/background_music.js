let audio = null;
let musicPlaying = false;

// Fonction pour préparer la musique de fond
function startBackgroundMusic(src, volume = 1) {
    audio = document.createElement('audio');
    audio.src = src;
    audio.loop = true;
    audio.volume = volume;
    audio.style.display = 'none';
    document.body.appendChild(audio);
    console.log('🎧 Musique de fond prête (en pause)');
}

// Préparer l'audio, sans autoplay
startBackgroundMusic('/static/background.mp3', 1);

// Gestion du bouton toggle
const toggleBtn = document.getElementById('toggleMusicBtn');
toggleBtn.addEventListener('click', () => {
    if (!musicPlaying) {
        audio.play().then(() => {
            toggleBtn.textContent = 'Désactiver la musique';
            musicPlaying = true;
            console.log('🎵 Musique activée');
        }).catch(err => {
            console.error('Erreur lors de la lecture :', err);
        });
    } else {
        audio.pause();
        toggleBtn.textContent = 'Activer la musique';
        musicPlaying = false;
        console.log('🔇 Musique désactivée');
    }
});
