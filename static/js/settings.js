
  function settingsButton() {
  const button = document.getElementById("dropdown-settings"); 
  // Si la card a la classe 'full-card', on la remet à 'card'
  if (button.classList.contains("dropdown-content")) {
  button.classList.remove("dropdown-content");
  button.classList.add("show-dropdown-content");
  } else {
  // Sinon, on passe à 'full-card'
  button.classList.remove("show-dropdown-content");
  button.classList.add("dropdown-content");

  }
  }




  

