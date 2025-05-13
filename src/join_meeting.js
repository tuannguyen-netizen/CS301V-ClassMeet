import React, { useState } from 'react';
import axios from 'axios';

const JoinMeeting = () => {
    const [meetingCode, setMeetingCode] = useState('');

    const handleJoinMeeting = async (e) => {
        e.preventDefault();
        try {
            const response = await axios.post('http://backend3.example.com/api/meeting/join', {
                meeting_code: meetingCode
            }, {
                headers: {
                    Authorization: `Bearer ${localStorage.getItem("token")}`
                }
            });
            alert("Successfully joined the meeting!");
            window.location.href = "/meeting"; // Redirect to Meeting
        } catch (error) {
            console.error('Error joining meeting', error);
            alert("Failed to join meeting. Please try again.");
        }
    };

    return (
        <div>
            <h1>Join Meeting</h1>
            <form onSubmit={handleJoinMeeting}>
                <input type="text" value={meetingCode} onChange={(e) => setMeetingCode(e.target.value)} placeholder="Meeting Code" required />
                <button type="submit">Join Meeting</button>
            </form>
        </div>
    );
};

export default JoinMeeting;
