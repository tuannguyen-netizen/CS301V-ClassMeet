document.addEventListener("DOMContentLoaded", async function () {
    const token = localStorage.getItem("token");
    if (!token) {
        alert("You are not logged in. Redirecting to login page...");
        window.location.href = "login.html";
        return;
    }

    try {
        const response = await fetch("/meeting/details", {
            headers: {
                "Authorization": `Bearer ${token}`,
            },
        });

        if (response.ok) {
            const meetingData = await response.json();
            document.getElementById("meeting-title").textContent = meetingData.title;
            document.getElementById("meeting-description").textContent = meetingData.description;
        } else {
            alert("Failed to load meeting details.");
        }
    } catch (error) {
        console.error("Error fetching meeting details:", error);
        alert("An error occurred. Please try again.");
    }
});
