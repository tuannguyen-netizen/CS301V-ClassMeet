import React, { useEffect, useRef } from 'react';
import { initializeWebRTC, handleIncomingStream } from '../utils/webrtc';
import './VideoCall.css';

const VideoCall = () => {
    const localVideoRef = useRef(null);
    const remoteVideoRef = useRef(null);

    useEffect(() => {
        const startVideoCall = async () => {
            const localStream = await initializeWebRTC(localVideoRef.current, remoteVideoRef.current);
            handleIncomingStream(remoteVideoRef.current);
        };

        startVideoCall();

        return () => {
            // Cleanup logic if needed
        };
    }, []);

    return (
        <div className="video-call-container">
            <video ref={localVideoRef} autoPlay muted className="local-video" />
            <video ref={remoteVideoRef} autoPlay className="remote-video" />
        </div>
    );
};

export default VideoCall;