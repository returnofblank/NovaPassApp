fetch('/api/json-passes/')
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok: ' + response.statusText);
        }
        return response.json();
    })
    .then(data => {
        if (!data.passes) {
            throw new Error('No passes found in the response');
        }
        data.passes.forEach(pass => {
            const passStatusUrl = `/api/pass-status/${pass.id}`;
            startTimer(pass.id, passStatusUrl);
        });
    })
    .catch(error => {
        console.error('Error fetching passes:', error);
    });

var timerIntervals = {};

function startTimer(passId, passStatusUrl) {
    updateTimer(passId, passStatusUrl);  // Initial immediate update
    var intervalId = setInterval(function() {
        updateTimer(passId, passStatusUrl);
    }, 1000);  // Update every second
    timerIntervals[passId] = intervalId;  // Store the interval ID for later reference
}

function updateTimer(passId, passStatusUrl) {
    fetch(passStatusUrl)
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok: ' + response.statusText);
        }
        return response.json();
    })
    .then(data => {
        const elementId = `timer-${passId}`;
        const timeElement = document.getElementById(elementId);
        if (!timeElement) {
            console.error(`Element with ID '${elementId}' not found.`);
            clearInterval(timerIntervals[passId]);  // Clear the interval if element is missing
            return;
        }
        if (data.status === "Active") {
            timeElement.innerText = `${data.remaining_minutes}m ${data.remaining_seconds}s`;
        } else if (data.status === "Ended") {
            window.location.href = '/dashboard';
        } else {
            timeElement.innerText = "EXPIRED";
            timeElement.classList.add('expired');
        }
    })
    .catch(error => {
        console.error('Fetch error for passId ' + passId + ':', error);
    });
}