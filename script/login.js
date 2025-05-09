import React, { useState } from 'react';
import axios from 'axios';

const Login = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');

    const handleLogin = async (e) => {
        e.preventDefault();
        try {
            const response = await axios.post('../backend3/api/auth/login', {
                email,
                password
            });
            localStorage.setItem("token", response.data.token);
            alert("Login successful!");
            window.location.href = "/"; // Redirect to home
        } catch (error) {
            console.error('Error logging in', error);
            alert("Login failed. Please try again.");
        }
    };

    return (
        <div>
            <h1>Login</h1>
            <form onSubmit={handleLogin}>
                <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="Email" required />
                <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="Password" required />
                <button type="submit">Login</button>
            </form>
            <Link to="/register">Register</Link>
        </div>
    );
};

export default Login.listen(5000);
