# utils/video_server.py
import socket
import pickle
import struct
import threading
import logging

logger = logging.getLogger(__name__)


class VideoCallServer:
    def __init__(self, host='0.0.0.0', port=5001):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((host, port))
        self.server_socket.listen(5)
        self.clients = {}  # Dictionary to store clients by meeting ID
        logger.info(f"Video server started on {host}:{port}")

    def broadcast(self, data, meeting_id, sender_socket):
        """Broadcast the data to all other clients in the same meeting"""
        if meeting_id in self.clients:
            for client in self.clients[meeting_id]:
                if client != sender_socket:
                    try:
                        client.send(data)
                    except:
                        # Remove failed client
                        self.clients[meeting_id].remove(client)
                        if not self.clients[meeting_id]:
                            del self.clients[meeting_id]

    def handle_client(self, client_socket, client_address, meeting_id):
        """Handle a client connection"""
        logger.info(f"Client {client_address} connected to meeting {meeting_id}")

        # Add client to meeting
        if meeting_id not in self.clients:
            self.clients[meeting_id] = []
        self.clients[meeting_id].append(client_socket)

        while True:
            try:
                # First, get the message length (4-byte integer)
                data = b""
                length_size = struct.calcsize("!I")

                while len(data) < length_size:
                    packet = client_socket.recv(length_size - len(data))
                    if not packet:
                        break
                    data += packet

                if not data:
                    break

                # Unpack the message length
                msg_length = struct.unpack("!I", data)[0]

                # Now read the actual message
                data = b""
                while len(data) < msg_length:
                    packet = client_socket.recv(min(msg_length - len(data), 4096))
                    if not packet:
                        break
                    data += packet

                if not data:
                    break

                # Forward data to other clients in the same meeting
                header = struct.pack("!I", len(data))
                self.broadcast(header + data, meeting_id, client_socket)

            except Exception as e:
                logger.error(f"Error handling client {client_address}: {str(e)}")
                break

        # Remove client on disconnect
        if meeting_id in self.clients and client_socket in self.clients[meeting_id]:
            self.clients[meeting_id].remove(client_socket)
            if not self.clients[meeting_id]:
                del self.clients[meeting_id]

        client_socket.close()
        logger.info(f"Client {client_address} disconnected from meeting {meeting_id}")

    def start(self):
        """Start the video server"""
        while True:
            try:
                client_socket, addr = self.server_socket.accept()

                # First message should be the meeting ID
                data = client_socket.recv(1024).decode('utf-8')
                meeting_id = data.strip()

                if not meeting_id:
                    client_socket.close()
                    continue

                # Start a new thread to handle this client
                thread = threading.Thread(
                    target=self.handle_client,
                    args=(client_socket, addr, meeting_id),
                    daemon=True
                )
                thread.start()

            except Exception as e:
                logger.error(f"Error accepting connection: {str(e)}")

    def close(self):
        """Close the video server"""
        for meeting_id in self.clients:
            for client in self.clients[meeting_id]:
                try:
                    client.close()
                except:
                    pass
        self.server_socket.close()
        logger.info("Video server closed")