import json, math, datetime, os
from flask import request, render_template, Response, g, session, redirect, send_file
from flask_mongoengine import Pagination
from bson import json_util

from models import Doc, User, Sent, Annotation, DocLog, AnnotationReview
from decorator import is_user, is_active_user, is_admin
import config
from tqdm import tqdm
import utils


@is_active_user
def index_page():
    item_per_page = 50
    page = request.args.get('p', 1)
    page = int(page)

    total = Doc.objects.filter(type='v1').count()
    total_page = math.ceil(total / item_per_page)
    paginator = Pagination(Doc.objects(type='v1').order_by('seq'), page, 50)
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

    return render_template('index.html', type='v1', docs=docs_data, g=g, pagination=pagination)


@is_active_user
def index_v2_page(doc_type):
    item_per_page = 50
    page = request.args.get('p', 1)
    page = int(page)

    total = Doc.objects.filter(type=doc_type).count()
    total_page = math.ceil(total / item_per_page)
    paginator = Pagination(Doc.objects(type=doc_type).order_by('seq'), page, 50)
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

    return render_template('index.html', type=doc_type, docs=docs_data, g=g, pagination=pagination)


@is_admin
def users_page():
    users = User.objects.all()
    for user in users:
        user.annotation_count = Annotation.objects(user=user).count()
    return render_template('users.html', users=users, g=g)


def login_page():
    callback = request.args.get('callback', '/')
    return render_template('login.html', g=g, callback=callback)


def page_403():
    return render_template('403.html', g=g)


def page_404():
    return render_template('404.html', g=g)


def signup_page():
    callback = request.args.get('callback', '/')
    return render_template('signup.html', callback=callback, g=g)


def auto_signup_page():
    callback = request.args.get('callback', '/')

    import random, string
    def random_char():
        return ''.join(random.choice(string.digits + string.ascii_lowercase) for _ in range(10))

    username = random_char()
    password = random_char()

    user = User(username=username, first_name='Random ID', last_name='')
    user.set_password(password)
    user.save()

    return render_template('auto_signup.html', callback=callback, g=g, username=username, password=password)


def logout_page():
    if 'username' in session: del session['username']
    return redirect('/login')


@is_active_user
def doc_page(doc_id):
    try:
        doc = Doc.objects.get(seq=doc_id)
    except Exception as e:
        return redirect('/404')

    doc_log = DocLog(user=g.user, doc=doc, ip=request.remote_addr)
    doc_log.save()

    if doc.type == 'v3':
        return render_template('doc_v3.html', doc=doc, g=g, ENCRYPTION_KEY=config.Config.ENCRYPTION_KEY)

    return render_template('doc.html', doc=doc, g=g, ENCRYPTION_KEY=config.Config.ENCRYPTION_KEY)


@is_active_user
def get_doc(doc_id):
    doc = Doc.objects.get(id=doc_id)
    sents = Sent.objects(doc=doc).order_by('index')

    sents_data = []
    for sent in sents:
        sents_data.append(sent.dump())

    return json.dumps({
        'sents': sents_data,
    })


@is_user
def post_annotation():
    data = request.get_json()

    doc = data['doc']
    target_text = data['target_text']
    index = data['index']
    anchor_offset = data['anchor_offset']
    focus_offset = data['focus_offset']
    type = data['type']
    basket = data['basket']

    doc = Doc.objects().get(id=doc)
    sent = Sent.objects().get(doc=doc, index=index)
    user = g.user

    target_sent = Sent.objects().get(doc=doc, index=index)

    # In sentence, filter logic have to be changed
    if type == 'sentence':
        annotations = Annotation.objects.filter(doc=doc, sent=sent, index=index, user=g.user, type=type)
    else:
        annotations = Annotation.objects.filter(doc=doc, sent=sent, index=index, user=g.user, type=type, anchor_offset=anchor_offset)

    if annotations.count() > 0:
        annotation = annotations[0]
    else:
        annotation = Annotation(doc=doc, sent=sent, user=user, index=index, type=type, anchor_offset=anchor_offset)

    annotation.anchor_offset = anchor_offset
    annotation.focus_offset = focus_offset
    annotation.entire_text = target_sent.text
    annotation.target_text = target_text
    annotation.basket = basket
    annotation.ip = request.remote_addr

    annotation.save()

    return json.dumps({
        'annotation': annotation.dump(),
    })


@is_user
def get_annotation(doc_id):
    try:
        doc = Doc.objects().get(id=doc_id)
        annotations = Annotation.objects(doc=doc, user=g.user)
    except Exception as e:
        return Response('not found', status=404)
    data = []
    for annotation in annotations:
        data.append(annotation.dump())

    return json.dumps({
        'annotations': data,
    })


@is_user
def delete_annotation(annotation_id):
    try:
        annotation = Annotation.objects().get(id=annotation_id)
    except Annotation.DoesNotExist:
        return Response('not found', status=404)

    if annotation.user.id != g.user.id:
        return Response('permission error', status=403)
    annotation.delete()
    return Response('success', status=200)


@is_user
def put_annotation(annotation_id):
    data = request.get_json()
    basket = data['basket']
    try:
        annotation = Annotation.objects().get(id=annotation_id)
    except Exception:
        return Response('not found', status=404)
    if annotation.user.id != g.user.id:
        return Response('permission error', status=403)
    annotation.basket = basket
    annotation.updated_at = datetime.datetime.now
    annotation.save()

    return json.dumps({
        'annotation': annotation.dump(),
    })


@is_admin
def download_dataset():
    docs = Doc.objects.filter()

    data = []
    for doc in tqdm(docs):
        annotations = Annotation.objects(doc=doc)
        for annotation in annotations:
            data.append({
                'annotator': annotation.user.username,
                'doc_id': doc.seq,
                'version': doc.type,
                'turker_id': annotation.user.turker_id,
                'sentence_index': annotation.index,
                'sentence': annotation.entire_text,
                'annotation_anchor_offset': annotation.anchor_offset,
                'annotation_focus_offset': annotation.focus_offset,
                'annotation_target_text': annotation.target_text,
                'annotation_type': annotation.type,
                'attributes': annotation.basket,
                'title': doc.title,
                'source': doc.source,
                'created_at': annotation.created_at,
            })

    dataset_path = os.path.abspath(os.path.dirname(__file__) + '/dataset.json')
    data_json = json.dumps(data, default=json_util.default, indent=2)
    with open(dataset_path, 'w', encoding='utf-8') as f:
        f.write(data_json)

    return send_file(dataset_path, as_attachment=True)


@is_admin
def download_dataset_AMT_v2():
    docs = Doc.objects.filter(type='mturk_v2')

    data = []
    for doc in tqdm(docs):
        annotations = Annotation.objects(doc=doc)
        for annotation in annotations:
            data.append({
                'annotator': annotation.user.username,
                'turker_id': annotation.user.turker_id,
                'doc_id': str(doc.id),
                'sentence_index': annotation.index,
                'sentence': annotation.entire_text,
                'basket': annotation.basket,
                'source': doc.source,
                'created_at': annotation.created_at,
            })

    dataset_path = os.path.abspath(os.path.dirname(__file__) + '/dataset_AMT_v2.json')
    data_json = json.dumps(data, default=json_util.default,indent=2)
    with open(dataset_path, 'w', encoding='utf-8') as f:
        f.write(data_json)

    return send_file(dataset_path, as_attachment=True)


@is_admin
def download_dataset_AMT_v3():
    docs = Doc.objects.filter(type='mturk_v3')

    data = []
    for doc in tqdm(docs):
        annotations = Annotation.objects(doc=doc)
        for annotation in annotations:
            data.append({
                'annotator': annotation.user.username,
                'version': doc.type,
                'turker_id': annotation.user.turker_id,
                'doc_id': str(doc.id),
                'sentence_index': annotation.index,
                'sentence': annotation.entire_text,
                'basket': annotation.basket,
                'source': doc.source,
                'created_at': annotation.created_at,
            })

    dataset_path = os.path.abspath(os.path.dirname(__file__) + '/dataset_AMT_v3.json')
    data_json = json.dumps(data, default=json_util.default, indent=2)
    with open(dataset_path, 'w', encoding='utf-8') as f:
        f.write(data_json)

    return send_file(dataset_path, as_attachment=True)


@is_admin
def download_encrypted():
    dataset_path = os.path.abspath(os.path.dirname(__file__) + '/encrypted.zip')
    return send_file(dataset_path, as_attachment=True)


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


@is_user
def mturk_upload_page():
    return render_template('mturk/upload.html', g=g)


@is_user
def mturk_upload_page_v2(doc_type):
    return render_template('mturk/{}/upload.html'.format(doc_type), g=g)


@is_user
def post_mturk_upload():
    data = request.get_json()
    text = data['text']
    doc_type = data['doc_type']

    if 'turker_id' in data:
        turker_id = data['turker_id']

        g.user.turker_id = turker_id
        g.user.save()

    from nltk.tokenize import sent_tokenize
    sents = sent_tokenize(text)

    doc = Doc(title='', text=text, source='mturk', type=doc_type)
    if 'source_url' in data:
        doc.source = data['source_url']
    doc.save()

    res = {
        'doc_id': str(doc.id),
        'sents': list(),
        'seq': doc.seq,
        'title': doc.title,
        'created_at': doc.created_at.isoformat(),
    }
    for index in range(0, len(sents)):
        sent = Sent(index=index, text=sents[index], doc=doc).save()
        res['sents'].append(sent.dump())

    return json.dumps(res)


@is_user
def mturk_doc_page(doc_id):
    try:
        doc = Doc.objects.get(id=doc_id)
    except Exception as e:
        return redirect('/404')

    doc_log = DocLog(doc=doc, ip=request.remote_addr)
    doc_log.save()

    return render_template('mturk/doc.html', doc=doc, g=g, ENCRYPTION_KEY=config.Config.ENCRYPTION_KEY)


@is_user
def mturk_doc_page_v2(doc_id, doc_type):
    try:
        doc = Doc.objects.get(id=doc_id)
    except Exception as e:
        return redirect('/404')

    doc_log = DocLog(doc=doc, ip=request.remote_addr)
    doc_log.save()

    return render_template('mturk/{}/doc.html'.format(doc_type), doc=doc, g=g, ENCRYPTION_KEY=config.Config.ENCRYPTION_KEY)


@is_admin
def review_index_page(user_id):
    try:
        user = User.objects.get(id=user_id)
    except Exception as e:
        return redirect('/404')

    doc_map = dict()
    annotations = Annotation.objects(user=user).order_by('-created_at')

    for annotation in annotations:
        try:
            # for situation in which the annotated document was deleted
            doc = annotation.doc
        except Exception:
            continue

        if not (doc.id in doc_map):
            sent_total = Sent.objects(doc=doc).count()
            annotation_sent_total = Annotation.objects(doc=doc, user=user, type='sentence').count()
            doc_map[doc.id] = {
                'doc': doc,
                'sent_total': sent_total,
                'annotation_sent_total': annotation_sent_total,
                'progress': annotation_sent_total / sent_total * 100,
                'annotation_total': Annotation.objects(doc=doc, user=user).count(),
                'review_total': AnnotationReview.objects(doc=doc, user=g.user).count(),
            }

    return render_template('review/index.html', doc_map=doc_map, user=user, g=g)


@is_admin
def review_doc_page(user_id, doc_id):
    try:
        doc = Doc.objects.get(id=doc_id)
        user = User.objects.get(id=user_id)
    except Exception as e:
        return redirect('/404')

    doc_log = DocLog(user=user, doc=doc, ip=request.remote_addr)
    doc_log.save()

    return render_template('review/doc.html', doc=doc, annotator=user, g=g, ENCRYPTION_KEY=config.Config.ENCRYPTION_KEY)


@is_admin
def get_review_annotation(user_id, doc_id):
    try:
        doc = Doc.objects.get(id=doc_id)
        user = User.objects.get(id=user_id)
    except Exception as e:
        return redirect('/404')
    annotations = Annotation.objects(doc=doc, user=user)

    data = []
    for annotation in annotations:
        try:
            annotation_review = AnnotationReview.objects().get(annotation=annotation, user=g.user)
            annotation.basket = utils.merge_dict(annotation.basket, annotation_review.basket)
        except AnnotationReview.DoesNotExist:
            pass

        data.append(annotation.dump())

    return json.dumps({
        'annotations': data,
    })


@is_admin
def put_review_annotation(annotation_id):
    data = request.get_json()
    basket = data['basket']

    try:
        annotation = Annotation.objects().get(id=annotation_id)
    except Exception:
        return Response('404', status=404)
    try:
        annotation_review = AnnotationReview.objects().get(annotation=annotation, user=g.user)
    except AnnotationReview.DoesNotExist:
        annotation_review = AnnotationReview(annotation=annotation, user=g.user)

    review_basket = dict()
    for key in basket:
        if '-review' in key:
            review_basket[key] = basket[key]

    annotation_review.doc = annotation.doc
    annotation_review.ip = request.remote_addr
    annotation_review.basket = review_basket
    annotation_review.updated_at = datetime.datetime.now
    annotation_review.save()

    annotation.basket = utils.merge_dict(annotation.basket, review_basket)

    return json.dumps({
        'annotation': annotation.dump(),
    })


@is_admin
def delete_review_annotation(annotation_id):
    try:
        annotation = Annotation.objects().get(id=annotation_id)
        annotation_review = AnnotationReview.objects().get(annotation=annotation, user=g.user)
        annotation_review.delete()
    except AnnotationReview.DoesNotExist:
        return Response('not found', status=404)

    return Response('success', status=200)
