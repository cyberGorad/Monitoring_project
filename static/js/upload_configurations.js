function sendPortConfig() {
    const input = document.getElementById("uploadPortJson");
    const file = input.files[0];
    if (!file) return alert("No file selected");

    const reader = new FileReader();
    reader.onload = function (e) {
        const content = e.target.result;
        try {
            const data = JSON.parse(content);
            socket.send(JSON.stringify({
                type: "upload_port_config",
                allowed_ports: data.allowed_ports
            }));
            alert("[Notice] Process Configuration updated success !");
        } catch (e) {
            alert("Error file not valid : " + e.message);
        }
    };
    reader.readAsText(file);
}