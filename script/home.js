import React from 'react';
import { Link } from 'react-router-dom';

const Home = () => {
    return (
        <div>
            <h1>Welcome to ClassMeet</h1>
            <Link to="/create_join_class">Create or Join Class</Link>
            <Link to="/login">Login</Link>
        </div>
    );
};

export default Home.listen(5000);
