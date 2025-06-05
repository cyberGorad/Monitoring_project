
// Vocal command keydown listener
window.addEventListener('keydown', function(event) {
    // Only trigger if not typing in an input field
    if (event.code === 'Space' && event.target.tagName !== 'INPUT' && event.target.tagName !== 'TEXTAREA') {
        event.preventDefault();
        startVoice();
    }
});

// Login Animation Logic
const loginSection = document.getElementById('login-section');
const showLoginLink = document.getElementById('show-login-link');
const closeLoginButton = document.getElementById('close-login');
// Function to show the login form - Futuristic v2 (Skew, Rotate, Filter)
function showLogin() {
    // Reset initial visual state right before animating IF NEEDED
    // loginSection.style.transform = 'translate(-50%, -50%) scale(0.8) skewX(-10deg) rotateZ(-5deg)'; // Example if base CSS doesn't set it

    anime({
        targets: loginSection,
        opacity: [0, 1],                  // Fade in
        scale: [0.85, 1],                 // Scale up from slightly smaller
        skewX: [-10, 0],                  // Correct skew distortion
        rotateZ: [-8, 0],                 // Correct slight rotation
        filter: ['blur(8px) brightness(1.8)', 'blur(0px) brightness(1)'], // De-blur and fade from bright
        duration: 700,                    // Slightly longer duration for effect
        easing: 'easeOutExpo',            // Smooth but quick deceleration
        // easing: 'easeOutElastic(1, .7)', // Alternative: Bouncier feel
        begin: function(anim) {
            // Ensure it's interactive as soon as it starts appearing
            loginSection.style.pointerEvents = 'auto';
        }
    });
}

// Function to hide the login form - Futuristic v2 (Reverse with distortion)
function hideLogin() {
     anime({
        targets: loginSection,
        opacity: [1, 0],                  // Fade out
        scale: [1, 0.7],                  // Shrink down significantly
        skewX: [0, 15],                   // Skew out noticeably
        rotateZ: [0, 10],                 // Rotate out
        filter: ['blur(0px)', 'blur(10px) brightness(0.5)'], // Blur out and dim
        duration: 500,                    // Faster hide
        easing: 'easeInOutQuad',          // Smooth acceleration into hiding
        complete: function(anim) {
            // Make non-interactive only after fully hidden
            loginSection.style.pointerEvents = 'none';
            // Optional: Reset transform/filter if needed after hiding fully
            // loginSection.style.transform = 'translate(-50%, -50%)';
            // loginSection.style.filter = 'blur(0px) brightness(1)';
        }
    });
}

// --- Keep the rest of your JavaScript event listeners the same ---
// (Event listener for show-login-link, close-login, Escape key etc.)

// Event listener for the login link
if (showLoginLink) {
     showLoginLink.addEventListener('click', function(event) {
        event.preventDefault(); // Prevent default anchor behavior
        showLogin();
     });
}

 // Event listener for the close button
 if (closeLoginButton) {
     closeLoginButton.addEventListener('click', function() {
        hideLogin();
     });
 }

// Optional: Hide login form if clicked outside of it
// window.addEventListener('click', function(event) {
//     if (loginSection.style.opacity === '1' && !loginSection.contains(event.target) && event.target !== showLoginLink) {
//         hideLogin();
//     }
// });

// Optional: Hide login form with Escape key
window.addEventListener('keydown', function(event) {
    if (event.key === 'Escape' && loginSection.style.opacity === '1') {
        hideLogin();
    }
});


Swal.fire({
    title: 'GORA',
    text: "{{ message|escapejs }}",
    icon: '{% if message.tags == "error" %}error{% elif message.tags == "success" %}success{% else %}info{% endif %}',
    background: 'black',
    color: '#00ff00',
    confirmButtonColor: '#00ff00',
    timer: 5000,
    timerProgressBar: true,
    showClass: {
      popup: 'animate__animated animate__zoomIn'
    },
    hideClass: {
      popup: 'animate__animated animate__zoomOut'
    }
  });