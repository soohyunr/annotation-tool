import os, json
from tqdm import tqdm

from mongoengine import connect

from models import Doc, User, Sent, Annotation
import config


def insert_doc(title, text, source):
    try:
        doc = Doc.objects.get(title=title)
        print('already exist -> pass')
        return
    except Doc.DoesNotExist:
        pass

    doc = Doc(title=title, text=text, source=source, type='v2')
    total = Doc.objects.count()
    doc.seq = total + 1
    doc.save()

    import re
    regex = re.compile(r'\(Sent\d{1,4}\)')

    # from nltk import sent_tokenize
    for text in text.split('\n'):
        if len(text) == 0:
            continue

        index_str = regex.findall(text)[0]
        text = text.replace(index_str, '').strip()
        index = int(index_str.replace('(Sent', '').replace(')', ''))

        Sent(index=index, text=text, doc=doc).save()


def delete_doc(doc_id):
    doc = Doc.objects().get(id=doc_id)
    sents = Sent.objects(doc=doc).order_by('index')
    for sent in sents:
        sent.delete()
    annotations = Sent.objects(doc=doc)
    for annotation in annotations:
        annotation.delete()
    doc.delete()


def insert_dataset(dirname, source):
    dir_path = os.path.abspath(os.path.dirname(__file__) + '/../data/{}'.format(dirname))
    filenames = os.listdir(dir_path)

    for filename in tqdm(filenames):
        print('filename : {}'.format(filename))
        path = os.path.join(dir_path, filename)

        # to exclude hidden files
        if filename[0] == '.':
            continue

        with open(path, 'r') as f:
            text = f.read()
            if len(text) == 0:
                continue

            insert_doc(title=filename, source=source, text=text)


def db_backup(memo):
    import datetime
    collections = ['doc', 'sent', 'annotation', 'user', 'doc_log', 'annotation_review']

    backup_dir = os.path.abspath(os.path.dirname(__file__) + '/../data/backup/' + datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S'))
    os.makedirs(backup_dir)

    memo_path = os.path.abspath(backup_dir + '/memo.txt')
    with open(memo_path, 'w') as f:
        f.write(memo)

    import subprocess

    MONGODB_SETTINGS = config.Config.MONGODB_SETTINGS
    for collection in collections:
        print('now backup collection {}'.format(collection))
        backup_path = os.path.abspath(backup_dir + '/{}'.format(collection))
        subprocess.call(['mongoexport',
                         '-h',
                         '{}:{}'.format(MONGODB_SETTINGS['host'], MONGODB_SETTINGS['port']),
                         '-u',
                         MONGODB_SETTINGS['username'],
                         '-p',
                         MONGODB_SETTINGS['password'],
                         '-d',
                         MONGODB_SETTINGS['db'],
                         '-c',
                         collection,
                         '-o',
                         backup_path,
                         ])

        # subprocess.call(['mongoimport',
        #                  '-h',
        #                  '{}:{}'.format(MONGODB_SETTINGS['host'], MONGODB_SETTINGS['port']),
        #                  '-u',
        #                  MONGODB_SETTINGS['username'],
        #                  '-p',
        #                  MONGODB_SETTINGS['password'],
        #                  '-d',
        #                  MONGODB_SETTINGS['db'],
        #                  '-c',
        #                  collection,
        #                  '-o',
        #                  backup_path,
        #                  ])


def db_restore(file_path):
    import datetime
    collections = ['doc', 'sent', 'annotation', 'user', 'doc_log', 'annotation_review']

    backup_dir = os.path.abspath(os.path.dirname(__file__) + '/../data/backup/' + file_path)

    import subprocess

    MONGODB_SETTINGS = config.Config.MONGODB_SETTINGS
    for collection in collections:
        print('now backup collection {}'.format(collection))
        backup_path = os.path.abspath(backup_dir + '/{}'.format(collection))

        subprocess.call(['mongoimport',
                         '-h',
                         '{}:{}'.format(MONGODB_SETTINGS['host'], MONGODB_SETTINGS['port']),
                         '-u',
                         MONGODB_SETTINGS['username'],
                         '-p',
                         MONGODB_SETTINGS['password'],
                         '-d',
                         MONGODB_SETTINGS['db'],
                         '-c',
                         collection,
                         '--file',
                         backup_path,
                         ])


def generate_encrypted_file(seq_id):
    from itertools import cycle
    def str_xor(s1, s2):
        result = []
        for (c1, c2) in zip(s1, cycle(s2)):
            result.append(str(ord(c1) ^ ord(c2)))
        return ",".join(result)

    try:
        doc = Doc.objects().get(seq=seq_id)
        sents = Sent.objects(doc=doc).order_by('index')
    except Exception:
        return

    data = {
        'doc_id': str(doc.id),
        'title': doc.title,
        'seq': doc.seq,
        'sents': [],
    }

    for sent in sents:
        data['sents'].append(sent.dump())

    data = json.dumps(data)
    data = str_xor(data, config.Config.ENCRYPTION_KEY)
    file_path = os.path.abspath(os.path.dirname(__file__) + '/../data/encrypted/#{}_{}'.format(seq_id, doc.title))
    with open(file_path, 'w') as f:
        f.write(data)


def generate_encrypted_files():
    docs = Doc.objects().all()
    for doc in tqdm(docs):
        if not (doc.type == 'v1' or doc.type == 'v2' or doc.type == 'v3'):
            continue
        generate_encrypted_file(seq_id=doc.seq)


def delete_duplicate_annotations():
    annotations = Annotation.objects().all()

    progress = 0
    total = annotations.count()
    for annotation in annotations:
        progress += 1
        if progress % 100 == 0:
            print('progress {}/{}'.format(progress, total))

        try:
            targets = Annotation.objects.filter(
                doc=annotation.doc,
                sent=annotation.sent,
                index=annotation.index,
                user=annotation.user,
                type=annotation.type,
                anchor_offset=annotation.anchor_offset)

            if targets.count() >= 2:
                print('count >= 2! :', targets.count())
                if targets[0].id != annotation.id:
                    targets[0].delete()
                else:
                    targets[1].delete()
        except:
            pass


def change_all_attribute_key():
    annotations = Annotation.objects().all()

    for annotation in tqdm(annotations):
        basket = annotation.basket
        new_basket = dict()

        for key in basket:
            new_key = key
            value = basket[key]
            if key == 'Disputability_of_the_sentence':
                new_key = 'Disputability'
            elif key == 'Perceived_Author_Credibility_for_the_upcoming_sentences':
                new_key = 'Perceived_Author_Credibility'
            elif key == 'Acceptance_of_the_sentence_as_true':
                new_key = 'Acceptance'
            new_basket[new_key] = value

        annotation.basket = new_basket
        annotation.save()


def doc_migration():
    docs = Doc.objects().all()
    for doc in tqdm(docs):
        if doc.mturk:
            doc.type = 'mturk'
        else:
            doc.type = 'v1'
        doc.save()


def target_migration():
    docs = Doc.objects().all()
    for doc in tqdm(docs):
        doc.text = doc.text.replace('<<TARGET>>', '(TARGET)')
        doc.save()

    sents = Sent.objects()
    for sent in tqdm(sents):
        sent.text = sent.text.replace('<<TARGET>>', '(TARGET)')
        sent.save()


def remove_invalid_annotation():
    user = User.objects.get(id='5c3c3741995fc1a8b4fa7154')
    annotations = Annotation.objects(user=user)
    for annotation in annotations:
        print('remove!')
        annotation.delete()


def duplicate_doc(from_type='v2', to_type='v3'):
    docs = Doc.objects(type=from_type).all()
    for doc in tqdm(docs):
        title = doc.title.replace('TARGET_ONLY', to_type)
        new_doc = Doc(title=title, text=doc.text, source=doc.source, type=to_type)
        new_doc.seq = Doc.objects.count() + 1
        new_doc.save()

        sents = Sent.objects(doc=doc).all()
        for sent in sents:
            Sent(index=sent.index, text=sent.text, doc=new_doc).save()


def delete_doc_type(doc_type='v3'):
    docs = Doc.objects(type=doc_type).all()
    for doc in tqdm(docs):
        delete_doc(doc.id)


def analysis_user():
    users = User.objects.filter(turker_id='A3FIO5T8LH65DM')
    total = 0
    fail = 0
    for user in users:
        annotations = Annotation.objects.filter(user=user)
        for annotation in annotations:
            total += 1
            if len(annotation.basket['Acceptance']['value']) == 0:
                fail += 1
                print(annotation.sent.index)
                print(annotation.basket['Acceptance'])
                print(annotation.doc.id)
                print(annotation.created_at)

    print('total :', total, ', fail :', fail)


if __name__ == '__main__':
    connect(**config.Config.MONGODB_SETTINGS)

    db_restore('2019-05-08T14:56:40')
    # db_backup('')
    # duplicate_doc(from_type='v2', to_type='v3')
    # generate_encrypted_files()
    # remove_invalid_annotation()

    # analysis_user()
