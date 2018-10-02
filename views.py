import json, math, datetime
from flask import request, render_template, Response, g, session, redirect, url_for
from flask_mongoengine import Pagination

from models import Doc, User, Sent, Annotation, DocLog
from decorator import login_required, is_admin
import config


@login_required
def index_page():
    item_per_page = 50
    page = request.args.get('p', 1)
    page = int(page)

    total = Doc.objects.count()
    total_page = math.ceil(total / item_per_page)
    paginator = Pagination(Doc.objects().order_by('seq'), page, 50)
    docs = paginator.items

    docs_data = []
    for doc in docs:
        item = doc.dump()
        item['sent_total'] = Sent.objects(doc=doc).count()
        item['progress'] = Annotation.objects(doc=doc, user=g.user, type='sentence').count()

        docs_data.append(item)

    pagination = {
        'page': page,
        'total_page': total_page,
        'left': max(1, page - 5),
        'right': min(page + 5, total_page),
    }

    return render_template('index.html', docs=docs_data, g=g, pagination=pagination)


@is_admin
def users_page():
    users = User.objects.all()
    for user in users:
        user.annotation_count = Annotation.objects(user=user).count()
    return render_template('users.html', users=users, g=g)


def login_page():
    return render_template('login.html', g=g)


def page_403():
    return render_template('403.html', g=g)


def signup_page():
    return render_template('signup.html', g=g)


def logout_page():
    if 'username' in session: del session['username']
    return redirect('/login')


@login_required
def doc_page(doc_id):
    doc = Doc.objects.get(seq=doc_id)

    doc_log = DocLog(user=g.user, doc=doc, ip=request.remote_addr)
    doc_log.save()

    return render_template('doc.html', doc=doc, g=g, ENCRYPTION_KEY=config.Config.ENCRYPTION_KEY)


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
    basket = data['basket']

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
        basket=basket,
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


@is_admin
def download_dataset():
    docs = Doc.objects

    data = []
    for doc in docs:
        annotations = Annotation.objects(doc=doc)
        for annotation in annotations:
            data.append({
                'annotator': annotation.user.username,
                'doc_id': doc.seq,
                'sentence_index': annotation.index,
                'sentence': annotation.entire_text,
                'annotation_anchor_offset': annotation.anchor_offset,
                'annotation_focus_offset': annotation.focus_offset,
                'annotation_target_text': annotation.target_text,
                'annotation_type': annotation.type,
                'attributes': annotation.basket,
                'title': doc.title,
                'source': doc.source,
            })

    return Response(json.dumps({
        'annotations': data,
    }), mimetype='application/json')


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
    annotation.updated_at = datetime.datetime.now
    annotation.save()

    return json.dumps({
        'annotation': annotation.dump(),
    })


@is_admin
def put_user_active(user_id):
    data = request.get_json()
    is_active = data['is_active']

    user = User.objects().get(id=user_id)
    user.is_active = is_active
    user.save()

    return Response('success', status=200)


def post_login():
    data = request.get_json()
    username = data['username']
    password = data['password']

    user = User.objects.filter(username=username)
    if len(user) == 0:
        return Response(status=403)

    user = user[0]
    if not user.check_password(password):
        return Response(status=403)

    session['username'] = username
    g.user = user.dump()
    return Response('success', status=200)


def post_signup():
    data = request.get_json()
    username = data['username']
    first_name = data['first_name']
    last_name = data['last_name']
    password = data['password']

    user = User.objects.filter(username=username)
    if len(user) != 0:
        return Response(status=401)

    user = User(username=username, first_name=first_name, last_name=last_name)
    user.set_password(password)
    user.save()

    return Response('success', status=200)
