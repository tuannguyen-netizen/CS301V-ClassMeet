import React, { useState } from 'react';
import axios from 'axios';

const JoinClass = () => {
    const [IDClass, setIDClass] = useState('');

    const handleJoinClass = async (e) => {
        e.preventDefault();
        try {
            const response = await axios.post('http://backend3.example.com/api/class/join', {
                class_id: IDClass,
                description
            }, {
                headers: {
                    Authorization: `Bearer ${localStorage.getItem("token")}`
                }
            });
            alert("Class joined successfully!");
            window.location.href = "/class_member"; // Redirect to Class Leader
        } catch (error) {
            console.error('Error joining class', error);
            alert("Failed to join class. Please try again.");
        }
    };

    return (
        <div>
            <h1>Join Class</h1>
            <form onSubmit={handleJoinClass}>
                <input type="text" value={IDClass} onChange={(e) => setIDClass(e.target.value)} placeholder="Class ID" required />
                <button type="submit">Join Class</button>
            </form>
        </div>
    );
};

export default JoinClass;
