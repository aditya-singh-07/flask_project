import os
import socket
import time

import mysql
from flask import Blueprint, redirect, render_template, request, url_for, flash, Flask, jsonify, Response
from flask_login import login_required, current_user
from datetime import date
from werkzeug.utils import secure_filename
from .model import User, db, VehicleData, Activitylog

# //////////////////
import base64
import json
import os
import ssl
import numpy as np
import cv2
import http.client as httplib
import mysql.connector
from datetime import datetime, timedelta
import pathlib

# //////////////////
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="vehicle-detection"
)
# google_maps = GoogleMaps(api_key="AIzaSyA0Dx_boXQiwvdz8sJHoYeZNVTdoWONYkU")


app = Flask(__name__)
UPLOAD_FOLDER = './uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4'}
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
    global page_global, user_global, vehicle_global, vehicle_pagination_global, week_count, active_count
    page_global = request.args.get('page', 1, type=int)
    user_global = User.query.filter_by(email=current_user.email).first_or_404()
    vehicle_global = user_global.vehicledata
    vehicle_pagination_global = VehicleData.query.filter_by(author=user_global).paginate(page=page_global, per_page=3)
    now = datetime.now()
    week_ago = now - timedelta(hours=8)
    total_visit_today = now - timedelta(hours=12)

    week_count = VehicleData.query.filter(VehicleData.date_created > week_ago).filter(
        VehicleData.date_created < now).count()
    active_count = Activitylog.query.filter(Activitylog.date_updated <= total_visit_today).count()
    if camera is None or not camera.isOpened():
        print(" Camera not working")
    if request.method == 'GET':
        user_log = User.query.filter_by(email=current_user.email).first_or_404()
        count_log = Activitylog.query.filter_by(author=user_log).count()
        return render_template('index.html', count=week_count, log=count_log, active=active_count,
                               data=vehicle_pagination_global, name=current_user.username)


@main.route('/stop')
@login_required
def video_stop():
    hide = False
    user_log = User.query.filter_by(email=current_user.email).first_or_404()
    count_log = Activitylog.query.filter_by(author=user_log).count()
    return render_template('index.html', hidden=hide, count=week_count, log=count_log, data=vehicle_pagination_global,
                           name=current_user.username)


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
    vehicle_post = VehicleData(current_user.id, vehicle, model, color, type, numberplate, date_created)
    change = "Added Vehicle"
    log = Activitylog(current_user.id, current_user.username, change, "192.168.0.1", date_created)
    db.session.add(log)
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
        change = "Updated Vehicle "
        hostname = socket.gethostname()
        IP = socket.gethostbyname(hostname)
        log = Activitylog(current_user.id, current_user.username, change, IP, date.today())
        db.session.add(log)
        db.session.add(vehicle_details)
        db.session.commit()
        flash("Successfully updated!!")
        return redirect(url_for('main.dashboard'))
    now = datetime.now()
    week_ago = now - timedelta(hours=8)
    page_log = request.args.get('page', 1, type=int)
    user_log = User.query.filter_by(email=current_user.email).first_or_404()
    vehicle_log = user_log.activitylog
    vehicle_pagination_log = Activitylog.query.filter_by(author=user_log).count()
    count_log = Activitylog.query.filter_by(author=user_log).count()
    return render_template('edit.html', count=week_count, log=count_log, active=active_count, vehicle=vehicle_details,
                           name=current_user.username)


@main.route('/details/<int:vehicle_id>/delete', methods=['GET', 'POST'])
@login_required
def vehicle_delete(vehicle_id):
    vehicle_details = VehicleData.query.get_or_404(vehicle_id)
    db.session.delete(vehicle_details)
    change = "Deleted Vehicle "
    hostname = socket.gethostname()
    IP = socket.gethostbyname(hostname)
    log = Activitylog(current_user.id, current_user.username, change, IP, date.today())
    db.session.add(log)
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
    date = datetime.now();

    if (mydb):
        print("connected with database ")
    mycursor = mydb.cursor()
    sql = "INSERT INTO vehicle_data(user_id,vehicle,model,color,type,number_plate,date_created) VALUES (4,%(vehicle)s,%(model)s,%(color)s,%(type)s,%(number_plate)s,%(date_created)s)"
    val = {
        'vehicle': vehicle_name,
        'model': vehicle_model,
        'color': vehicle_color,
        'type': vehicle_type,
        'number_plate': vehicle_number_plate,
        'date_created': date
    }

    # sql = VehicleData(4, vehicle_name, vehicle_model, vehicle_color, vehicle_type, vehicle_number_plate, date)
    change = "Recognized Vehicle "
    hostname = socket.gethostname()
    IP = socket.gethostbyname(hostname)
    log = Activitylog(4, current_user.username, change, IP, date.today())
    db.session.add(log)
    # db.session.add(sql)
    db.session.commit()
    # print(val)
    # g = geocoder.ip('me')
    # lat=g.lat
    # lng=g.lng
    # print(lat)
    # print(lng)
    # my_location = google_maps.search(lat=lat, lng=lng).first()
    # print(my_location)
    mycursor.execute(sql, val)
    mydb.commit()
    flash("Successfully Detected")
    # ------------------------CAR-------------------------------------------------------

    return data


@main.route('/uploader', methods=['GET', 'POST'])
@login_required
def upload_file():
    if request.method == 'POST':
        f = request.files['file']
        index=f.filename.split('.')[1]
        print(index)
        if f.filename != '':
            if index != "mp4":
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
            else:
                filename_video = secure_filename(f.filename)
                file = pathlib.Path(UPLOAD_FOLDER + "/" + 'cars3.mp4')
                if file.exists():
                    os.remove(UPLOAD_FOLDER + "/" + 'cars3.mp4')
                f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename_video))
                os.rename(UPLOAD_FOLDER + "/" + filename_video, UPLOAD_FOLDER + "/" + 'cars3.mp4')
                # f.save(secure_filename(f.filename))
                flash("Uploaded Successfully")
                file = pathlib.Path(UPLOAD_FOLDER + "/" + 'cars3.mp4')

            return redirect(url_for('main.dashboard'))
        else:
            flash(" Please select images")
            return redirect(url_for('main.dashboard'))


@main.route('/activity')
@login_required
def activitylog():
    global page_log, user_log, vehicle_log, vehicle_pagination_log, count_log
    page_log = request.args.get('page', 1, type=int)
    user_log = User.query.filter_by(email=current_user.email).first_or_404()
    vehicle_log = user_log.activitylog
    vehicle_pagination_log = Activitylog.query.filter_by(author=user_log).paginate(page=page_log, per_page=5)
    count_log = Activitylog.query.filter_by(author=user_log).count()
    return render_template('activity.html', data=vehicle_pagination_log)


# @main.route("/search", methods=["POST","GET"])
# @login_required
# def search():
#     searchbox = request.form.get("search_text")
#     search = "%{}%".format(searchbox)
#     vehicle_found = VehicleData.query.filter(VehicleData.vehicle.like(search)).all()
#     return render_template('index.html',data=vehicle_found)

@main.route("/search", methods=["POST", "GET"])
@login_required
def search():
    searchbox = request.form.get("search_text")
    search = "%{}%".format(searchbox)
    page = request.args.get('page', 1, type=int)
    vehicle_pagination = VehicleData.query.filter(VehicleData.vehicle.like(search)).paginate(page=page, per_page=3)
    now = datetime.now()
    week_ago = now - timedelta(hours=8)
    total_visit_today = now - timedelta(hours=12)
    active_count = Activitylog.query.filter(Activitylog.date_updated <= total_visit_today).count()
    week_count = VehicleData.query.filter(VehicleData.date_created > week_ago).filter(
        VehicleData.date_created < now).count()
    user_log = User.query.filter_by(email=current_user.email).first_or_404()
    count_log = Activitylog.query.filter_by(author=user_log).count()
    return render_template('index.html', count=week_count, log=count_log, active=active_count, data=vehicle_pagination,
                           name=current_user.username)


# camera = cv2.VideoCapture(0)
camera = cv2.VideoCapture('D:/Project/flask-project/venv/flask_project/video/cars3.mp4')


def snapshot(frame, ctr):
    cv2.imwrite("D:/Project/flask-project/cardetect/Snaphots/ss" + str(ctr) + ".jpg", frame)
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(frame, "Taking Snapshot", (15, 15), font, 0.5, (255, 255, 255), 1)
    cv2.imshow('Vehicle Detection System - Snapshot Screen', frame)
    return True


def renderJSON_video(json_v):
    # ------------------------CAR-------------------------------------------------------
    count = 0
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
    global vehicle_name, vehicle_model, vehicle_color, vehicle_type, vehicle_number_plate, date
    vehicle_name = data["car_make"]["name"].upper();
    vehicle_model = data["car_model"]["name"].upper();
    vehicle_color = data["car_color"]["name"].upper();
    vehicle_type = data["car_type"].upper();
    vehicle_number_plate = data["number_plate"].upper();
    date = datetime.now();
    count = count + 1
    data["number_plate"] = json_v["objects"][0]["vehicleAnnotation"]["recognitionConfidence"]
    # print("{:.1f}".format(data["number_plate"]))
    # if (mydb):
    #     print("connected with database ")
    # mycursor = mydb.cursor()
    # sql = "INSERT INTO vehicle_data(user_id,vehicle,model,color,type,number_plate,date_created) VALUES (4,%(vehicle)s,%(model)s,%(color)s,%(type)s,%(number_plate)s,%(date_created)s)"
    # val = {
    #     'vehicle': vehicle_name,
    #     'model': vehicle_model,
    #     'color': vehicle_color,
    #     'type': vehicle_type,
    #     'number_plate': vehicle_number_plate,
    #     'date_created': date
    # }
    # mycursor.execute(sql, val)
    # mydb.commit()

    # ------------------------CAR-------------------------------------------------------

    return data


def gen_frames():  # generate frame by frame from camera
    ctr = 0

    font = cv2.FONT_HERSHEY_SIMPLEX
    # Turn to TRUE to send stream to API
    carRecogMode = True

    car_cascade = cv2.CascadeClassifier('cars4.xml')
    while True:
        # Capture frame-by-frame
        ret, frame = camera.read()  # read the camera frame
        if not ret:
            break
        else:

            # ret, buffer = cv2.imencode('.jpg', frame)
            #
            # frame = buffer.tobytes()
            imgencode = cv2.imencode('.jpg', frame)[1].tobytes()
            # stringData = imgencode.tostring()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + imgencode + b'\r\n')  # concat frame one by one and show result

            cv2.imwrite("D:/Project/flask-project/venv/flask_project/Frames/f" + str(ctr) + ".jpg", frame)
            # cv2.imwrite("Frames/f" + str(ctr) + ".jpg", frame)
            response = findCar("D:/Project/flask-project/venv/flask_project/Frames/f" + str(ctr) + ".jpg")

            # Converting their Response to JSON
            json_response = json.loads(response)

            # Processing that JSON for our Parameters
            print(json_response)

            data = renderJSON_video(json_response)

            if data["car_color"] != False:
                yield (data["car_color"]["name"])
                cv2.putText(frame, data["car_color"]["name"], (15, 60), font, 1, (0, 0, 0), 3)

                print(data["car_color"]["name"])

            if data["number_plate"] != False:
                # LPN
                cv2.putText(frame, str(data["number_plate"]), (10, 100), font, 1, (255, 146, 0), 3)
                print(str(data["number_plate"]))

            # display the resulting frame
            # cv2.imshow('Vehicle Detection System - Live Camera Footage', frame)
            ctr = ctr + 1

            # -------------------------------------------

            # press Q on keyboard to exit---------------
            c = cv2.waitKey(25)
            # print("NOT EXITING: Q is not Pressed!")

            if c == ord('q'):
                # print("EXITING: Q is Pressed!")
                break
            if c == ord('s'):
                snapshot(frame, ctr)
            # -------------------------------------------

        # ------------------------------------------------------------------------

        # release the videocapture object

        # camera.release()
        # close all the frames
        # cv2.destroyAllWindows()


@main.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@main.route('/video_process', methods=["POST", "GET"])
def video_response():
    count = 1
    # camera.release()
    # cv2.destroyAllWindows()
    if (mydb):
        print("connected with database ")
    mycursor = mydb.cursor()
    if count == 1:
        sql = "INSERT INTO vehicle_data(user_id,vehicle,model,color,type,number_plate,date_created) VALUES (4,%(vehicle)s,%(model)s,%(color)s,%(type)s,%(number_plate)s,%(date_created)s)"
        val = {
            'vehicle': vehicle_name,
            'model': vehicle_model,
            'color': vehicle_color,
            'type': vehicle_type,
            'number_plate': vehicle_number_plate,
            'date_created': date
        }
        mycursor.execute(sql, val)
        mydb.commit()
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(email=current_user.email).first_or_404()
    vehicle = user.vehicledata
    hide = False
    vehicle_pagination = VehicleData.query.filter_by(author=user).paginate(page=page, per_page=3)
    return render_template('index.html', count=week_count, response='ok', hidden=hide, data=vehicle_pagination,
                           name=current_user.username)


@main.route('/dashboard')
def video_restart():
    return redirect(url_for('main.dashboard'))


@main.route('/start')
def video_start():
    hide = True
    if request.method == 'GET':
        return render_template('index.html', count=week_count, hidden=hide, data=vehicle_pagination_global,
                               name=current_user.username)
