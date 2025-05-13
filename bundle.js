// Log a message to confirm the script is loaded
console.log("bundle.js loaded successfully");

// Example: Initialize WebRTC connection
const startVideoChat = async () => {
    try {
        // Get access to the user's webcam and microphone
        const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });

        // Display the local video stream
        const videoElement = document.createElement("video");
        videoElement.srcObject = stream;
        videoElement.autoplay = true;
        videoElement.muted = true; // Mute local video to avoid echo
        document.getElementById("app").appendChild(videoElement);

        console.log("Video chat initialized successfully");
    } catch (error) {
        console.error("Error initializing video chat:", error);
    }
};

// Start the video chat when the page loads
window.addEventListener("DOMContentLoaded", startVideoChat);