import os, json
from tqdm import tqdm

from mongoengine import connect

from models import Doc, User, Sent,Annotation
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
            elif key =='Acceptance_of_the_sentence_as_true':
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


if __name__ == '__main__':
    connect(**config.Config.MONGODB_SETTINGS)

    # insert_dataset('XXX_paragraph_to_annotate', source='XXX')
    # insert_dataset('v2/guardian_paragraph_to_annotate', source='guardian')
    db_backup('')
    # delete_duplicate_annotations()
    # change_all_attribute_key()
    # doc_migration()
    # generate_encrypted_files()
    # target_migration()

    # delete_doc('5c3c3975995fc1ab555950ea')
