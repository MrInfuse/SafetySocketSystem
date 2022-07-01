from re import L
import sqlite3
from turtle import delay
import wiringpi as wp
import serial
import datetime
import time
import os

from outlet import outlet
from ct import currentSensor
from flask import Flask, request, render_template, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.register_blueprint(outlet, url_prefix="")
app.register_blueprint(currentSensor, url_prefix="")
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SECRET_KEY'] = 'mors omnibus'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)

class RegisterForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)])
    password = PasswordField(validators=[InputRequired(), Length(min=4, max=20)])
    submit = SubmitField("Register")

    def validate_username(self, username):
        existing_user_username = User.query.filter_by(username=username.data).first()

        if existing_user_username:
            raise ValidationError("That username already exist. Please choose a different one.")


class LoginForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)])
    password = PasswordField(validators=[InputRequired(), Length(min=4, max=20)])
    submit = SubmitField("Login")


@app.route('/', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('outlet.index'))
    return render_template('login.html', form=form)


@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))

    return render_template('register.html', form=form)


@app.route('/consumption')
def wattsOMeter():
    
    # while True:
    #     if ser.in_waiting > 0:
    #         line = ser.readline().decode('utf-8').rstrip()
    #         print(line)
    return render_template('consumption.html')

@app.route('/ArduinoCT01')
def update():
    ser = serial.Serial('/dev/ttyACM0', 115200, timeout=1)
    ser.flush()
    
    while True:
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8').rstrip()
            print(line)
            data = {'MCct1' : line}
            return jsonify(data)


@app.route('/app_env_db', methods=['GET'])
def app_env_db():
    curt, from_date_str, to_date_str = get_records()
    return render_template('app_env_db.html',
                           current=curt,
                           from_date=from_date_str,
                           to_date=to_date_str)


def get_records():
    from_date_str = request.args.get('from', time.strftime("%Y-%m-%d 00:00"))
    to_date_str = request.args.get('to', time.strftime("%Y-%m-%d %H:%M"))
    range_h_form = request.args.get("range_h", '');

    range_h_int = "nan"

    try:
        range_h_int = int(range_h_form)
        print(range_h_int)
    except:
        print("range_h_from not a number")
        print(range_h_form)

    if not validate_date(from_date_str):
        from_date_str = time.strftime("%Y-%m-%d 00:00")
    if not validate_date(to_date_str):
        to_date_str = time.strftime("%Y-%m-%d %H:%M")

    if isinstance(range_h_int, int):
        time_now = datetime.datetime.now()
        time_from = time_now - datetime.timedelta(hours=range_h_int)
        time_to = time_now
        from_date_str = time_from.strftime("%Y-%m-%d %H:%M")
        to_date_str = time_to.strftime("%Y-%m-%d %H:%M")

    connection = sqlite3.connect('/var/www/SafetySocketSystem/app.db')
    getCursor = connection.cursor()
    getCursor.execute("SELECT * FROM curr WHERE rDatetime BETWEEN ? AND ?", (from_date_str, to_date_str))
    curt = getCursor.fetchall()
    connection.close()
    return [curt, from_date_str, to_date_str]


def validate_date(d):
    try:
        datetime.datetime.strptime(d, '%Y-%m-%d %H:%M')
        return True
    except ValueError:
        return False


@app.route('/shutdown')
def shutdown():
    os.system('sudo shutdown now')
    return '<h1>Shutting Down!</h1>'


@app.route('/reboot')
def reboot():
    os.system('sudo reboot')
    return '<h1>Restarting Down!</h1>'


if __name__ == '__main__':
    app.run(debug=True, host='192.168.0.16')