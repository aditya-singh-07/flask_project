#import libraries of python opencv
import cv2
import numpy as np
import json
from FindCarPythonProgram import *

def snapshot(frame, ctr):
    cv2.imwrite("Snapshots/ss" + str(ctr) + ".jpg", frame)
    cv2.putText(frame, "Taking Snapshot" , (15,15), font, 0.5,(255,255,255),1)
    cv2.imshow('Vehicle Detection System - Snapshot Screen',frame)
    return True

font = cv2.FONT_HERSHEY_SIMPLEX

# create VideoCapture object ---------------------------------------------

#IF WANT TO CAPTURE FROM PRE-RECORDED VIDEO
cap = cv2.VideoCapture('video\cars4.mp4')

#IF WANT TO CAPTURE FROM LIVE VIDEO CAM
#cap = cv2.VideoCapture(0)

# ------------------------------------------------------------------------

#use trained cars XML classifiers ----------------------------------------

car_cascade = cv2.CascadeClassifier('cars4.xml')

# ------------------------------------------------------------------------

# infinite loop capture frame by frame video stream input ----------------
ctr = 0

# Turn to TRUE to send stream to API
carRecogMode = True

while True:
    
    #capture frame by frame ---------------------
    ret, frame = cap.read()
    #frame = cv2.rotate(frame ,cv2.cv2.ROTATE_90_CLOCKWISE)
    #frame = cv2.rotate(frame, cv2.ROTATE_180)
    #frame = rotateImage(frame, 180+90)
    #gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    #flipped = cv2.flip(gray, flipCode = 1)
    #flipped = cv2.rotate(flipped, cv2.cv2.ROTATE_90_CLOCKWISE)
    #flipped = cv2.rotate(src, cv2.ROTATE_180) 
    
    
    # Contacting External Server
    #cv2.imshow('something',frame)
    cv2.imwrite("Frames/f"+str(ctr)+".jpg", frame)
    response = findCar("Frames/f"+str(ctr)+".jpg")

    # Converting their Response to JSON
    json_response = json.loads(response)

    # Processing that JSON for our Parameters
    # print(json_response)
    data = renderJSON(json_response)
                
    if data["car_color"] != False:
        cv2.putText(frame,data["car_color"]["name"], (10,60), font, 1,(0,0,0),3)
        print(data["car_color"]["name"])

    if data["number_plate"] != False:
        #LPN
        cv2.putText(frame, str(data["number_plate"]), (10,100), font, 1,(255,146,0),3)
        print(str(data["number_plate"]))
        
        
    #display the resulting frame
    #cv2.imshow('Vehicle Detection System - Live Camera Footage', frame)
    ctr = ctr + 1

    #-------------------------------------------
        
    #press Q on keyboard to exit---------------
    c = cv2.waitKey(25)
    #print("NOT EXITING: Q is not Pressed!")
        
    if c== ord('q'):
        #print("EXITING: Q is Pressed!")
        break
    if c== ord('s'):
        snapshot(frame, ctr)
    #-------------------------------------------
    
# ------------------------------------------------------------------------
       
#release the videocapture object
cap.release()
#close all the frames
cv2.destroyAllWindows()

