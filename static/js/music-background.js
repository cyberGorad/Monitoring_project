let audioQueue = [];
let isPlaying = false;
let soundEnabled = true;

const toggleSoundButton = document.getElementById('toggle-sound');

toggleSoundButton.addEventListener('click', () => {
    soundEnabled = !soundEnabled;
    toggleSoundButton.textContent = soundEnabled ? '🔊 Son Activé' : '🔇 Son Désactivé';
});

function playAudio(src) {
    if (!soundEnabled) return; // Corrigé ici

    audioQueue.push(src);
    playNextAudio();
}

function playNextAudio() {
    if (isPlaying || audioQueue.length === 0) return;

    isPlaying = true;
    const src = audioQueue.shift();

    const audio = new Audio(src);
    audio.play();

    audio.onended = () => {
        isPlaying = false;
        playNextAudio();
    };

    audio.onerror = () => {
        console.error('Erreur lors de la lecture du fichier audio : ' + src);
        isPlaying = false;
        playNextAudio();
    };
}
