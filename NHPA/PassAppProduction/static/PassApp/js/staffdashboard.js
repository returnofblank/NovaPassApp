// Define the refresh function
function refreshPasses() {
    fetch('/api/json-passes/')
        .then(response => response.json())
        .then(data => {
            const passesContainer = document.getElementById('passes-container');
            // Clear old content and set header
            passesContainer.innerHTML = `
                <h2><span class="pass-label">Passes</span></h2>
                <div class="pass-categories">
                    <h3>Name</h3>
                    <h3>Start Time</h3>
                    <h3>Duration</h3>
                    <h3>To</h3>
                </div>
            `;

            // Check if there are any passes
            if (data.passes.length === 0) {
                const noPasses = '<h2>No passes found</h2>';
                passesContainer.innerHTML += noPasses;
            } else {
                // Populate Passes
                data.passes.forEach(pass => {
                    // Parse the datetime string to a Date object
                    const startTime = new Date(pass.start_time.replace(' ', 'T'));

                    const passHtml = `
                        <div class="pass-display ${pass.status === 'Expired' ? 'expired' : pass.status === 'Active' ? 'active' : ''}" id="pass-${pass.id}">
                            <p>${pass.student_name}</p>
                            <p>${startTime.toLocaleTimeString('en-US', { hour: 'numeric', minute: 'numeric', hour12: true })}</p>
                            <p>${pass.duration} minutes</p>
                            <p>${pass.room_to}</p>
                        </div>`;
                    passesContainer.innerHTML += passHtml;
                });

                addSwipeFunctionality();
            }
        })
        .catch(error => {
            console.error('Error fetching passes:', error);
        });
}

function addSwipeFunctionality() {
    const passDisplays = document.querySelectorAll('.pass-display.expired');

    passDisplays.forEach(passDisplay => {
        let startX;

        const handleStart = (clientX) => {
            startX = clientX;
            passDisplay.classList.add('swiping');
        };

        const handleMove = (clientX) => {
            const moveX = startX - clientX; // Change to swipe left
            if (moveX > 0) { // Swiping left
                passDisplay.style.transform = `translateX(-${moveX}px)`;
            }
        };

        const handleEnd = (clientX) => {
            const moveX = startX - clientX; // Change to swipe left
            if (moveX > passDisplay.offsetWidth / 2) { // Swipe threshold
                passDisplay.classList.add('swiped');
                setTimeout(() => {
                    passDisplay.style.display = 'none';
                    endPass(passDisplay.id.split('-')[1]); // Pass the pass ID to the endPass function
                }, 300);
            } else {
                passDisplay.style.transform = 'translateX(0)';
            }
            passDisplay.classList.remove('swiping');
        };

        // Touch events
        passDisplay.addEventListener('touchstart', (e) => handleStart(e.touches[0].clientX));
        passDisplay.addEventListener('touchmove', (e) => handleMove(e.touches[0].clientX));
        passDisplay.addEventListener('touchend', (e) => handleEnd(e.changedTouches[0].clientX));

        // Mouse events
        passDisplay.addEventListener('mousedown', (e) => handleStart(e.clientX));
        passDisplay.addEventListener('mousemove', (e) => {
            if (passDisplay.classList.contains('swiping')) {
                handleMove(e.clientX);
            }
        });
        passDisplay.addEventListener('mouseup', (e) => {
            if (passDisplay.classList.contains('swiping')) {
                handleEnd(e.clientX);
            }
        });

        // Mouse leave event to handle cases where the mouse leaves the element while swiping
        passDisplay.addEventListener('mouseleave', (e) => {
            if (passDisplay.classList.contains('swiping')) {
                handleEnd(e.clientX);
            }
        });
    });
}

function endPass(passId) {
    const csrfToken = document.body.getAttribute('data-csrf-token');
    const endPassUrl = document.body.getAttribute('data-end-pass-url').replace('0', passId);

    fetch(endPassUrl, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({ pass_id: passId })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            console.log(`Pass ${passId} ended successfully.`);
        } else {
            console.error(`Failed to end pass ${passId}.`);
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

// Refresh every 10 seconds
setInterval(refreshPasses, 10000);

// Initial load
refreshPasses();