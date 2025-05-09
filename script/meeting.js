import React from 'react';

const Meeting = () => {
    return (
        <div>
            <h1>Meeting</h1>
            <div>
                <video id="localVideo" autoPlay></video>
                <div className="chatbox">
                    <div id="messages"></div>
                    <input type="text" id="messageInput" placeholder="Type a message..." />
                    <button id="sendButton">Send</button>
                </div>
            </div>
            <Link to="/">End Meeting</Link>
        </div>
    );
};

export default Meeting.listen(5000);
