

let audioQueue = [];
let isPlaying = false;

function playAudio(src) {
    audioQueue.push(src); // Ajoute le son à la file d'attente
    playNextAudio();
}

function playNextAudio() {
    if (isPlaying || audioQueue.length === 0) {
        return; // Un son est déjà en cours de lecture ou la file est vide
    }

    isPlaying = true;
    const src = audioQueue.shift(); // Récupère et supprime le premier élément de la file

    const audio = new Audio(src);
    audio.play();

    audio.onended = () => {
        isPlaying = false;
        playNextAudio(); // Joue le son suivant
        audio.remove();//supprime l'element audio du dom
    };

    audio.onerror = () => {
        console.error('Erreur lors de la lecture du fichier audio : ' + src);
        isPlaying = false;
        playNextAudio(); // Passe au son suivant même en cas d'erreur
        audio.remove();//supprime l'element audio du dom
    };
}