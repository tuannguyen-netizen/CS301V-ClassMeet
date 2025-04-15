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

    def broadcast(self, frame, sender_socket):
        data = pickle.dumps(frame)
        message = struct.pack("Q", len(data)) + data
        for client in self.clients:
            if client != sender_socket:
                try:
                    client.send(message)
                except:
                    self.clients.remove(client)

    def handle_client(self, client_socket):
        self.clients.append(client_socket)

        while True:
            try:
                data = b""
                payload_size = struct.calcsize("Q")

                while len(data) < payload_size:
                    packet = client_socket.recv(4096)
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
                self.broadcast(frame, client_socket)

            except:
                break

        self.clients.remove(client_socket)
        client_socket.close()

    def start(self):
        while True:
            client_socket, addr = self.server_socket.accept()
            print(f"Connected to {addr}")
            thread = threading.Thread(target=self.handle_client, args=(client_socket,))
            thread.start()


if __name__ == "__main__":
    server = VideoCallServer()
    server.start()