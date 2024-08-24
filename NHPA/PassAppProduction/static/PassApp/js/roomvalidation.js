function selectTime(element) {
    var buttons = document.querySelectorAll('.time-btn');
    buttons.forEach(btn => btn.classList.remove('active'));
    element.classList.add('active');

    // Set the value of the hidden input to the time associated with the clicked button
    document.getElementById('selected-time').value = element.textContent.trim();
}

const buildingFromSelect = document.getElementById('building-from');
const roomFromSelect = document.getElementById('room-from');
const buildingToSelect = document.getElementById('building-to');
const roomToSelect = document.getElementById('room-to');

function updateRooms(buildingSelect, roomSelect) {
    const selectedBuilding = buildingSelect.value;
    const rooms = locations[selectedBuilding];
    
    roomSelect.innerHTML = '<option>Select a room</option>';  // Clear previous rooms and add a prompt
    rooms.forEach(function(room) {
        const option = document.createElement('option');
        option.value = room;
        option.textContent = room;
        roomSelect.appendChild(option);
    });
}

buildingFromSelect.addEventListener('change', function() {
    updateRooms(buildingFromSelect, roomFromSelect);
});

buildingToSelect.addEventListener('change', function() {
    updateRooms(buildingToSelect, roomToSelect);
});

// Initialize rooms on load based on the first building option if necessary
updateRooms(buildingFromSelect, roomFromSelect);
updateRooms(buildingToSelect, roomToSelect);