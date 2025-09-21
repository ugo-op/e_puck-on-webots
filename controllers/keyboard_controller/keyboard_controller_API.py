# Keyboard controller API which as well sends sensor readings in real time to a client

from controller import Robot, Keyboard # type:ignore
import json, threading
from server import CameraServer, ProximitySensorServer



class E_Puck_KeyBoardController(Robot):
    def __init__(self):
        super(E_Puck_KeyBoardController, self).__init__()
        self.TIME_STEP = int(self.getBasicTimeStep())
        self.default_MAX_SPEED = 7.50
        self.factor = 0.50 # serve as default
        self.MAX_SPEED = self.default_MAX_SPEED
        self.keyboard = self._init_keyboard()
        self.gps = self.getDevice("gps")
        self.right_motor, self.left_motor = self._init_motors()
        self.camera = self._init_camera()
        # init servers
        self.camera_server = CameraServer()
        self.proximity_sensor_server = ProximitySensorServer()
        threading.Thread(target=self._camera_connect_to_client, daemon=True).start()
        threading.Thread(target=self._ps_sensor_connect_to_client, daemon=True).start()
        
        # for saving image frames, # change to your preferred directory
        #self.base_dir = "/home/ugochukwu/Documents/my_project/images" 
              
    def _camera_connect_to_client(self):
        self.camera_connection = self.camera_server.establish_connection()
        print("Camera connection established")
        
    def _ps_sensor_connect_to_client(self):
        self.ps_sensor_connection = self.proximity_sensor_server.establish_connection()
        print("PS Sensor connection established")
          
    def _init_keyboard(self):
        keyboard = Keyboard()
        keyboard.enable(self.TIME_STEP)
        return keyboard
    
    def _init_motors(self):
        right_motor = self.getDevice("right wheel motor")
        left_motor = self.getDevice("left wheel motor")
        right_motor.setPosition(float('inf'))
        left_motor.setPosition(float('inf'))
        right_motor.setVelocity(0)
        left_motor.setVelocity(0)
        return right_motor, left_motor
    
    def _init_camera(self):
        camera = self.getDevice("camera")
        camera.enable(self.TIME_STEP)
        return camera
               
    def set_robot_max_speed(self, speed):
        self.MAX_SPEED = speed
        
    def get_robot_max_speed(self):
        return self.MAX_SPEED
    
    def get_proximity_sensor_values(self):
        ps = []
        psNames = ['ps0','ps1','ps2','ps3','ps4','ps5','ps6','ps7']
        psValues = []
        for i in range(8):
            ps.append(self.getDevice(psNames[i]))
            ps[i].enable(self.TIME_STEP)
            value = ps[i].getValue()
            psValues.append(value)
        return psValues
            
    # called in a loop
    # def _save_images(self, frame_id, action_label):
    #     # function to save camera images in a directory 
    #     # saved images are labelled _ can serve as a training dataset
        
    #     # create subdirectories
    #     image_dir = os.path.join(self.base_dir, "camera_data")
    #     label_dir = os.path.join(self.base_dir, "labels")
    #     os.makedirs(image_dir, exist_ok=True)
    #     os.makedirs(label_dir, exist_ok=True)

    #     # save image
    #     file_name = os.path.join(image_dir, f"image_{frame_id}.png")
    #     self.camera.saveImage(file_name, 100)

    #     # save label
    #     label_file = os.path.join(label_dir, "labels.csv")
    #     if not os.path.exists(label_file):
    #         with open(label_file, "w") as f:
    #             f.write("frame_id,filename,label\n")

    #     with open(label_file, "a") as f:
    #         f.write(f"{frame_id},image_{frame_id}.png,{action_label}\n")

        
    # key entry functions -> right_motor_speed, left_motor_speed
    def _move_right(self):
        return -self.factor * self.MAX_SPEED, self.factor * self.MAX_SPEED

    def _move_left(self):
        return self.factor * self.MAX_SPEED, -self.factor * self.MAX_SPEED

    def _move_forward(self):
        return self.factor * self.MAX_SPEED, self.factor * self.MAX_SPEED

    def _move_backward(self):
        return -self.factor * self.MAX_SPEED, -self.factor * self.MAX_SPEED
    
    def _increase_speed(self):
        if self.factor < 1:
            self.factor += 0.1
        else:
            self.factor = 1
    
    def _decrease_speed(self):
        if self.factor >= 0.2:
            self.factor -= 0.1
        else:
            self.factor = 0.1
    
    #-------------------------------run method---Entry point of the controller-------------------------------------------#
    
    def run(self):
        #frame_id = 0
        while self.step(self.TIME_STEP) != -1:
            
            key = self.keyboard.getKey()
             # default motor state
             
            action = "stop"
            right_motor_speed, left_motor_speed = 0.0, 0.0

            if key == Keyboard.LEFT:
                action = "left"
                right_motor_speed, left_motor_speed = self._move_left()   
            elif key == Keyboard.RIGHT:
                action = "right"
                right_motor_speed, left_motor_speed = self._move_right()    
            elif key == Keyboard.UP:
                action = "forward"
                right_motor_speed, left_motor_speed = self._move_forward()    
            elif key == Keyboard.DOWN:
                action = "backward"
                right_motor_speed, left_motor_speed = self._move_backward()   
            elif key == Keyboard.CONTROL+ord("A"):
                self._increase_speed()
                print(f"Speed +++ ->: {self.factor*self.MAX_SPEED}")      
            elif key == Keyboard.CONTROL+ord("D"):
                self._decrease_speed()
                print(f"Speed --- ->: {self.factor*self.MAX_SPEED}")
                
            # to save labelled images (can be used for model training)
            #self._save_images(frame_id, action)  
            
            # actuate
            self.right_motor.setVelocity(right_motor_speed)
            self.left_motor.setVelocity(left_motor_speed)
            
            try:
                # send image frames to the client
                image_byte = self.camera.getImage()
                self.camera_connection.sendall(image_byte)
                
                # send proximity sensor values to the client
                values = self.get_proximity_sensor_values()
                values_json = json.dumps(values) + "\n"
                values_bytes = values_json.encode()
                self.ps_sensor_connection.sendall(values_bytes)
            except Exception:
                #print("Waiting for the client to connect")
                pass
            #frame_id += 1
            