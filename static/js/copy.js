
document.getElementById("copy-gemini-response").addEventListener("click", function () {
    const responseText = document.getElementById("gemini-response-text").textContent;

    navigator.clipboard.writeText(responseText).then(() => {
        Swal.fire({
            icon: 'success',
            title: 'Success',
            text: 'Copy successfull',
            toast: true,
            position: 'top-end',
            showConfirmButton: false,
            timer: 2000,
            background:'black',
            color:'#00FF00',
            timerProgressBar: true
    
        });
    }).catch(err => {
        Swal.fire({
            icon: 'error',
            title: 'Error',
            text: 'Fatal ERROR',
            toast: true,
            position: 'top-end',
            showConfirmButton: false,
            background:'black',
            color : 'red',
            timer: 2000,
            timerProgressBar: true
        });
    });
});

