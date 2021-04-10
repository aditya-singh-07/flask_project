from datetime import datetime

from . import db
from flask_login import UserMixin


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    vehicledata = db.relationship('VehicleData', backref='author', lazy=True)
    activitylog = db.relationship('Activitylog', backref='author', lazy=True)

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password


class VehicleData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    vehicle = db.Column(db.String(50), nullable=False)
    model = db.Column(db.String(50), nullable=False)
    color = db.Column(db.String(50), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    number_plate = db.Column(db.String(100), nullable=False)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __init__(self, user_id, vehicle, model, color, type, number_plate, date_created):
        self.user_id = user_id
        self.vehicle = vehicle
        self.model = model
        self.color = color
        self.type = type
        self.number_plate = number_plate
        self.date_created = date_created


class Activitylog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    username = db.Column(db.String(100), nullable=False)
    changes = db.Column(db.String(100), nullable=False)
    ip = db.Column(db.String(255), nullable=False)
    date_updated = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __init__(self, user_id,username, changes, ip, date_updated):
        self.user_id = user_id
        self.username=username
        self.changes = changes
        self.ip = ip
        self.date_updated = date_updated
