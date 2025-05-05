# management/video_server.py
import socket
import pickle
import struct
import threading
import logging

logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        self.active_connections = {}  # {meeting_id: {user_id: websocket}}

    async def connect(self, websocket, meeting_id, user_id):
        await websocket.accept()
        self.active_connections.setdefault(meeting_id, {})[user_id] = websocket
        logger.info(f"User {user_id} connected to meeting {meeting_id}")

    def disconnect(self, meeting_id, user_id):
        if meeting_id in self.active_connections:
            self.active_connections[meeting_id].pop(user_id, None)
            if not self.active_connections[meeting_id]:
                self.active_connections.pop(meeting_id)
            logger.info(f"User {user_id} disconnected from meeting {meeting_id}")

    async def broadcast(self, message, meeting_id, sender_id=None):
        for uid, conn in self.active_connections.get(meeting_id, {}).items():
            if uid != sender_id:
                await conn.send_text(message)


class VideoCallServer:
    def __init__(self, host='0.0.0.0', port=5001):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((host, port))
        self.server_socket.listen(5)
        self.clients = {}
        logger.info(f"Video server started on {host}:{port}")

    def broadcast(self, data, meeting_id, sender_socket):
        for client in self.clients.get(meeting_id, []):
            if client != sender_socket:
                try:
                    client.send(data)
                except:
                    self.clients[meeting_id].remove(client)

    def handle_client(self, client_socket, addr, meeting_id):
        self.clients.setdefault(meeting_id, []).append(client_socket)
        while True:
            try:
                length_size = struct.calcsize("!I")
                data = client_socket.recv(length_size)
                if not data:
                    break
                msg_len = struct.unpack("!I", data)[0]
                payload = b""
                while len(payload) < msg_len:
                    packet = client_socket.recv(msg_len - len(payload))
                    if not packet:
                        break
                    payload += packet
                self.broadcast(struct.pack("!I", len(payload)) + payload, meeting_id, client_socket)
            except:
                break
        self.clients[meeting_id].remove(client_socket)
        client_socket.close()

    def start(self):
        while True:
            client_socket, addr = self.server_socket.accept()
            meeting_id = client_socket.recv(1024).decode().strip()
            if not meeting_id:
                client_socket.close()
                continue
            threading.Thread(target=self.handle_client, args=(client_socket, addr, meeting_id), daemon=True).start()

    def close(self):
        for conns in self.clients.values():
            for client in conns:
                try:
                    client.close()
                except:
                    pass
        self.server_socket.close()
