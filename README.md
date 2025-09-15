
# E-Puck Keyboard Controller & Sensor Monitor  

## Introduction  

This project demonstrates the integration of a **keyboard controller** with a **sensor monitoring system** (camera and distance sensors) for the [E-puck robot](https://www.cyberbotics.com/doc/guide/tutorial-4-more-about-controllers) in the [Webots](https://cyberbotics.com/) simulation environment.  
A client application provides live streaming of the robot’s camera feed and distance sensor values via a browser-based interface.  

---

## Features  

- Real-time **keyboard control** of the E-puck robot.  
- **Camera streaming** directly from the Webots simulation and **Distance sensor values visualization** in a browser.  
- Adjustable **speed control** (increase/decrease).  
- Lightweight, modular design for **easy extension**.  
- Image Frames can be saved as ML training dataset.

---

## Dependencies  

- [Webots](https://cyberbotics.com/)  
- [Flask](https://flask.palletsprojects.com/en/stable/)  
- [NumPy](https://numpy.org/)  
- [OpenCV](https://opencv.org/)  
- Python 3.9+  

---

## Usage Summary  

1. **Clone the repository**  
   ```bash
   git clone https://github.com/your-username/e_puck-on-webots.git
   
    Install Webots
    Download and install Webots

## **Demo**

```bash
# Step 1: Launch Webots
webots
# From the GUI, open the world file
# (e.g., /worlds/my_world.wbt)

# Step 2: Start the Client
./src/run_client.sh
# This will display a URL in the terminal

# Step 3: Access the Interface
# Open the displayed URL in your browser to view:
# - Live camera feed
# - Real-time distance sensor values

# Step 4: Control the Robot
# Use the keyboard to control the robot (see instructions below)


    Control Keys

        Arrow Keys

            ⬆️ Up → Move Forward

            ⬇️ Down → Move Backward

            ⬅️ Left → Turn Left

            ➡️ Right → Turn Right

        Speed Adjustment

            CTRL + A → Increase speed

            CTRL + D → Decrease speed

## Future Work  
A possible extension of this project is to use the keyboard controller for **manual obstacle avoidance** while simultaneously generating image frames and corresponding action policies.  
The collected images, paired with their action labels, can then serve as **training data for supervised learning**.  
This approach could lead to the development of a controller capable of **autonomously avoiding collisions**.  

**Note:**  
The existing obstacle avoidance controllers for the E-puck in Webots often **collide with obstacles before initiating a turn**.  

