from flask import Flask, Response
import socket
import numpy as np
import cv2

app = Flask(__name__)

CAMERA_HEIGHT = 46
CAMERA_WIDTH = 52
BUFFER_SIZE = CAMERA_HEIGHT * CAMERA_WIDTH * 4

# Connect to the same server
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(("127.0.0.1", 5550))

def receive_frame():
    while True:
        raw_data = b""
        while len(raw_data) < BUFFER_SIZE:
            chunk = client_socket.recv(BUFFER_SIZE - len(raw_data))
            if not chunk:
                return
            raw_data += chunk

        image_array = np.frombuffer(raw_data, dtype=np.uint8).reshape((CAMERA_HEIGHT, CAMERA_WIDTH, 4))
        bgr_image = image_array[:, :, :3]
        resized = cv2.resize(bgr_image, (640, 720))
        _, buffer = cv2.imencode('.jpg', resized)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

@app.route('/')
def index():
    return '<html><body><h1>Live Camera Feed</h1><img src="/video"></body></html>'

@app.route('/video')
def video():
    return Response(receive_frame(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
