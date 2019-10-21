import os, json
from tqdm import tqdm

from bson import json_util
from mongoengine import connect

from models import Doc, User, Sent, Annotation
import config


def is_ok(annotations):
    for annotation in annotations:
        if annotation.user.username == 'annotator1':
            return False

        if 'Acceptance' not in annotation['basket']:
            return False

        if not annotation['basket']['Acceptance']['value']:
            return False

    return True


def export_dataset_v3():
    docs = Doc.objects.filter(type='mturk_v3')

    data = []
    for doc in tqdm(docs):
        sents = Sent.objects(doc=doc)
        annotations = Annotation.objects(doc=doc)

        if sents.count() != annotations.count():
            continue

        source = doc.source
        if 'aljazeera' not in source and 'foxnews' not in source and 'theguardian' not in source:
            continue

        if not is_ok(annotations):
            continue

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

    dataset_path = os.path.abspath(os.path.dirname(__file__) + '/../data/dataset_AMT_v3.json')
    data_json = json.dumps(data, default=json_util.default)
    with open(dataset_path, 'w', encoding='utf-8') as f:
        f.write(data_json)


if __name__ == '__main__':
    connect(**config.Config.MONGODB_SETTINGS)

    export_dataset_v3()
