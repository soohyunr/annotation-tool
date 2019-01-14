import os, sys, datetime, random
from flask import Flask, session, g, request, render_template, redirect
from flask_mongoengine import MongoEngine
# import sentry_sdk
# from sentry_sdk.integrations.flask import FlaskIntegration

import views, config
from models import User

base_dir = os.path.abspath(os.path.dirname(__file__) + '/')
sys.path.append(base_dir)

# sentry_sdk.init(
#     dsn=config.Config.SENTRY_DSN,
#     integrations=[FlaskIntegration()]
# )

app = Flask(__name__)

app.config.from_object('config.Config')
db = MongoEngine(app)


@app.before_request
def before_request():
    g.random = random.randrange(1, 10000)
    if 'username' not in session:
        g.user = None
    else:
        user = User.objects.get(username=session['username'])
        user.accessed_at = datetime.datetime.now
        user.last_ip = request.remote_addr
        user.save()
        g.user = user


app.add_url_rule('/', view_func=views.index_page, methods=['GET'])
app.add_url_rule('/403', view_func=views.page_403, methods=['GET'])
app.add_url_rule('/users', view_func=views.users_page, methods=['GET'])
app.add_url_rule('/login', view_func=views.login_page, methods=['GET'])
app.add_url_rule('/signup', view_func=views.signup_page, methods=['GET'])
app.add_url_rule('/logout', view_func=views.logout_page, methods=['GET'])
app.add_url_rule('/doc/<doc_id>', view_func=views.doc_page, methods=['GET'])

app.add_url_rule('/api/login', view_func=views.post_login, methods=['POST'])
app.add_url_rule('/api/signup', view_func=views.post_signup, methods=['POST'])
app.add_url_rule('/api/user/<user_id>/active', view_func=views.put_user_active, methods=['PUT'])
# app.add_url_rule('/api/doc/<doc_id>', view_func=views.get_doc, methods=['GET'])
app.add_url_rule('/api/doc/<doc_id>/annotation', view_func=views.get_annotation, methods=['GET'])
app.add_url_rule('/api/annotation', view_func=views.post_annotation, methods=['POST'])
app.add_url_rule('/api/annotation/<annotation_id>', view_func=views.delete_annotation, methods=['DELETE'])
app.add_url_rule('/api/annotation/<annotation_id>', view_func=views.put_annotation, methods=['PUT'])

app.add_url_rule('/download/dataset', view_func=views.download_dataset, methods=['GET'])

app.add_url_rule('/mturk/upload', view_func=views.mturk_upload_page, methods=['GET'])
app.add_url_rule('/mturk/doc/<doc_id>', view_func=views.mturk_doc_page, methods=['GET'])
app.add_url_rule('/api/mturk/upload', view_func=views.post_mturk_upload, methods=['POST'])

if __name__ == '__main__':
    FLASK_DEBUG = os.getenv('FLASK_DEBUG', False)
    app.run(host='0.0.0.0', debug=FLASK_DEBUG, port=8081)
