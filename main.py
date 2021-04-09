import os

from flask import Blueprint, redirect, render_template, request, url_for, flash, Flask
from flask_login import login_required, current_user
from datetime import date
from werkzeug.utils import secure_filename
from .model import User, db, VehicleData

# //////////////////
import base64
import json
import os
import ssl
import numpy as np
import cv2
import http.client as httplib
#import mysql.connector
import datetime
import pathlib

# //////////////////
# mydb = mysql.connector.connect(
#   host="localhost",
#   user="root",
#   password="",
#   database="vehicle-detection"
# )
#google_maps = GoogleMaps(api_key="AIzaSyA0Dx_boXQiwvdz8sJHoYeZNVTdoWONYkU")


app = Flask(__name__)
UPLOAD_FOLDER = './uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


main = Blueprint('main', __name__)


# @main.route('/')
# @login_required
# def index():
#     return render_template('index.html')

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@main.route('/dashboard')
@login_required
def dashboard():
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(email=current_user.email).first_or_404()
    vehicle = user.vehicledata
    vehicle_pagination = VehicleData.query.filter_by(author=user).paginate(page=page, per_page=3)

    return render_template('index.html', data=vehicle_pagination, name=current_user.username)


# @main.route('/dashboard',methods=['GET'])
# @login_required
# def vehicleData():
#     user = User.query.filter_by(email=current_user.email).first_or_404()
#     vehicle=user.vehicledata
#     print(vehicle)
#     return render_template('index.html',data=vehicle,name=current_user.username)

@main.route('/post', methods=['POST'])
@login_required
def vehicle_post():
    vehicle = request.form.get('vehicle')
    model = request.form.get('model')
    color = request.form.get('color')
    type = request.form.get('type')
    numberplate = request.form.get('numberplate')
    date_created = date.today()
    print(vehicle, model, color, type, numberplate, date_created)
    user = User.query.filter_by(email=current_user.email).first_or_404()
    vehicle_post = VehicleData(user.id, vehicle, model, color, type, numberplate, date_created)
    db.session.add(vehicle_post)
    db.session.commit()
    flash("added successfully!!")
    return redirect(url_for('main.dashboard'))


@main.route('/details/<int:vehicle_id>/update', methods=['GET', 'POST'])
@login_required
def vehicle_updates(vehicle_id):
    vehicle_details = VehicleData.query.get_or_404(vehicle_id)
    if request.method == 'POST':
        vehicle_details.vehicle = request.form['vehicle']
        vehicle_details.model = request.form['model']
        vehicle_details.color = request.form['color']
        vehicle_details.type = request.form['type']
        vehicle_details.numberplate = request.form['numberplate']
        vehicle_details.date_created = date.today()
        db.session.add(vehicle_details)
        db.session.commit()
        flash("Successfully updated!!")
        return redirect(url_for('main.dashboard'))
    return render_template('edit.html', vehicle=vehicle_details, name=current_user.username)


@main.route('/details/<int:vehicle_id>/delete', methods=['GET', 'POST'])
@login_required
def vehicle_delete(vehicle_id):
    vehicle_details = VehicleData.query.get_or_404(vehicle_id)
    db.session.delete(vehicle_details)
    db.session.commit()
    flash("Successfully Deleted!!")
    return redirect(url_for('main.dashboard'))


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
    # conn.request("POST", "/v1/detections?type=face,person&faceOption=landmark,gender", params, headers)
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
    data["number_plate"] = json_v["objects"][0]["vehicleAnnotation"]["licenseplate"]["attributes"]["system"]["string"][
        "name"]
    data["number_plate_top_left"] = json_v["objects"][0]["vehicleAnnotation"]["licenseplate"]["bounding"]["vertices"][0]
    data["number_plate_top_left"] = json_v["objects"][0]["vehicleAnnotation"]["licenseplate"]["bounding"]["vertices"][2]
    print("Number Plate :: " + data["number_plate"].upper())

    vehicle_name = data["car_make"]["name"].upper();
    vehicle_model = data["car_model"]["name"].upper();
    vehicle_color = data["car_color"]["name"].upper();
    vehicle_type = data["car_type"].upper();
    vehicle_number_plate = data["number_plate"].upper();
    date = datetime.datetime.now();

    # if (mydb):
    #     print("connected with database ")
    # mycursor = mydb.cursor()
    # sql = "INSERT INTO vehicle_data (user_id,vehicle,model,color,type,number_plate,date_created) VALUES (1,%(vehicle)s,%(model)s,%(color)s,%(type)s,%(number_plate)s,%(date_created)s)"
    # val = {'user_id': "1",
    #        'vehicle': vehicle_name,
    #        'model': vehicle_model,
    #        'color': vehicle_color,
    #        'type': vehicle_type,
    #        'number_plate': vehicle_number_plate,
    #        'date_created': date
    #        }
    sql = VehicleData(current_user.id, vehicle_name, vehicle_model, vehicle_color, vehicle_type, vehicle_number_plate, date)
    db.session.add(sql)
    db.session.commit()
    #print(val)
    # g = geocoder.ip('me')
    # lat=g.lat
    # lng=g.lng
    # print(lat)
    # print(lng)
    # my_location = google_maps.search(lat=lat, lng=lng).first()
    # print(my_location)
    # mycursor.execute(sql, val)
    # mydb.commit()

    # ------------------------CAR-------------------------------------------------------

    return data


@main.route('/uploader', methods=['GET', 'POST'])
@login_required
def upload_file():
    if request.method == 'POST':
        f = request.files['file']
        if f.filename != '':
            filename = secure_filename(f.filename)
            file = pathlib.Path(UPLOAD_FOLDER + "/" + 'testimage.png')
            if file.exists():
                os.remove(UPLOAD_FOLDER + "/" + 'testimage.png')
            f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            os.rename(UPLOAD_FOLDER + "/" + filename, UPLOAD_FOLDER + "/" + 'testimage.png')
            # f.save(secure_filename(f.filename))
            # flash("Uploaded Successfully")
            file = pathlib.Path(UPLOAD_FOLDER + "/" + 'testimage.png')
            if file.exists():
                print("File exist")
                car_image = "./uploads/testimage.png"

                # Contacting External Server
                response = findCar(car_image)

                # Converting their Response to JSON
                json_response = json.loads(response)

                # Processing that JSON for our Parameters
                print(json_response)

                renderJSON(json_response)
                flash("recognized Success")
            else:
                print("File not exist")
            # Car Image to be Processed

            return redirect(url_for('main.dashboard'))
        else:
            flash(" Please select images")
            return redirect(url_for('main.dashboard'))



