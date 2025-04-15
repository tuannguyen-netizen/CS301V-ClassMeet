import socket
import cv2
import pickle
import struct
import threading
import numpy as np


class VideoCallClient:
    def __init__(self, host='127.0.0.1', port=5000, camera_index=0):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((host, port))
        self.running = True
        self.camera_index = camera_index
        print(f"Connected to {host}:{port}")

    def send_video(self):
        cap = cv2.VideoCapture(self.camera_index)

        if not cap.isOpened():
            print(f"Error: Could not open camera at index {self.camera_index}")
            self.running = False
            return

        while self.running:
            ret, frame = cap.read()
            if not ret:
                print("Failed to capture video frame")
                break

            # Serialize the frame
            data = pickle.dumps(frame)
            message = struct.pack("Q", len(data)) + data
            try:
                self.client_socket.sendall(message)
            except Exception as e:
                print(f"Error sending frame: {e}")
                break

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()

    def receive_video(self):
        data = b""
        payload_size = struct.calcsize("Q")

        while self.running:
            try:
                while len(data) < payload_size:
                    packet = self.client_socket.recv(4096)
                    if not packet:
                        self.running = False
                        break
                    data += packet

                if not self.running:
                    break

                packed_msg_size = data[:payload_size]
                data = data[payload_size:]
                msg_size = struct.unpack("Q", packed_msg_size)[0]

                while len(data) < msg_size:
                    data += self.client_socket.recv(4096)

                frame_data = data[:msg_size]
                data = data[msg_size:]

                frame = pickle.loads(frame_data)
                cv2.imshow("Received", frame)

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    self.running = False
                    break
            except Exception as e:
                print(f"Error receiving frame: {e}")
                self.running = False
                break

    def start(self):
        send_thread = threading.Thread(target=self.send_video)
        receive_thread = threading.Thread(target=self.receive_video)

        send_thread.start()
        receive_thread.start()

        send_thread.join()
        receive_thread.join()

        cv2.destroyAllWindows()
        self.client_socket.close()
        print("Connection closed")


if __name__ == "__main__":
    try:
        # Change the camera_index to the correct one based on your system
        client = VideoCallClient(camera_index=0)  # Try 0, 1, or 2 based on the test script
        client.start()
    except Exception as e:
        print(f"Error: {e}")