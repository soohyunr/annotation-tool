import json
from flask import request, render_template, Response, g, session, redirect, url_for

from models import Doc, User
from decorator import login_required


@login_required
def index():
    docs = Doc.objects.all()
    return render_template('index.html', docs=docs, g=g)


def login():
    return render_template('login.html', g=g)


def logout():
    if 'username' in session: del session['username']
    return redirect(url_for('login'))


def doc(doc_id):
    doc = Doc.objects.get(id=doc_id)
    sents = []

    for index, sen in enumerate(doc.text.split('.')):
        sents.append((index + 1, sen + '.'))

    return render_template('doc.html', doc=doc, sents=sents, g=g)


def login_api():
    data = request.get_json()
    username = data['username']
    password = data['password']

    user = User.objects.get(username=username)
    if not user or not user.check_password(password):
        return Response(status=403)

    session['username'] = username
    g.user = user.dump()
    return Response('success', status=200)
