import React, { useRef, useEffect, useState } from 'react';
import '../style/meeting.css';
import { Link } from 'react-router-dom';
import io from 'socket.io-client';

const socket = io('http://172.20.10.3:5000/meeting.html'); // Thay bằng URL server của bạn

const Meeting = () => {
    const localVideoRef = useRef(null);
    const remoteVideoRef = useRef(null);
    const messagesRef = useRef(null);
    const messageInputRef = useRef(null);

    const [localStream, setLocalStream] = useState(null);
    const [peerConnection, setPeerConnection] = useState(null);

    const config = { iceServers: [{ urls: 'stun:stun.l.google.com:19302' }] };

    useEffect(() => {
        // Get user media
        navigator.mediaDevices.getUserMedia({ video: true, audio: true })
            .then(stream => {
                if (localVideoRef.current) {
                    localVideoRef.current.srcObject = stream;
                }
                setLocalStream(stream);
            })
            .catch(error => console.error('Error accessing media devices.', error));
    }, []);

    useEffect(() => {
        if (localStream) {
            const pc = new RTCPeerConnection(config);
            localStream.getTracks().forEach(track => pc.addTrack(track, localStream));

            pc.ontrack = event => {
                if (remoteVideoRef.current) {
                    remoteVideoRef.current.srcObject = event.streams[0];
                }
            };

            pc.onicecandidate = event => {
                if (event.candidate) {
                    socket.emit('ice-candidate', event.candidate);
                }
            };

            socket.on('offer', async (offer) => {
                await pc.setRemoteDescription(new RTCSessionDescription(offer));
                const answer = await pc.createAnswer();
                await pc.setLocalDescription(answer);
                socket.emit('answer', answer);
            });

            socket.on('answer', async (answer) => {
                await pc.setRemoteDescription(new RTCSessionDescription(answer));
            });

            socket.on('ice-candidate', async (candidate) => {
                try {
                    await pc.addIceCandidate(new RTCIceCandidate(candidate));
                } catch (error) {
                    console.error('Error adding received ICE candidate', error);
                }
            });

            pc.createOffer()
                .then(offer => pc.setLocalDescription(offer))
                .then(() => {
                    socket.emit('offer', pc.localDescription);
                });

            setPeerConnection(pc);
        }
    }, [localStream]);

    const handleSendMessage = () => {
        const message = messageInputRef.current.value;
        if (message.trim()) {
            socket.emit('chat-message', message);
            const messageElement = document.createElement('div');
            messageElement.textContent = `You: ${message}`;
            if (messagesRef.current) {
                messagesRef.current.appendChild(messageElement);
                messagesRef.current.scrollTop = messagesRef.current.scrollHeight;
            }
            messageInputRef.current.value = '';
        }
    };

    useEffect(() => {
        socket.on('chat-message', (message) => {
            const messageElement = document.createElement('div');
            messageElement.textContent = `Peer: ${message}`;
            if (messagesRef.current) {
                messagesRef.current.appendChild(messageElement);
                messagesRef.current.scrollTop = messagesRef.current.scrollHeight;
            }
        });

        return () => {
            socket.off('chat-message');
        };
    }, []);

    return (
        <div className="meeting-container">
            <h1>Meeting</h1>
            <div className="video-container">
                <video ref={localVideoRef} id="localVideo" autoPlay muted></video>
                <video ref={remoteVideoRef} id="remoteVideo" autoPlay></video>
            </div>
            <div className="chatbox">
                <div ref={messagesRef} id="messages" className="messages"></div>
                <input
                    type="text"
                    ref={messageInputRef}
                    id="messageInput"
                    placeholder="Type a message..."
                />
                <button id="sendButton" onClick={handleSendMessage}>
                    Send
                </button>
            </div>
            <Link to="/home.html" className="end-meeting-link">End Meeting</Link>
        </div>
    );
};

export default Meeting;