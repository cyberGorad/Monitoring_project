
let soundEnabled = true; // Par défaut, le son est activé

// Fonction utilitaire pour jouer un son seulement si autorisé
function playAudio(path) {
if (!soundEnabled) return;
const audio = new Audio(path);
audio.play();
}

// Gestion du bouton toggle
const toggleSoundButton = document.getElementById('toggle-sound');
toggleSoundButton.addEventListener('click', () => {
soundEnabled = !soundEnabled;

// Mettre à jour l'affichage du bouton
toggleSoundButton.innerHTML = soundEnabled ? "🔈 Son: Activé" : "🔇 Vocal desactivated";
});

