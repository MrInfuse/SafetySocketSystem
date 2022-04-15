import serial
from flask import Blueprint, request, url_for, render_template

currentSensor = Blueprint("currentSensor", __name__, static_folder="static", template_folder="templates")


