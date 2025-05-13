import { io } from 'socket.io-client';

const socket = io('http://192.168.1.192:5000'); // Replace with your server URL

export const connectSocket = () => {
    socket.connect();
};

export const disconnectSocket = () => {
    socket.disconnect();
};

export const sendMessage = (message) => {
    socket.emit('message', message);
};

export const onMessageReceived = (callback) => {
    socket.on('message', (message) => {
        callback(message);
    });
};

export const onConnect = (callback) => {
    socket.on('connect', () => {
        callback();
    });
};

export const onDisconnect = (callback) => {
    socket.on('disconnect', () => {
        callback();
    });
};