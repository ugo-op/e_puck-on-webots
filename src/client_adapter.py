import socket, threading
import numpy as np
import cv2, json
from flask import Flask, Response



CAMERA_HEIGHT : int = 46
CAMERA_WIDTH : int = 52



class ClientAdapter:
    def __init__(self, host = "127.0.0.1", camera_port = 5550, ps_sensor_port = 5551):
        self.host = host
        # CAMERA
        self.camera_port = camera_port
        self.camera_address = (self.host, self.camera_port)
        self.camera_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.camera_socket.connect(self.camera_address)
        # PS SENSOR
        self.ps_sensor_port = ps_sensor_port
        self.ps_sensor_address = (self.host, self.ps_sensor_port)
        self.ps_sensor_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ps_sensor_socket.connect(self.ps_sensor_address)
        
        self.BUFFER_SIZE = CAMERA_HEIGHT*CAMERA_WIDTH*4
        

        
    # def display_camera_output(self):
    #     print("IAM HERE")
    #     while True:
    #         raw_data = self.camera_socket.recv(CAMERA_HEIGHT*CAMERA_WIDTH*4)
    #         image_array = np.frombuffer(raw_data, dtype=np.uint8).reshape((CAMERA_HEIGHT, CAMERA_WIDTH, 4))  # BGRA

    #         # Convert BGRA to BGR (drop alpha channel)
    #         bgr_image = image_array[:, :, :3]  # Keep BGR channels only

    #         # Display using OpenCV
    #         resized_image = cv2.resize(bgr_image, (230, 260))  # or any size you want
    #         #cv2.imshow("Webots Camera", resized_image)
    #     #     if cv2.waitKey(1) & 0xFF == ord('q'):
    #     #         break         
    #     # cv2.destroyAllWindows()
        
        
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
     

    # def read_ps_values(self):
    #     while True:
    #         list_data = b""
    #         while not list_data.endswith(b"\n"):
    #             chunk = self.ps_sensor_socket.recv(1024)
    #             if not chunk:
    #                 print("Sensor socket closed or no data received")
                    
    #             list_data += chunk

    #         try:
    #             json_str = list_data.decode("utf-8").strip()
    #             decoded = json.loads(json_str)
    #             print("Received list:", decoded)
    #         except json.JSONDecodeError as e:
    #             print("JSON decode error:", e)
    #             print("Raw string was:", repr(json_str))

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
                print("JSON decode error:", e)
                print("Raw string was:", repr(json_str))



class WebMonitor(ClientAdapter):
    # This class is in charge of the monitoring the sensor readings in the web
    def __init__(self, host="127.0.0.1", camera_port=5550, ps_sensor_port=5551):
        super().__init__(host, camera_port, ps_sensor_port)
        
    
    def run(self, host='0.0.0.0', port=5000):
        app = Flask(__name__)
        @app.route('/')
        def index():
            return '''
    <html>
    <body>
        <h1>Live Camera Feed</h1>
        <img src="/camera" style="border:1px solid black;"><br><br>
        <h2>Proximity Sensor Readings: [ps0, ps1, ps2, ps3, ps4, ps5, ps6, ps7]</h2>
        <pre id="sensor-output" style="
            font-size: 1.5em;
            padding: 10px;
            border: 1px solid #ccc;
            background-color: #f9f9f9;
            width: 80%;
            max-height: 300px;
            overflow-y: auto;
        ">Waiting for data...</pre>

        <script>
        const sensorOutput = document.getElementById("sensor-output");
        const evtSource = new EventSource("/ps_sensor");
        evtSource.onmessage = function(event) {
            sensorOutput.textContent = event.data;
        };
        </script>
    </body>
    </html>
    '''

        @app.route('/camera')
        def video():
            return Response(self.receive_image_frame(), mimetype='multipart/x-mixed-replace; boundary=frame')
        
        @app.route('/ps_sensor')
        def ps_sensor():
            def stream_sensor_data():
                for data in self.receive_ps_sensor_data():  # This should yield dicts
                    yield f"data: {json.dumps(data)}\n\n"
            return Response(stream_sensor_data(), mimetype='text/event-stream')

        app.run(host,port)
                
