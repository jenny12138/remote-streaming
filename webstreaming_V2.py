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
import imutils
from imutils.video import VideoStream
print("This script is using cv2 version", cv2.__version__)

"""
Performing some initializations
"""
outputFrame = None
lock = threading.Lock() # to prevent race condition; in this case, it ensures that one thread isn't trying to read the frame as it is being updated.
app = Flask(__name__) # initialize a flask object
camera = cv2.VideoCapture(0)
time.sleep(5.0) # wait for the camera to warm up. Changed to 5 seconds as it looks like it takes a while for the camera to turn on.

"""
Function to render the index.html template and serve up the output video stream
"""
@app.route("/") # Decorator that routes you to a specific URL: in this case just /.
def index():
    return render_template("index.html")

"""
Function to return a frame
"""
def return_frame():
    # grab global references to the video stream, output frame, and lock variables.
    global camera, outputFrame, lock

    while True:
        with lock: # wait until the lock is acquired
            success, frame = camera.read() # read the camera frame
            if not success:
                break
            else:
                (flag, encodedImage) = cv2.imencode(".jpg", frame) # encode the frame in JPEG format 
                if not flag: # ensure the frame was successfully encoded
                    continue

        yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + bytearray(encodedImage) + b'\r\n') # yield some text and the output frame in the byte format
        # the yield keyword will turn any expression that is given with it into a generator object and return it to the caller. Therefore, you must
        # iterate over the genertor object if you wish to obtain the values stored there.

"""
Function to use the flask function Response
"""
@app.route("/video_feed")
def video_feed():
    return Response(return_frame(), mimetype="multipart/x-mixed-replace; boundary=frame") #MIME type a.k.a. media type: indicates the nature and format of a document, file, or assortment of bytes. MIME types are defined and standardized in IETF's RFC6838. 

"""
Handle parsing commmand line arguments and launch the Flask app
"""
if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--ip", type=str, required=True, help="ip address of the device")
    ap.add_argument("-o", "--port", type=int, required=True, help="ephemeral port number of the server (1024 to 65535)")
    args=vars(ap.parse_args())

    # start a thread that will perform motion detection
    t = threading.Thread(target=return_frame)
    t.daemon = True
    t.start()

    # start the flask app
    #app.run(host=args["ip"], port=args["port"], debug=True, threaded=True, use_reloader=False)
    app.run(host='10.42.0.1', port=args["port"], debug=True, threaded=True, use_reloader=False)

camera.release() # Before ending the script release the camera.
print("End of script.")