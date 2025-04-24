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

document.getElementById("meeting-code").addEventListener("input", function () {
    const meetingCode = document.getElementById("meeting-code").value;
    const joinButton = document.getElementById("join-button");
    joinButton.disabled = meetingCode.length === 0;
});

document.getElementById("meeting-code").addEventListener("keydown", function (e) {
    if (e.key === "Enter") {
        e.preventDefault();
        document.getElementById("join-meeting-form").dispatchEvent(new Event("submit"));
    }
});

document.getElementById("meeting-code").focus();
