document.addEventListener("DOMContentLoaded", function () {
    const createClassButton = document.getElementById("create-class-btn");
    const joinMeetingButton = document.getElementById("join-meeting-btn");

    createClassButton.addEventListener("click", function () {
        window.location.href = "create_class.html";
    });

    joinMeetingButton.addEventListener("click", function () {
        window.location.href = "join_meeting.html";
    });
});