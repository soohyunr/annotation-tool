import os, sys
from flask import Flask, session, g
from flask_mongoengine import MongoEngine

import views
from models import User

base_dir = os.path.abspath(os.path.dirname(__file__) + '/')
sys.path.append(base_dir)

app = Flask(__name__)

app.config.from_object('config.Config')
db = MongoEngine(app)


@app.before_request
def before_request():
    if 'username' not in session:
        g.user = None
    else:
        g.user = User.objects.get(username=session['username'])


app.add_url_rule('/', view_func=views.index, methods=['GET'])
app.add_url_rule('/login', view_func=views.login, methods=['GET'])
app.add_url_rule('/logout', view_func=views.logout, methods=['GET'])

app.add_url_rule('/api/login', view_func=views.login_api, methods=['POST'])

if __name__ == '__main__':
    FLASK_DEBUG = os.getenv('FLASK_DEBUG', True)
    app.run(host='0.0.0.0', debug=FLASK_DEBUG, port=8080)
