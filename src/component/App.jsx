import React, { useState } from 'react';
import ChatBox from './ChatBox';
import VideoCall from './VideoCall';
import './App.css';

const App = () => {
    const [isCallActive, setIsCallActive] = useState(false);

    const toggleCall = () => {
        setIsCallActive(!isCallActive);
    };

    return (
        <div className="app-container">
            <h1>WebRTC Video Chat</h1>
            <button onClick={toggleCall}>
                {isCallActive ? 'End Call' : 'Start Call'}
            </button>
            {isCallActive ? <VideoCall /> : <ChatBox />}
        </div>
    );
};

export default App;