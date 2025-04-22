document.getElementById("join-meeting-form").addEventListener("submit", async function (e) {
    e.preventDefault();

    const token = localStorage.getItem("token");
    const meetingCode = document.getElementById("meeting-code").value;

    try {
        const response = await fetch("/meeting/join", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`,
            },
            body: JSON.stringify({ meeting_code: meetingCode }),
        });

        if (response.ok) {
            alert("Successfully joined the meeting!");
            window.location.href = "meeting.html";
        } else {
            const errorData = await response.json();
            alert(`Failed to join meeting: ${errorData.detail}`);
        }
    } catch (error) {
        console.error("Error joining meeting:", error);
        alert("An error occurred. Please try again.");
    }
});
