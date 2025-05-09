import React, { useEffect, useState } from 'react';
import axios from 'axios';

const ClassManagement = () => {
    const [classes, setClasses] = useState([]);
    const [className, setClassName] = useState('');
    const [description, setDescription] = useState('');

    const fetchClasses = async () => {
        try {
            const response = await axios.get('http://backend3.example.com/api/class/my-classes', {
                headers: {
                    Authorization: `Bearer ${localStorage.getItem("token")}`
                }
            });
            setClasses(response.data);
        } catch (error) {
            console.error('Error fetching classes', error);
        }
    };

    const createClass = async () => {
        try {
            const response = await axios.post('http://backend3.example.com/api/class/create', {
                class_name: className,
                description: description
            }, {
                headers: {
                    Authorization: `Bearer ${localStorage.getItem("token")}`
                }
            });
            console.log('Class created:', response.data);
            fetchClasses(); // Refresh the class list
        } catch (error) {
            console.error('Error creating class', error);
        }
    };

    useEffect(() => {
        fetchClasses();
    }, []);

    return (
        <div>
            <h2>Class Management</h2>
            <input
                type="text"
                value={className}
                onChange={(e) => setClassName(e.target.value)}
                placeholder="Class Name"
            />
            <input
                type="text"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Description"
            />
            <button onClick={createClass}>Create Class</button>

            <h3>Your Classes</h3>
            <ul>
                {classes.map((cls) => (
                    <li key={cls.class_id}>
                        {cls.class_name} - {cls.description}
                    </li>
                ))}
            </ul>
        </div>
    );
};

export default ClassManagement;
