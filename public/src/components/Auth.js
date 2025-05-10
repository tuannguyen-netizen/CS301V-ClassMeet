import React, { useState } from 'react';
import axios from 'axios';

const Auth = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');

    const handleLogin = async () => {
        try {
            const response = await axios.post('http://backend3.example.com/api/auth/login', {
                email,
                password
            });
            console.log(response.data);
            // Lưu token vào localStorage
            localStorage.setItem("token", response.data.token);
            alert("Login successful!");
            window.location.href = "home.html"; // Chuyển hướng đến trang home
        } catch (error) {
            console.error('Error logging in', error);
            alert("Login failed. Please try again.");
        }
    };

    return (
        <div>
            <h2>Login</h2>
            <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="Email" />
            <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="Password" />
            <button onClick={handleLogin}>Login</button>
        </div>
    );
};

export default Auth;
