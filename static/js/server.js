// server.js
const express = require("express");
const { exec } = require("child_process");
const app = express();
const port = 3000;

app.get("/open-folder", (req, res) => {
  const folderPath = decodeURIComponent(req.query.path);
  exec(`caja "${folderPath}"`, (err) => {
    if (err) {
      console.error("Erreur :", err);
      res.status(500).send("Erreur lors de l'ouverture du dossier.");
    } else {
      res.send("Dossier ouvert !");
    }
  });
});

app.listen(port, () => {
  console.log(`Serveur lancé sur http://localhost:${port}`);
});
