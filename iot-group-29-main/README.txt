Smart Pet Flap System

Introduction
This application controls a Smart Pet Flap system designed to monitor and interact with pets as they enter and leave your home. The system uses a Raspberry Pi, various Grove sensors, and a camera to detect the pet’s movement, capture photos, and notify the owner through visual indicators and email alerts.

Features
Ultrasonic Distance Measurement: Detects pet presence as they pass through the flap.
Buzzer Notifications: Alerts nearby individuals when a pet passes through.
Live Streaming: Provides a live video feed of the pet flap area.
Temperature and Humidity Monitoring: Keeps track of environmental conditions.
Email Notifications: Sends an email with photos of the pet as they pass through the flap.
Interactive LCD Display: Shows greetings, temperature, humidity, and system status messages with changing background colors.

Hardware Components
Raspberry Pi: Main controller of the system.
GrovePi Board: Interface for the sensors and actuators.
Ultrasonic Sensor (Grove): Measures the distance to detect if the pet is near the flap.
Buzzer (Grove): Provides audible alerts.
RGB Backlight LCD (Grove): Displays system status and environmental conditions.
DHT Sensor (Grove): Measures temperature and humidity.
Pi Camera: Captures images of the pet.

Software and Libraries
Flask: Python web framework used for creating the web interface.
OpenCV (cv2): For camera operations and live video streaming.
GrovePi: Library to interact with the sensors and actuators on the GrovePi board.
SMBus: For communication with I2C devices, particularly the RGB LCD.
imutils: Utilities to make basic image processing functions such as translation, rotation, resizing, skeletonization, and displaying Matplotlib images easier with OpenCV.
Concurrent.futures: For running asynchronous tasks.
smtplib, email.mime: Sending emails with attached images.
JSON: Handling data storage and configuration.

Installation
Set up your Raspberry Pi with the latest version of Raspberry Pi OS.
Connect the hardware components as described in the Hardware Components section.

Install the necessary Python libraries:

pip install Flask opencv-python-headless grovepi smbus imutils concurrent.futures

git clone [repository-url]
cd [project-folder]
python3 app.py


Usage
Access the web interface via http://<raspberry-pi-ip-address>:3000.
Interact with the system through the provided web interface to view live streams, captured images, and send emails.
Configuration
Ensure all sensors and components are correctly connected to the GrovePi board as per the designated ports in the code. Configure your SMTP settings in the application to use the email functionality.

Troubleshooting
Sensor Not Responding: Check the connections and ensure the correct port numbers are used in the code.
Camera Issues: Verify that the Pi Camera is correctly enabled in the Raspberry Pi configuration settings.

