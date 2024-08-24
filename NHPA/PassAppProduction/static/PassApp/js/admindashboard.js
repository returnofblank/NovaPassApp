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
                        <div class="pass-display ${pass.status === 'Expired' || pass.status === 'Ended' ? 'expired' : pass.status === 'Active' ? 'active' : ''}" id="pass-${pass.id}">
                            <p>${pass.student_name}</p>
                            <p>${startTime.toLocaleTimeString('en-US', { hour: 'numeric', minute: 'numeric', hour12: true })}</p>
                            <p>${pass.duration} minutes</p>
                            <p>${pass.room_to}</p>
                            <h3>${pass.status}</h3>
                        </div>`;
                    passesContainer.innerHTML += passHtml;
                });
            }
        })
        .catch(error => {
            console.error('Error fetching passes:', error);
        });
};

// Refresh every 10 seconds
setInterval(refreshPasses, 10000);

// Initial load
refreshPasses();