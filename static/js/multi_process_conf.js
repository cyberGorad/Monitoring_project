function sendProcessmultiConfig() {
    const input = document.getElementById("uploadProcessJson");
    const file = input.files[0];
    if (!file) return alert("No file selected");

    const reader = new FileReader();
    reader.onload = function (e) {
        const content = e.target.result;
        try {
            const data = JSON.parse(content);
            
            if (ws.readyState !== WebSocket.OPEN) {
                alert(">> WebSocket not connected !");
                return;
              }


            // Envoie conforme à ton JSON
            ws.send(JSON.stringify({
                type: "upload_process_config",
                allowed_process: data.allowed_process  // correspond à la clé du fichier
            }));

            alert("[Notice] Process configuration updated !");
        } catch (e) {
            alert("Fichier JSON invalide : " + e.message);
        }
    };
    reader.readAsText(file);
}
