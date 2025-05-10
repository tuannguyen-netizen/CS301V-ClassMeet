import React, { useState } from 'react';
import axios from 'axios';

const CreateClass = () => {
    const [className, setClassName] = useState('');
    const [description, setDescription] = useState('');

    const handleCreateClass = async (e) => {
        e.preventDefault();
        try {
            const response = await axios.post('http://backend3.example.com/api/class/create', {
                class_name: className,
                description
            }, {
                headers: {
                    Authorization: `Bearer ${localStorage.getItem("token")}`
                }
            });
            alert("Class created successfully!");
            window.location.href = "/class_leader"; // Redirect to Class Leader
        } catch (error) {
            console.error('Error creating class', error);
            alert("Failed to create class. Please try again.");
        }
    };

    return (
        <div>
            <h1>Create Class</h1>
            <form onSubmit={handleCreateClass}>
                <input type="text" value={className} onChange={(e) => setClassName(e.target.value)} placeholder="Class Name" required />
                <input type="text" value={description} onChange={(e) => setDescription(e.target.value)} placeholder="Description" />
                <button type="submit">Create Class</button>
            </form>
        </div>
    );
};

export default CreateClass.listen(5000);
