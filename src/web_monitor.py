from flask import Flask, Response
from client_adapter import ClientAdapter
import json


class WebMonitor(ClientAdapter):
    # This hosts the sensor readings in the web _ for monitoring
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
                
