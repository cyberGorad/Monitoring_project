const modal = document.getElementById('modal');
const closeBtn = document.querySelector('.close-btn');

closeBtn.addEventListener('click', () => {
  modal.classList.add('fade-out'); // 🔁 Joue l’animation

  setTimeout(() => {
    modal.classList.add('hidden'); // 🫥 Cache après l'animation
    modal.classList.remove('fade-out'); // reset pour la prochaine ouverture
  }, 400); // ⏳ même durée que l'animation
});
