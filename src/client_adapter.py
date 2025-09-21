import socket
import numpy as np
import cv2, json

# constants
CAMERA_HEIGHT : int = 46
CAMERA_WIDTH : int = 52


class ClientAdapter:
    def __init__(self, 
                host = "127.0.0.1",
                camera_port = 5550,
                ps_sensor_port = 5551):
        
        self.host = host
        # CAMERA
        self.camera_port = camera_port
        self.camera_address = (self.host, self.camera_port)
        self.camera_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.camera_socket.connect(self.camera_address)
        self.BUFFER_SIZE = CAMERA_HEIGHT*CAMERA_WIDTH*4
        # PS SENSOR
        self.ps_sensor_port = ps_sensor_port
        self.ps_sensor_address = (self.host, self.ps_sensor_port)
        self.ps_sensor_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ps_sensor_socket.connect(self.ps_sensor_address)
        
          
    def receive_image_frame(self):
        # receving from the camera sensor server
        while True:
            raw_data = b""
            while len(raw_data) < self.BUFFER_SIZE:
                chunk = self.camera_socket.recv(self.BUFFER_SIZE - len(raw_data))
                if not chunk:
                    return
                raw_data += chunk

            image_array = np.frombuffer(raw_data, dtype=np.uint8).reshape((CAMERA_HEIGHT, CAMERA_WIDTH, 4))
            bgr_image = image_array[:, :, :3]
            resized = cv2.resize(bgr_image, (320, 360))
            _, buffer = cv2.imencode('.jpg', resized)
            yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
            

    def receive_ps_sensor_data(self):
        # receiving from the ps sensor server
        while True:
            list_data = b""
            while not list_data.endswith(b"\n"):
                chunk = self.ps_sensor_socket.recv(1024)
                if not chunk:
                    print("Sensor socket closed or no data received")
                    return  # Exit if connection is lost
                list_data += chunk
            try:
                json_str = list_data.decode("utf-8").strip()
                if not json_str:
                    print("Empty sensor data received")
                    continue
                decoded = json.loads(json_str)
                yield decoded
            except json.JSONDecodeError as e:
                # print("JSON decode error:", e)
                # print("Raw string was:", repr(json_str))
                pass

