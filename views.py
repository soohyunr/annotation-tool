import json, math
from flask import request, render_template, Response, g, session, redirect, url_for
from flask_mongoengine import Pagination

from models import Doc, User, Sent, Annotation
from decorator import login_required


@login_required
def index():
    item_per_page = 50
    page = request.args.get('p', 1)
    page = int(page)

    total = Doc.objects.count()
    total_page = math.ceil(total / item_per_page)
    paginator = Pagination(Doc.objects, page, 50)
    docs = paginator.items
    return render_template('index.html', docs=docs, g=g, page=page, total_page=total_page)


def login():
    return render_template('login.html', g=g)


def logout():
    if 'username' in session: del session['username']
    return redirect(url_for('login'))


@login_required
def doc(doc_id):
    doc = Doc.objects.get(seq=doc_id)
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


@login_required
def post_annotation():
    data = request.get_json()

    doc = data['doc']
    entire_text = data['entire_text']
    target_text = data['target_text']
    index = data['index']
    anchor_offset = data['anchor_offset']
    focus_offset = data['focus_offset']
    type = data['type']

    doc = Doc.objects().get(id=doc)
    sent = Sent.objects().get(doc=doc, index=index)
    user = g.user

    annotation = Annotation(
        doc=doc,
        sent=sent,
        user=user,
        type=type,
        index=index,
        anchor_offset=anchor_offset,
        focus_offset=focus_offset,
        entire_text=entire_text,
        target_text=target_text,
    )
    annotation.save()

    return json.dumps({
        'annotation': annotation.dump(),
    })


@login_required
def get_annotation(doc_id):
    doc = Doc.objects().get(id=doc_id)
    annotations = Annotation.objects(doc=doc, user=g.user)

    data = []
    for annotation in annotations:
        data.append(annotation.dump())

    return json.dumps({
        'annotations': data,
    })


@login_required
def delete_annotation(annotation_id):
    Annotation.objects(id=annotation_id).delete()
    return Response('success', status=200)


@login_required
def put_annotation(annotation_id):
    data = request.get_json()
    basket = data['basket']
    annotation = Annotation.objects().get(id=annotation_id)
    annotation.basket = basket
    annotation.save()

    return json.dumps({
        'annotation': annotation.dump(),
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
