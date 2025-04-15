import socket
import cv2
import pickle
import struct
import threading


class VideoCallServer:
    def __init__(self, host='0.0.0.0', port=5000):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((host, port))
        self.server_socket.listen(5)
        self.clients = []
        print(f"Server started on {host}:{port}")

    def broadcast(self, data, sender_socket):
        # Broadcast the data (either a video frame or a text message) to all other clients
        for client in self.clients:
            if client != sender_socket:
                try:
                    client.send(data)
                except:
                    self.clients.remove(client)

    def handle_client(self, client_socket):
        self.clients.append(client_socket)

        while True:
            try:
                # First, check for a 4-byte message length (for text messages)
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
                    packet = client_socket.recv(msg_length - len(data))
                    if not packet:
                        break
                    data += packet

                if not data:
                    break

                # Try to decode the message as text (assuming it's a text message)
                try:
                    message = data.decode('utf-8')
                    print(f"Received text message: {message}")
                    # Broadcast the text message (repack the length and message)
                    broadcast_data = struct.pack('!I', len(data)) + data
                    self.broadcast(broadcast_data, client_socket)
                except UnicodeDecodeError:
                    # If it's not a text message, assume it's a video frame (original format)
                    # For video frames, the server expects a 'Q' format (8 bytes) for the length
                    # Since we've already consumed 4 bytes, we need to adjust
                    # This is a fallback for compatibility with the original video frame format
                    data = b""
                    payload_size = struct.calcsize("Q")

                    while len(data) < payload_size:
                        packet = client_socket.recv(payload_size - len(data))
                        if not packet:
                            break
                        data += packet

                    if not data:
                        break

                    packed_msg_size = data[:payload_size]
                    data = data[payload_size:]
                    msg_size = struct.unpack("Q", packed_msg_size)[0]

                    while len(data) < msg_size:
                        data += client_socket.recv(4096)

                    frame_data = data[:msg_size]
                    data = data[msg_size:]

                    frame = pickle.loads(frame_data)
                    print("Received a video frame")
                    # Broadcast the video frame
                    broadcast_data = struct.pack("Q", len(frame_data)) + frame_data
                    self.broadcast(broadcast_data, client_socket)

            except Exception as e:
                print(f"Error handling client: {e}")
                break

        self.clients.remove(client_socket)
        client_socket.close()

    def start(self):
        while True:
            client_socket, addr = self.server_socket.accept()
            print(f"Connected to {addr}")
            thread = threading.Thread(target=self.handle_client, args=(client_socket,))
            thread.start()