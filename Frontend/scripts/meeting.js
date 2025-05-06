document.addEventListener('DOMContentLoaded', () => {
    const localVideo = document.getElementById('localVideo');
    const remoteVideo = document.getElementById('remoteVideo');
    const messages = document.getElementById('messages');
    const messageInput = document.getElementById('messageInput');
    const sendButton = document.getElementById('sendButton');
    const muteButton = document.getElementById('mute-btn');
    const videoButton = document.getElementById('video-btn');
    const volumeButton = document.getElementById('volume-btn');
    const endCallButton = document.getElementById('end-call-btn');

    // Initialize video call
    navigator.mediaDevices.getUserMedia({ video: true, audio: true })
        .then(stream => {
            localVideo.srcObject = stream;
            // Simulate remote video for demo purposes
            remoteVideo.srcObject = stream;
        })
        .catch(error => console.error('Error accessing media devices:', error));

    // Chatbox functionality
    sendButton.addEventListener('click', () => {
        const message = messageInput.value.trim();
        if (message) {
            const messageElement = document.createElement('div');
            messageElement.textContent = message;
            messages.appendChild(messageElement);
            messageInput.value = '';
            messages.scrollTop = messages.scrollHeight;
        }
    });

    // Mute/unmute microphone
    muteButton.addEventListener('click', () => {
        const stream = localVideo.srcObject;
        if (stream) {
            const audioTracks = stream.getAudioTracks();
            audioTracks.forEach(track => track.enabled = !track.enabled);
            console.log(`Microphone ${audioTracks[0].enabled ? 'unmuted' : 'muted'}`);
        }
    });

    // Toggle camera on/off
    videoButton.addEventListener('click', () => {
        const stream = localVideo.srcObject;
        if (stream) {
            const videoTracks = stream.getVideoTracks();
            videoTracks.forEach(track => track.enabled = !track.enabled);
            console.log(`Camera ${videoTracks[0].enabled ? 'enabled' : 'disabled'}`);
        }
    });

    // Toggle volume on/off
    volumeButton.addEventListener('click', () => {
        const stream = remoteVideo.srcObject;
        if (stream) {
            const audioTracks = stream.getAudioTracks();
            audioTracks.forEach(track => track.enabled = !track.enabled);
            console.log(`Volume ${audioTracks[0].enabled ? 'enabled' : 'muted'}`);
        }
    });

    // Confirm before ending the call
    endCallButton.addEventListener('click', (event) => {
        if (!confirm('Are you sure you want to end the call?')) {
            event.preventDefault();
        }
    });
});
