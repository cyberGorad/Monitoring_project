const terminals = document.getElementById("terminalText");
const messages = [
  "[✓] Initializing system...",
  "[✓] Server connected successfully...",
  "[✓] Loading Data...",
  "[✓] Alls data Ready is Ready",
  "[✓] Launching Gorad System..."
];

let indexe = 0;
let charIndex = 0;
let currentLine = "";

function typeWriter() {
  if (indexe < messages.length) {
    if (charIndex < messages[indexe].length) {
      currentLine += messages[indexe].charAt(charIndex);
      terminals.textContent = messages.slice(0, indexe).join("\n") + "\n" + currentLine;
      charIndex++;
      setTimeout(typeWriter, 30); // Délai entre chaque caractère
    } else {
      // Fin de la ligne actuelle, passer à la suivante
      terminals.textContent += "\n";
      indexe++;
      charIndex = 0;
      currentLine = "";
      setTimeout(typeWriter, 500); // Délai avant de passer à la ligne suivante
    }
  } else {
    // Fin du loader après 5 secondes
    setTimeout(() => {
      document.getElementById("loader").style.display = "none";
    }, 5000);
  }
}

// Lancer le loader
window.addEventListener("load", () => {
  typeWriter();
});