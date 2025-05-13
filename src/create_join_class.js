import React from 'react';
import { Link } from 'react-router-dom';

const CreateJoinClass = () => {
    return (
        <div>
            <h1>Create or Join a Class</h1>
            <Link to="/create_class">Create Class</Link>
            <Link to="/join_meeting">Join Meeting</Link>
        </div>
    );
};

export default CreateJoinClass;
