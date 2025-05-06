document.addEventListener("DOMContentLoaded", function () {
    const createClassButton = document.getElementById("create-class-btn");
    const joinMeetingButton = document.getElementById("join-meeting-btn");
    const classList = document.getElementById("class-list");
    const userName = document.getElementById("user-name");
    const logoutButton = document.getElementById("logout-btn");
    const token = localStorage.getItem("token");

    logoutButton.addEventListener("click", function () {
        localStorage.removeItem("token");
        window.location.href = "login.html";
    });

    createClassButton.addEventListener("click", function () {
        window.location.href = "create_class.html";
    });

    joinMeetingButton.addEventListener("click", function () {
        window.location.href = "join_meeting.html";
    });

    if (!token) {
        alert("You are not logged in. Redirecting to login page...");
        window.location.href = "login.html";
        return;
    }
});