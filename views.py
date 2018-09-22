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
                'memo': annotation.memo,
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
    memo = data['memo']
    annotation = Annotation.objects().get(id=annotation_id)
    annotation.basket = basket
    annotation.memo = memo
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
