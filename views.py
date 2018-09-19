import flask
from models import Doc


def index():
    docs = Doc.objects.all()

    for doc in docs:
        print(doc.id)

    return flask.render_template('index.html', docs=docs)
