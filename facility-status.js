function getFacilityStatus(openTime, closeTime, closedDays) {
    let now = new Date();
    let currentHour = now.getHours();
    let currentDay = now.getDay(); // 0 = Sunday, 6 = Saturday

    if (closedDays.includes(currentDay)) {
        return "❌ Closed";
    }
    
    if (currentHour >= openTime && currentHour < closeTime) {
        return "✅ Open";
    } else {
        return "❌ Closed";
    }
}

// Update facility status dynamically
document.addEventListener("DOMContentLoaded", function () {
    document.getElementById("library-status").innerText = getFacilityStatus(8, 20, [0]); // Closed Sundays
    document.getElementById("canteen-status").innerText = getFacilityStatus(9, 18, [0]); // Closed Sundays
    document.getElementById("office-status").innerText = getFacilityStatus(10, 17, [6, 0]); // Closed Weekends
});
