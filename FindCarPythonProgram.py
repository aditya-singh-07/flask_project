import base64
import json
import os
import ssl
import numpy as np
import cv2
import http.client as httplib
import mysql.connector
import datetime
#import geocoder
#from geolocation.main import GoogleMaps

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="",
  database="vehicle-detection"
)
#google_maps = GoogleMaps(api_key="AIzaSyA0Dx_boXQiwvdz8sJHoYeZNVTdoWONYkU")

def findCar(car_image):

    # Setting the authentication parameters -------------
    headers = {"Content-type": "application/json",
               "X-Access-Token": "6sscGZ7BSOgvVOke1lm4sOwwiLtsGXhZ6Fdo"}
    # ---------------------------------------------------

    # Connecting to the Sighthound API ------------------
    conn = httplib.HTTPSConnection("dev.sighthoundapi.com", 
           context=ssl.SSLContext(ssl.PROTOCOL_TLSv1))
    # ---------------------------------------------------

    # Selecting the image -------------------------------
    # To use a hosted image uncomment the following line and update the URL
    # image_data = "http://example.com/path/to/hosted/image.jpg"

    # To use a local file uncomment the following line and update the path
    image_data = base64.b64encode(open(car_image, "rb").read()).decode()
    # ---------------------------------------------------

    # Preparing a json to send --------------------------
    params = json.dumps({"image": image_data})
    # ---------------------------------------------------

    # Calling a service ---------------------------------
    #conn.request("POST", "/v1/detections?type=face,person&faceOption=landmark,gender", params, headers)
    conn.request("POST", "/v1/recognition?objectType=vehicle,licenseplate", params, headers)
    response = conn.getresponse()
    result = response.read()
    # ---------------------------------------------------

    # Displaying the response ---------------------------
    test = result
    # ---------------------------------------------------
 
    return test

def renderJSON(json_v):
    # ------------------------CAR-------------------------------------------------------

    # Forming Data
    data = {}

    # Car Make
    data["car_make"] = json_v["objects"][0]["vehicleAnnotation"]["attributes"]["system"]["make"]
    print("Car Name :: " + data["car_make"]["name"].upper())
   
    # Car Model
    data["car_model"] = json_v["objects"][0]["vehicleAnnotation"]["attributes"]["system"]["model"]
    print("Car Model :: " + data["car_model"]["name"].upper())

    # Car Color
    data["car_color"] = json_v["objects"][0]["vehicleAnnotation"]["attributes"]["system"]["color"]
    print("Car Color :: " + data["car_color"]["name"].upper())

    # Car Type
    data["car_type"] = json_v["objects"][0]["vehicleAnnotation"]["attributes"]["system"]["vehicleType"]
    print("Vehicle Type :: " + data["car_type"].upper())

    # Number Plate
    data["number_plate"] = json_v["objects"][0]["vehicleAnnotation"]["licenseplate"]["attributes"]["system"]["string"]["name"]
    data["number_plate_top_left"] = json_v["objects"][0]["vehicleAnnotation"]["licenseplate"]["bounding"]["vertices"][0]
    data["number_plate_top_left"] = json_v["objects"][0]["vehicleAnnotation"]["licenseplate"]["bounding"]["vertices"][2]
    print("Number Plate :: " + data["number_plate"].upper())
    
    vehicle_name=data["car_make"]["name"].upper();
    vehicle_model=data["car_model"]["name"].upper();
    vehicle_color=data["car_color"]["name"].upper();
    vehicle_type=data["car_type"].upper();
    vehicle_number_plate=data["number_plate"].upper();
    date=datetime.datetime.now();
     
    if(mydb):
      print("connected with database ")
    mycursor = mydb.cursor()
                        
    sql = "INSERT INTO miniproject2020 (vehicle,model,color,type,number_plate,date_created) VALUES (%(vehicle)s,%(model)s,%(color)s,%(type)s,%(number_plate)s,%(date_created)s)"
    val= {'vehicle':vehicle_name,
    'model': vehicle_model,
    'color': vehicle_color,
    'type': vehicle_type,
    'number_plate': vehicle_number_plate, 
    'date_created': date
    }
    print(val)
    #g = geocoder.ip('me')
    #lat=g.lat
    #lng=g.lng
    #print(lat)
    #print(lng)
    #my_location = google_maps.search(lat=lat, lng=lng).first()
    #print(my_location)
    mycursor.execute(sql, val)
    mydb.commit()
            
    # ------------------------CAR-------------------------------------------------------

    return data

# Car Image to be Processed
car_image = "./uploads/testimage.png"

# Contacting External Server
response = findCar(car_image)

# Converting their Response to JSON
json_response = json.loads(response)

# Processing that JSON for our Parameters
print(json_response)

renderJSON(json_response)
