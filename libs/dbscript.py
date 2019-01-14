import os, json

from mongoengine import connect

from models import Doc, User, Sent
import config


def insert_doc(title, text, source):
    doc = Doc(title=title, text=text, source=source)
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

    for filename in filenames:
        print('filename : {}'.format(filename))
        path = os.path.join(dir_path, filename)

        with open(path, 'r') as f:
            text = f.read()
            if len(text) == 0:
                continue
            insert_doc(title=filename, source=source, text=text)


def db_backup(memo):
    import datetime
    collections = ['doc', 'sent', 'annotation', 'user', 'doc_log']

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

    doc = Doc.objects().get(seq=seq_id)
    sents = Sent.objects(doc=doc).order_by('index')

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
    for doc in docs:
        generate_encrypted_file(seq_id=doc.seq)



if __name__ == '__main__':
    connect(**config.Config.MONGODB_SETTINGS)

    # insert_dataset('XXX_paragraph_to_annotate', source='XXX')
    # db_backup('')

    # generate_encrypted_files()

    delete_doc('5c3c3975995fc1ab555950ea')
