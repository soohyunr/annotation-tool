import json
from flask import request, render_template, Response, g, session, redirect, url_for

from models import Doc, User, Sent
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


@login_required
def doc(doc_id):
    doc = Doc.objects.get(id=doc_id)
    return render_template('doc.html', doc=doc, g=g)


@login_required
def get_doc(doc_id):
    doc = Doc.objects.get(id=doc_id)
    sents = Sent.objects(doc=doc).order_by('index')

    sents_data = []
    for sent in sents:
        sents_data.append(sent.dump())

    return json.dumps({
        'sents': sents_data,
    })


def post_login():
    data = request.get_json()
    username = data['username']
    password = data['password']

    user = User.objects.get(username=username)
    if not user or not user.check_password(password):
        return Response(status=403)

    session['username'] = username
    g.user = user.dump()
    return Response('success', status=200)
