const terminals = document.getElementById("terminalText");
const messages = [
  "[✓] Initializing system...",
  "[✓] Checking Agent connected .....",
  "[✓] Preparing Data...",
  "[✓] Lauching Multi-monitoring...",

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
      setTimeout(typeWriter, 5); // Délai entre chaque caractère
    } else {
      // Fin de la ligne actuelle, passer à la suivante
      terminals.textContent += "\n";
      indexe++;
      charIndex = 0;
      currentLine = "";
      setTimeout(typeWriter, 50); // Délai avant de passer à la ligne suivante
    }
  } else {
    // Fin du loader après 5 secondes
    setTimeout(() => {
      document.getElementById("loader").style.display = "none";
    }, 1000);
  }
}

// Lancer le loader
window.addEventListener("load", () => {
  typeWriter();
});