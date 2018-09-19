import os, sys
import flask
from flask_mongoengine import MongoEngine

import views

base_dir = os.path.abspath(os.path.dirname(__file__) + '/')
sys.path.append(base_dir)

app = flask.Flask(__name__)

app.config.from_pyfile('config.cfg')
db = MongoEngine(app)

app.add_url_rule('/', view_func=views.index)
app.add_url_rule('/pagination', view_func=views.pagination)

if __name__ == '__main__':
    FLASK_DEBUG = os.getenv('FLASK_DEBUG', False)
    app.run(host='0.0.0.0', debug=FLASK_DEBUG, port=8080)
