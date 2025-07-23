function startNavigation() {
    let destination = document.getElementById("destination").value;
    let mapsUrl = `https://www.google.com/maps/dir/?api=1&destination=${encodeURIComponent(destination)}`;
    window.location.href = mapsUrl;
}
