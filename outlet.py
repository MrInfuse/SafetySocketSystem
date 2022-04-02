from flask import Blueprint, render_template

outlet = Blueprint("outlet", __name__, static_folder="static", template_folder="template")