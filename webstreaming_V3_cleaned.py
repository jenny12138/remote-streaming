"""
Necessary imports
"""
import platform # to determine which version of Python is being run
print("This script is run using Python interpreter", platform.python_version()) 
import threading
import argparse
import datetime
import time
import flask
import numpy as np
print("This script is using Numpy version", np.__version__)
from flask import Response, Flask, render_template
import numpy
import cv2
print("This script is using cv2 version", cv2.__version__)

"""
Performing some initializations
"""
lock = threading.Lock() # to prevent race condition; in this case, it ensures that one thread isn't trying to read the frame as it is being updated.
app = Flask(__name__) # initialize a flask object
try:
    camera = cv2.VideoCapture(0) # so that we can use the webcam
    print("Camera opened!")
except:
    print("Camera didn't open!")

#fps = int(camera.get(cv2.CAP_PROP_FPS))
fps = 10 #TODO: figure out fps
resize_width = int(camera.get(cv2.CAP_PROP_FRAME_WIDTH))
print("resize_width is ", resize_width)
resize_height = int(camera.get(cv2.CAP_PROP_FRAME_HEIGHT))
print("resize_height is ", resize_height)
out = cv2.VideoWriter("test.mp4", cv2.VideoWriter_fourcc(*'mp4v'), fps, (resize_width, resize_height))

"""
Function to render the index.html template and serve up the output video stream
"""
@app.route("/") # Decorator that routes you to a specific URL: in this case just /.
def index():
    return render_template("index.html")

def generate_frames():
    global camera, lock, out
    try:
        while True:
            with lock: # wait until the lock is acquired. We need to acquire the lock to ensure the frame variable is not accidentally being read by a client while we are trying to update it.
                success, frame = camera.read() # read the camera frame
                if not success:
                    break
                else:
                    out.write(frame)
                    (flag, encodedImage) = cv2.imencode(".jpg", frame) # encode the frame in JPEG format
                    if not flag: # ensure the frame was successfully encoded
                        continue

            frame_bytes = b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + bytearray(encodedImage) + b'\r\n'
            app.frame_buffer = frame_bytes  # Store the generated frame in the app instance

    except KeyboardInterrupt:
        out.release()
        camera.release()
    
def generate_frames_continuously():
    while True:
        if hasattr(app, 'frame_buffer'):
            yield app.frame_buffer
        else:
            time.sleep(0.1)  # Adjust the delay as needed

"""
Function to use the flask function Response
"""
@app.route("/video_feed")
def video_feed():
    return Response(generate_frames_continuously(),
                    mimetype="multipart/x-mixed-replace; boundary=frame")

"""
Handle parsing commmand line arguments and launch the Flask app
"""
if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--ip", type=str, required=True, help="ip address of the device")
    ap.add_argument("-o", "--port", type=int, required=True, help="ephemeral port number of the server (1024 to 65535)")
    args=vars(ap.parse_args())

    # start a thread that will perform motion detection
    t = threading.Thread(target=generate_frames)
    t.daemon = True
    t.start()

    # start the flask app
    try:
        app.run(host='0.0.0.0', port=args["port"], debug=True, threaded=True, use_reloader=False) # Find the IP address of the Jetson device manually, then replace host=... with that ip address
    finally:
        out.release()
        camera.release()
        print("Resources released.")
    # to find the ip address, use the ifconfig command. Under wlan, the ip address is listed after the "inet" field.

print("End of script.")
