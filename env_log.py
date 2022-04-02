import sqlite3
import wiringpi
from time import time, sleep

wiringpi.mcp3004Setup(97, 0)  # pin 1-8 = [97, 98, 99, 100, 101, 102, 103, 104] channel = 0 GPIO8 CE0


def log_values(sensor_id, curt):
    connection = sqlite3.connect('/var/www/SafetySocketSystem/app.db')
    getCursor = connection.cursor()
    getCursor.execute("""INSERT INTO curr values(datetime(CURRENT_TIMESTAMP, 'localtime'), (?), (?))""", (sensor_id, curt))
    connection.commit()
    connection.close()


mcp3008pin_01 = wiringpi.analogRead(97)
if mcp3008pin_01 is not None:
    log_values("1", mcp3008pin_01)
else:
    log_values("1", -999)
