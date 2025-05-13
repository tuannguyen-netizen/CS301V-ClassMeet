import React from 'react';
import { Link } from 'react-router-dom';

const Home = () => {
    return (
        <div>
            <h1>Welcome to ClassMeet</h1>
            <Link to="/create_class">Create Class</Link>
            <Link to="/join_class">Join Class</Link>
            <Link to="/login">Login</Link>
            <Link to="/index">Join</Link>
        </div>
    );
};

export default Home;
