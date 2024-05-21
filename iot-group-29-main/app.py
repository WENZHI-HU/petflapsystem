from flask import Flask, render_template, redirect, url_for, send_from_directory, request
import grovepi
import threading
import datetime
import time
import os
import cv2
from imutils.video.pivideostream import PiVideoStream
from concurrent.futures import ThreadPoolExecutor
from camera_singleton import CameraSingleton 
from flask import request
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import random
import sys
import math
import json
import smbus
from grovepi import dht


#Flask application settings
app = Flask(__name__)
executor = ThreadPoolExecutor(max_workers=2)
UPLOAD_FOLDER = '/home/pi/Desktop/photos'

#Hardware port configuration
ultrasonic_port = 7  #Ultrasonic sensor port
buzzer_port = 8      #buzzer port
grovepi.pinMode(buzzer_port, "OUTPUT")  #Set the buzzer port as output
temp_sensor_port = 2  #Temperature and humidity sensor port
#Hardware operation function
def read_distance():
    return grovepi.ultrasonicRead(ultrasonic_port)





DISPLAY_RGB_ADDR = 0x62
DISPLAY_TEXT_ADDR = 0x3e


bus = smbus.SMBus(1)  
def textCommand(cmd):
    bus.write_byte_data(DISPLAY_TEXT_ADDR, 0x80, cmd)
def setText(text):

    textCommand(0x01)  #clear display
    time.sleep(0.05)
    textCommand(0x08 | 0x04) #Turn on the LCD display and turn off the cursor
    textCommand(0x28) #2 lines display
    time.sleep(0.05)
    
    #Since the LCD can only display 16 characters, the text needs to be truncated or continued on the second line
    count = 0
    row = 0
    for char in text:
        if char == '\n' or count == 16:
            count = 0
            row += 1
            if row == 2:
                break
            textCommand(0xc0) #move to next line
            if char == '\n':
                continue
        count += 1
        bus.write_byte_data(DISPLAY_TEXT_ADDR, 0x40, ord(char))
#Set backlight color
def setRGB(r,g,b):
    bus.write_byte_data(DISPLAY_RGB_ADDR,0,0)
    bus.write_byte_data(DISPLAY_RGB_ADDR,1,0)
    bus.write_byte_data(DISPLAY_RGB_ADDR,0x08,0xaa)
    bus.write_byte_data(DISPLAY_RGB_ADDR,4,r)
    bus.write_byte_data(DISPLAY_RGB_ADDR,3,g)
    bus.write_byte_data(DISPLAY_RGB_ADDR,2,b)


def read_temperature():
    try:
        [temp, hum] = dht(temp_sensor_port, 0)  #0 for DHT11, 1 for DHT22
        return temp, hum
    except IOError:
        print("Error reading temperature")
        return None, None



def change_lcd_color():
    current_time = datetime.datetime.now()
    if current_time.hour < 12:
        greetings = 'Good Morning'
    elif 12 <= current_time.hour < 18:
        greetings = 'Good afternoon'
    else:
        greetings = 'Good evening'
        
    temp, hum = read_temperature() 
    
    

    #Define messages to display
    messages = [greetings, f"Temp: {temp}C", f"Humidity: {hum}%","PET FLAP SYSTEM IS WORKING..."]
    while True:
        for message in messages:
            setText(message)
            #Randomly generate colors
            r = random.randint(0, 255)
            g = random.randint(0, 255)
            b = random.randint(0, 255)
            #set lcd color
            setRGB(r, g, b)
            #Pause for a period of time, long enough for the user to see the information clearly
            time.sleep(10)

def notify_user():
    grovepi.digitalWrite(buzzer_port, 1)  #Turn on the buzzer
    time.sleep(0.5)                      #The buzzer sounds for 0.5 seconds
    grovepi.digitalWrite(buzzer_port, 0)  #Turn off the buzzer
    
def capture_photo():
    camera = CameraSingleton()
    base_folder = os.path.expanduser(UPLOAD_FOLDER)
    if not os.path.exists(base_folder):
        os.makedirs(base_folder)
    frame = camera.get_frame()
    timestamp = datetime.datetime.now()
    filename = f"{timestamp.strftime('%Y%m%d_%H%M%S')}.jpg"
    filepath = os.path.join(base_folder, filename)
    cv2.imwrite(filepath, frame)
    print(f"Photo taken and saved: {filepath}")


def live_stream():
    camera = CameraSingleton()
    if not camera.camera:
        print("Camera not initialized")
        return
    cv2.namedWindow("Live Stream", cv2.WINDOW_AUTOSIZE)
    start_time = time.time()
    try:
        while time.time() - start_time < 10:
            frame = camera.get_frame()
            if frame is None:
                print("No frame to display")
                break
            cv2.imshow("Live Stream", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    finally:
        cv2.destroyAllWindows()
        camera.stop_camera()
    print("Live stream ended")

sensor_active = False
def sensor_loop():
    global sensor_active
    camera = CameraSingleton()
    camera.start_camera()
    sensor_active = True  #enable sensor
    while sensor_active:  #Use sensor_active to control the loop
        try:
            distance = grovepi.ultrasonicRead(ultrasonic_port)
            print("Distance:", distance, "cm")

            if distance < 5 and sensor_active:  #Check if the sensor is still active
                capture_photo()
                print("Distance less than 5cm, starting live stream for 10 seconds...")
                notify_user()
                #Rgb lcd.set white()
                live_stream()
                #Rgb lcd.turn off()

            time.sleep(1)

        except TypeError as e:
            print("Type Error:", e)
        except IOError as e:
            print("IO Error:", e)
    camera.stop_camera()  #The loop ends and the camera is turned off
    print("Sensor loop stopped")

def create_email_html(name):
    #Generate HTML content with images from the UPLOAD_FOLDER
    images_html = ""
    for image_filename in os.listdir(UPLOAD_FOLDER):
        image_path = os.path.join(UPLOAD_FOLDER, image_filename)
        images_html += f'<img src="cid:{image_filename}" style="width:100px; height:auto;">'

    html_content = f"""
    <html>
        <head>
          <style>
            body {{
            font-family: Arial, sans-serif;
            background-color: #007bff;
            color: #333333;
            margin: 0;
            padding: 0;
            }}
            .container {{
            max-width: 600px;
            margin: 20px auto;
            padding: 20px;
            background-color: #ffffff;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            }}
            .header {{
            background-color: #0abdf0;
            padding: 10px 20px;
            text-align: center;
            border-radius: 8px 8px 0 0;
            }}
            .header img {{
            max-height: 80px;
            }}
            .content {{
            padding: 20px;
            }}
            .footer {{
            text-align: center;
            padding: 10px 20px;
            background-color: #f2f2f2;
            border-radius: 0 0 8px 8px;
            font-size: 12px;
            }}
          </style>
        </head>
        <body>
        <div class="container">
            <div class="header">
                <img src="{{url_for('static', filename='catcam.png')}}" alt="Pet Flap Logo" class="logo-image">
            </div>
            <div class="content">
                <h1>Welcome to Pet Flap</h1>
                <p>Hello there!</p>
                <p>Welcome to Pet Flap. We're thrilled to have you aboard.</p>
                <p>Keep track of your pet's in and out activity effortlessly.</p>
                {images_html}
            </div>
            <div class="footer">
            <p>Thank you for choosing Pet Flap.</p>
            </div>
        </div>
        </body>
    </html>
    """
    return html_content


def send_email(recipient, subject, html_content):
    sender = "arimakana114514@gmail.com"
    password = "qdtqqwepeqghxjzq"
    msg = MIMEMultipart('related') 
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = recipient
    msg_alternative = MIMEMultipart('alternative')
    msg.attach(msg_alternative)
    part_html = MIMEText(html_content, 'html')
    msg_alternative.attach(part_html)

    #Attach images with explicit MIME types
    for image_filename in os.listdir(UPLOAD_FOLDER):
        image_path = os.path.join(UPLOAD_FOLDER, image_filename)
        with open(image_path, 'rb') as file:
            file_data = file.read()
            content_type = 'image/jpeg'  #Default to JPEG
            if image_filename.lower().endswith('.png'):
                content_type = 'image/png'
            elif image_filename.lower().endswith('.gif'):
                content_type = 'image/gif'
            
            msg_image = MIMEImage(file_data, _subtype=content_type.split('/')[-1])
            msg_image.add_header('Content-ID', f'<{image_filename}>')
            msg_image.add_header('Content-Disposition', 'inline', filename=image_filename)
            msg.attach(msg_image)

    #Send the email
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender, password)
        server.sendmail(sender, recipient, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False


    

#Flask route definition
@app.route('/')
def index():
    currentTime = datetime.datetime.now()
    #Greeets users :D
    if currentTime.hour < 12:
        greetings = 'Good Morning'
    elif 12 <= currentTime.hour < 18:
        greetings = 'Good afternoon'
    else:
        greetings = 'Good evening'
    return render_template('index.html', greetings=greetings)

@app.route('/start_sensors', methods=['POST'])
def start_sensors():
    thread = threading.Thread(target=sensor_loop)
    thread.daemon = True  #Set it as a daemon thread so that the thread will also exit when the main program exits.
    thread.start()
    return redirect(url_for('index'))  #Redirect to homepage after starting thread

def sensor_check():
    while True:
        distance = read_distance()
        if distance < 5:  #If the distance is less than 20 cm
            notify_user()
            break
        time.sleep(1)


@app.route('/stop_sensors', methods=['POST'])
def stop_sensors():
    global sensor_active
    sensor_active = False  #Set the flag to False to notify the loop to stop
#Wait for a while to give sensor_loop a chance to respond and exit
    time.sleep(2)  
    cv2.destroyAllWindows()  #Close all open cv windows
    camera = CameraSingleton()
    if camera.camera:  #If the camera is running, stop it
        camera.stop_camera()
    print("Sensors and live stream stopped")
    return redirect(url_for('images'))



@app.route('/start_camera_actions', methods=['POST'])
def start_camera_actions():
    camera = CameraSingleton()
    if not camera.camera:
        camera.start_camera()
    capture_photo()  #Call the camera function
    return live_stream()  #Call the video streaming function and return its response

@app.route('/image')
def images():
    image_names = os.listdir(UPLOAD_FOLDER)
    return render_template('image.html', images=image_names)

@app.route('/send_image/<filename>')
def send_image(filename):
    #Ensure that the call result of send_from_directory is returned correctly
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route('/delete_image/<filename>', methods=['POST'])
def delete_image(filename):
    #deletes images
    base_folder = os.path.expanduser(UPLOAD_FOLDER)
    filepath = os.path.join(base_folder, filename)
    if os.path.exists(filepath):
        os.system(f'rm {filepath}')
    return redirect(url_for('images'))


@app.route('/send_email_form', methods=['POST'])
def send_email_form():
    if request.method == 'POST':
        recipient_email = request.form['email']
        subject = "Your Pet's Activity Snapshot"
        html_content = create_email_html("Pet Owner")
    if send_email(recipient_email, subject, html_content):
        return "Email sent successfully!"
    else:
        return "Failed to send email."


if __name__ == '__main__':
    color_thread = threading.Thread(target=change_lcd_color)
    color_thread.daemon = True  #Set thread as daemon thread
    color_thread.start()
    app.run(host='0.0.0.0', port=3000, debug=True, threaded=True)