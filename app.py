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

app = Flask(__name__)
app.register_blueprint(outlet, url_prefix="")
app.register_blueprint(currentSensor, url_prefix="")


@app.route('/consumption')
def wattsOMeter():
    
    # while True:
    #     if ser.in_waiting > 0:
    #         line = ser.readline().decode('utf-8').rstrip()
    #         print(line)
    return render_template('consumption.html')

@app.route('/update')
def update():
    ser = serial.Serial('/dev/ttyACM0', 115200, timeout=1)
    ser.flush()
    
    while True:
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8').rstrip()
            print(line)
            data = {'ct1' : line}
            return jsonify(data)

@app.route('/app_curt')
def app_curt():
    while 1:
        # wp.delay(30)
        pin_97_value = wp.analogRead(97)
        return render_template('app_curt.html', mcp3008_01=pin_97_value)


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
    app.run(debug=True, host='192.168.254.105')