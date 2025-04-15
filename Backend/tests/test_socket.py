import unittest
import socket
import cv2
import pickle
import struct
import threading
import numpy as np
from unittest.mock import patch
import time


class VideoCallClient:
    def __init__(self, host='127.0.0.1', port=5000):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((host, port))
        self.running = True
        print(f"Connected to {host}:{port}")

    def send_video(self, frame):
        data = pickle.dumps(frame)
        message = struct.pack("Q", len(data)) + data
        self.client_socket.sendall(message)

    def receive_video(self):
        data = b""
        payload_size = struct.calcsize("Q")

        while self.running:
            while len(data) < payload_size:
                packet = self.client_socket.recv(4096)
                if not packet:
                    return None
                data += packet

            packed_msg_size = data[:payload_size]
            data = data[payload_size:]
            msg_size = struct.unpack("Q", packed_msg_size)[0]

            while len(data) < msg_size:
                data += self.client_socket.recv(4096)

            frame_data = data[:msg_size]
            data = data[msg_size:]

            frame = pickle.loads(frame_data)
            return frame

    def close(self):
        self.running = False
        self.client_socket.close()


class TestVideoCallClient(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Start the VideoCallServer in a separate thread
        from app.video_server import VideoCallServer
        cls.server = VideoCallServer(host='127.0.0.1', port=5000)
        cls.server_thread = threading.Thread(target=cls.server.start, daemon=True)
        cls.server_thread.start()
        time.sleep(1)  # Give the server time to start

    @classmethod
    def tearDownClass(cls):
        # Stop the server
        cls.server.server_socket.close()
        for client in cls.server.clients:
            try:
                client.close()
            except:
                pass

    def setUp(self):
        self.client = VideoCallClient(host='127.0.0.1', port=5000)

    def tearDown(self):
        self.client.close()

    def test_client_connect_and_send_frame(self):
        # Create a dummy frame (a 100x100 black image)
        dummy_frame = np.zeros((100, 100, 3), dtype=np.uint8)

        # Send the frame
        self.client.send_video(dummy_frame)

        # Receive the frame (simulating broadcast from server)
        received_frame = self.client.receive_video()

        # Check if a frame was received
        self.assertIsNotNone(received_frame, "No frame received from server")

        # Check if the received frame has the same shape as the sent frame
        self.assertEqual(received_frame.shape, dummy_frame.shape,
                         "Received frame shape does not match sent frame shape")


if __name__ == '__main__':
    unittest.main()