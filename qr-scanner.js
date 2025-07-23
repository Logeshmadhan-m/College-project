// Start the camera when the user clicks the button
function startCamera() {
    let video = document.getElementById("video");

    // Ensure browser supports camera access
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        alert("Camera not supported on this device.");
        return;
    }

    // Request camera access
    navigator.mediaDevices.getUserMedia({ video: { facingMode: "environment" } })
        .then(stream => {
            video.srcObject = stream;
        })
        .catch(error => {
            console.error("Camera error:", error);
            alert("Camera access denied or unavailable. Please check permissions in browser settings.");
        });
}

// Ensure camera starts only after user clicks the button
document.getElementById("start-scan").addEventListener("click", startCamera);

// Capture QR code image and send it to the server for processing
function captureQR() {
    let video = document.getElementById("video");
    let canvas = document.getElementById("canvas");
    let ctx = canvas.getContext("2d");

    if (!video.srcObject) {
        alert("Camera is not active. Please start the scan first.");
        return;
    }

    // Capture video frame
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    canvas.toBlob(blob => {
        let formData = new FormData();
        formData.append("qr_image", blob, "qr-code.png");

        fetch("/scan_qr", {
            method: "POST",
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.location) {
                window.location.href = "/map/" + encodeURIComponent(data.location);
            } else {
                alert("QR Code not detected. Try again.");
            }
        })
        .catch(error => {
            console.error("QR scan error:", error);
            alert("Error processing QR code. Please try again.");
        });
    }, "image/png");
}
