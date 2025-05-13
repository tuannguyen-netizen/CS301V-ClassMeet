import React, { useState, useEffect } from 'react';
import './ChatBox.css';

const ChatBox = ({ socket }) => {
    const [message, setMessage] = useState('');
    const [messages, setMessages] = useState([]);

    useEffect(() => {
        socket.on('receive_message', (data) => {
            setMessages((prevMessages) => [...prevMessages, data]);
        });

        return () => {
            socket.off('receive_message');
        };
    }, [socket]);

    const sendMessage = () => {
        if (message.trim()) {
            const messageData = {
                message,
                time: new Date().toLocaleTimeString(),
            };
            socket.emit('send_message', messageData);
            setMessages((prevMessages) => [...prevMessages, messageData]);
            setMessage('');
        }
    };

    return (
        <div className="chat-box">
            <div className="messages">
                {messages.map((msg, index) => (
                    <div key={index} className="message">
                        <span>{msg.time}</span>: {msg.message}
                    </div>
                ))}
            </div>
            <input
                type="text"
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                placeholder="Type a message..."
            />
            <button onClick={sendMessage}>Send</button>
        </div>
    );
};

export default ChatBox;