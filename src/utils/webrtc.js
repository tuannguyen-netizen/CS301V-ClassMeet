const configuration = {
  iceServers: [
    {
      urls: 'stun:stun.l.google.com:19302'
    },
    {
      urls: 'turn:YOUR_TURN_SERVER_URL',
      username: 'YOUR_TURN_SERVER_USERNAME',
      credential: 'YOUR_TURN_SERVER_CREDENTIAL'
    }
  ]
};

let localStream;
let peerConnection;
const localVideo = document.getElementById('localVideo');
const remoteVideo = document.getElementById('remoteVideo');

export const startLocalStream = async () => {
  localStream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
  localVideo.srcObject = localStream;
};

export const createPeerConnection = () => {
  peerConnection = new RTCPeerConnection(configuration);

  localStream.getTracks().forEach(track => {
    peerConnection.addTrack(track, localStream);
  });

  peerConnection.onicecandidate = event => {
    if (event.candidate) {
      // Send the candidate to the remote peer
    }
  };

  peerConnection.ontrack = event => {
    remoteVideo.srcObject = event.streams[0];
  };
};

export const createOffer = async () => {
  const offer = await peerConnection.createOffer();
  await peerConnection.setLocalDescription(offer);
  // Send the offer to the remote peer
};

export const createAnswer = async (offer) => {
  await peerConnection.setRemoteDescription(new RTCSessionDescription(offer));
  const answer = await peerConnection.createAnswer();
  await peerConnection.setLocalDescription(answer);
  // Send the answer back to the remote peer
};

export const handleRemoteCandidate = (candidate) => {
  peerConnection.addIceCandidate(new RTCIceCandidate(candidate));
};