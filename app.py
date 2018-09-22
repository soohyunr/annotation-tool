import os, sys
from flask import Flask, session, g, request, render_template
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
    remote_addr = request.remote_addr
    if remote_addr != '127.0.0.1' and '143.248.' not in remote_addr:
        return render_template('403.html')

    if 'username' not in session:
        g.user = None
    else:
        g.user = User.objects.get(username=session['username'])


app.add_url_rule('/', view_func=views.index, methods=['GET'])
app.add_url_rule('/login', view_func=views.login, methods=['GET'])
app.add_url_rule('/logout', view_func=views.logout, methods=['GET'])
app.add_url_rule('/doc/<doc_id>', view_func=views.doc, methods=['GET'])

app.add_url_rule('/api/login', view_func=views.post_login, methods=['POST'])
app.add_url_rule('/api/doc/<doc_id>', view_func=views.get_doc, methods=['GET'])
app.add_url_rule('/api/doc/<doc_id>/annotation', view_func=views.get_annotation, methods=['GET'])
app.add_url_rule('/api/annotation', view_func=views.post_annotation, methods=['POST'])
app.add_url_rule('/api/annotation/<annotation_id>', view_func=views.delete_annotation, methods=['DELETE'])
app.add_url_rule('/api/annotation/<annotation_id>', view_func=views.put_annotation, methods=['PUT'])

if __name__ == '__main__':
    FLASK_DEBUG = os.getenv('FLASK_DEBUG', True)
    app.run(host='0.0.0.0', debug=FLASK_DEBUG, port=8081)
