import React, { useEffect, useState } from 'react';
import axios from 'axios';

const MeetingManagement = () => {
    const [meetings, setMeetings] = useState([]);
    const [title, setTitle] = useState('');
    const [description, setDescription] = useState('');
    const [classId, setClassId] = useState('');

    const fetchMeetings = async () => {
        try {
            const response = await axios.get('http://backend3.example.com/api/meeting/my-meetings', {
                headers: {
                    Authorization: `Bearer ${localStorage.getItem("token")}`
                }
            });
            setMeetings(response.data);
        } catch (error) {
            console.error('Error fetching meetings', error);
        }
    };

    const createMeeting = async () => {
        try {
            const response = await axios.post(`http://backend3.example.com/api/meeting/class/${classId}/create`, {
                title: title,
                description: description
            }, {
                headers: {
                    Authorization: `Bearer ${localStorage.getItem("token")}`
                }
            });
            console.log('Meeting created:', response.data);
            fetchMeetings(); // Refresh the meeting list
        } catch (error) {
            console.error('Error creating meeting', error);
        }
    };

    useEffect(() => {
        fetchMeetings();
    }, []);

    return (
        <div>
            <h2>Meeting Management</h2>
            <input
                type="text"
                value={classId}
                onChange={(e) => setClassId(e.target.value)}
                placeholder="Class ID"
            />
            <input
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="Meeting Title"
            />
            <input
                type="text"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Description"
            />
            <button onClick={createMeeting}>Create Meeting</button>

            <h3>Your Meetings</h3>
            <ul>
                {meetings.map((meeting) => (
                    <li key={meeting.meeting_id}>
                        {meeting.title} - {meeting.description}
                    </li>
                ))}
            </ul>
        </div>
    );
};

export default MeetingManagement;
