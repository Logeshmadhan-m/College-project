let map, userMarker, destinationMarker, directionsService, directionsRenderer;

function initMap() {
    map = new google.maps.Map(document.getElementById("map"), {
        center: { lat: 11.104, lng: 79.694 }, // Default campus center
        zoom: 17
    });

    directionsService = new google.maps.DirectionsService();
    directionsRenderer = new google.maps.DirectionsRenderer();
    directionsRenderer.setMap(map);

    fetch("/get_locations")
        .then(response => response.json())
        .then(data => {
            let destinationSelect = document.getElementById("destination");
            for (let key in data) {
                let option = document.createElement("option");
                option.value = key;
                option.textContent = key;
                destinationSelect.appendChild(option);
            }
        });

    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(function(position) {
            let userLocation = {
                lat: position.coords.latitude,
                lng: position.coords.longitude
            };
            userMarker = new google.maps.Marker({
                position: userLocation,
                map: map,
                title: "Your Location"
            });
            map.setCenter(userLocation);
        });
    }
}

function startNavigation() {
    let selectedDestination = document.getElementById("destination").value;

    fetch("/get_locations")
        .then(response => response.json())
        .then(data => {
            let destinationCoords = data[selectedDestination];

            if (destinationMarker) {
                destinationMarker.setMap(null);
            }

            destinationMarker = new google.maps.Marker({
                position: destinationCoords,
                map: map,
                title: selectedDestination
            });

            let request = {
                origin: userMarker.getPosition(),
                destination: destinationCoords,
                travelMode: 'WALKING'
            };

            directionsService.route(request, function(response, status) {
                if (status === 'OK') {
                    directionsRenderer.setDirections(response);
                } else {
                    alert('Could not find a route.');
                }
            });
        });
}

// Load map when the page is loaded
window.onload = initMap;
