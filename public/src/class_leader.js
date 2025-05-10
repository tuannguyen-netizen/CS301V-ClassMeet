import React from 'react';
import { Link } from 'react-router-dom';

const ClassLeader = () => {
    return (
        <div>
            <h1>Class Leader</h1>
            <Link to="/create_class">Create Class</Link>
            <Link to="/join_meeting">Join Meeting</Link>
            <Link to="/class_member">Class Members</Link>
        </div>
    );
};

export default ClassLeader.listen(5000);
