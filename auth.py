from flask import Blueprint, redirect, render_template, request, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import  login_user, logout_user, login_required, current_user
from .model import User,db

auth = Blueprint('auth', __name__)

@auth.route('/')
def home():
    return redirect(url_for('auth.login'))

@auth.route('/login')
def login():
    return render_template('pages/auth/login.html')

@auth.route('/login', methods=['POST'])
def login_post():
    email = request.form.get('email')
    password = request.form.get('password')
    remember=True if request.form.get('remember') else False
    user= User.query.filter_by(email=email).first()
    print(email,check_password_hash(user.password,password))
    if not user or not check_password_hash(user.password,password):
        flash("Login failed try again")
        return redirect(url_for('auth.login'))
    login_user(user, remember=remember)
    flash("Welcome "+ current_user.username)
    return redirect(url_for('main.dashboard'))

@auth.route('/signup')
def signup():
    return render_template('pages/auth/register.html')


@auth.route('/signup', methods=['POST'])
def signup_post():
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')
    hash_password=generate_password_hash(password, method = 'sha256')
    print(email, hash_password)
    user= User.query.filter_by(email=email).first()
    if user:
        flash("User Already exist try different email")
        return redirect(url_for('auth.signup'))
    New_user=User(username,email,hash_password)
    db.session.add(New_user)
    db.session.commit()
    flash("Successfully created!!")
    return redirect(url_for('auth.login'))

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
