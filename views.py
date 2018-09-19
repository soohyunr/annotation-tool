import flask
from models import Doc


def index():

    return flask.render_template('index.html')

