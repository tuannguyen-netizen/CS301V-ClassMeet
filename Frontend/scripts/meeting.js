const socket = io();
const peer = new Peer();

const localVideo = document.getElementById('local-video');
const remoteVideo = document.getElementById('remote-video');
const muteBtn = document.getElementById('mute-btn-button');
const videoBtn = document.getElementById('video-btn-button');
const volumeBtn = document.getElementById('volume-btn-button');
const endBtn = document.getElementById('end-btn-button');
const chatInput = document.getElementById('chat-input');
const sendBtn = document.getElementById('send-btn');
const chatBox = document.getElementById('chat-box');

let localStream;
let isMuted = false;
let isVideoOn = true;
let volumeOn = true;

// Initialize WebRTC
async function init() {
  try {
    localStream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
    localVideo.srcObject = localStream;

    peer.on('open', (id) => {
      socket.emit('join-room', 'video-call-room', id);
    });

    peer.on('call', (call) => {
      call.answer(localStream);
      call.on('stream', (remoteStream) => {
        remoteVideo.srcObject = remoteStream;
      });
    });

    socket.on('user-connected', (userId) => {
      const call = peer.call(userId, localStream);
      call.on('stream', (remoteStream) => {
        remoteVideo.srcObject = remoteStream;
      });
    });
  } catch (err) {
    console.error('Error accessing media devices:', err);
  }
}

// Chat functionality
function addMessage(content, isSent) {
  const messageDiv = document.createElement('div');
  messageDiv.classList.add('message', isSent ? 'sent' : 'received');
  messageDiv.textContent = content;
  chatBox.appendChild(messageDiv);
  chatBox.scrollTop = chatBox.scrollHeight;
}

sendBtn.addEventListener('click', () => {
  const message = chatInput.value.trim();
  if (message) {
    socket.emit('chat-message', message);
    addMessage(message, true);
    chatInput.value = '';
  }
});

chatInput.addEventListener('keypress', (e) => {
  if (e.key === 'Enter') {
    sendBtn.click();
  }
  if (e.key === 'Escape') {
    chatInput.value = '';
  }
  if (e.key === 'ArrowUp') {
    chatInput.value = chatInput.value.slice(0, -1); // Remove last character
  }
});

socket.on('chat-message', (message) => {
  addMessage(message, false);
});

socket.on('user-disconnected', (userId) => {
  console.log(`User ${userId} disconnected`);
  // Handle user disconnection (e.g., show a message or update UI)
});

// Media controls
muteBtn.addEventListener('click', () => {
  isMuted = !isMuted;
  localStream.getAudioTracks()[0].enabled = !isMuted;
  muteBtn.style.backgroundColor = isMuted ? '#ccc' : '#fff';
});

videoBtn.addEventListener('click', () => {
  isVideoOn = !isVideoOn;
  localStream.getVideoTracks()[0].enabled = isVideoOn;
  videoBtn.style.backgroundColor = isVideoOn ? '#fff' : '#ccc';
});

volumeBtn.addEventListener('click', () => {
  volumeOn = !volumeOn;
  remoteVideo.muted = !volumeOn;
  volumeBtn.style.backgroundColor = volumeOn ? '#fff' : '#ccc';
});

endBtn.addEventListener('click', () => {
  localStream.getTracks().forEach(track => track.stop());
  localVideo.srcObject = null;
  remoteVideo.srcObject = null;
  socket.disconnect();
});

// Handle window close event
window.addEventListener('beforeunload', () => {
  localStream.getTracks().forEach(track => track.stop());
  socket.disconnect();
});

// Handle chat input focus and blur events
chatInput.addEventListener('focus', () => {
  chatInput.style.backgroundColor = '#fff';
});
// Start the app
init();