



const bgSelect = document.getElementById('bg-select');
const bgUpload = document.getElementById('bg-upload');

// Gestion du <select>
bgSelect.addEventListener('change', () => {
    const value = bgSelect.value;
    if (value === "none") {
        document.body.style.backgroundImage = "none";
    } else {
        document.body.style.backgroundImage = `url("/static/${value}")`;
        document.body.style.backgroundSize = "cover";
        document.body.style.backgroundAttachment = "fixed";
    }
});

// Gestion du input file
bgUpload.addEventListener('change', (event) => {
    const file = event.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = function(e) {
        document.body.style.backgroundImage = `url('${e.target.result}')`;
        document.body.style.backgroundSize = "cover";
        document.body.style.backgroundAttachment = "fixed";
    };
    reader.readAsDataURL(file);
});




            