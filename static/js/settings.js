const homeBtn = document.getElementById('home_btn');
const modal = document.getElementById('modal');
const closeBtn = document.getElementById('close_modal');

homeBtn.addEventListener('click', (e) => {
  e.preventDefault(); // empêche le href de recharger la page
  modal.classList.remove('hidden');
});

closeBtn.addEventListener('click', () => {
  modal.classList.add('hidden');
});

window.addEventListener('click', (e) => {
  if (e.target === modal) {
    modal.classList.add('hidden'); // clic en dehors du contenu
  }
});
