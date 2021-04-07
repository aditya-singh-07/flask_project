import os

from flask import Blueprint, redirect, render_template, request, url_for, flash, Flask
from flask_login import login_required, current_user
from datetime import date
from werkzeug.utils import secure_filename
from .model import User, db, VehicleData
app = Flask(__name__)
UPLOAD_FOLDER = './uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


main = Blueprint('main', __name__)


# @main.route('/')
# @login_required
# def index():
#     return render_template('index.html')


@main.route('/dashboard')
@login_required
def dashboard():
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(email=current_user.email).first_or_404()
    vehicle = user.vehicledata
    vehicle_pagination = VehicleData.query.filter_by(author=user).paginate(page=page, per_page=5)

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


@main.route('/uploader', methods=['GET', 'POST'])
@login_required
def upload_file():
    if request.method == 'POST':
        f = request.files['file']
        if f.filename == '':
            flash('No selected file')
            return redirect(request.url)
        filename = secure_filename(f.filename)
        f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        # f.save(secure_filename(f.filename))
        flash("Uploaded Successfully")
        return redirect(url_for('main.dashboard'))
