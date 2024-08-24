function selectTime(element) {
    var buttons = document.querySelectorAll('.time-btn');
    buttons.forEach(btn => btn.classList.remove('active'));
    element.classList.add('active');
    document.getElementById('selected-time').value = element.textContent.trim();
}

const buildingFromSelect = document.getElementById('building-from');
const roomFromSelect = document.getElementById('room-from');
const buildingToSelect = document.getElementById('building-to');
const roomToSelect = document.getElementById('room-to');

function updateRooms(buildingSelect, roomSelect) {
    const selectedBuilding = buildingSelect.value;
    const rooms = locations[selectedBuilding];
    
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

updateRooms(buildingFromSelect, roomFromSelect);
updateRooms(buildingToSelect, roomToSelect);