import os, json, random, pickle
from tqdm import tqdm
import logging

from mongoengine import connect
from mongoengine.queryset.visitor import Q

from models import Doc, User, Sent, Annotation
from tqdm import tqdm
import config


def analysis_reason():
    annotations = Annotation.objects(type='sentence')
    count = annotations.count()

    attribute_key = 'Knowledge_Awareness'
    attribute_value = 'I_did_not_know_the_information'

    dumps = []
    bin_path = './annotations.bin'
    if os.path.exists(bin_path):
        print(bin_path + ' exist!')
        dumps = pickle.load(open(bin_path, "rb"))
    else:
        for annotation in tqdm(annotations):
            try:
                dumps.append(annotation.dump())
            except Exception as e:
                print('annotation_id :', annotation.id)
                logging.exception(e)
                annotation.delete()
        pickle.dump(dumps, open(bin_path, "wb"))

    random.shuffle(dumps)

    with open('./{}.txt'.format(attribute_key), 'w+') as f:
        for annotation in tqdm(dumps):
            if attribute_key in annotation['basket']:
                try:
                    item = annotation['basket'][attribute_key]
                    print('item :', item)
                    if item['value'] != attribute_value:
                        continue

                    if not item['reason']:
                        continue

                    doc = Doc.objects.get(id=annotation['doc'])

                    f.write(annotation['entire_text'] + '\n')
                    f.write('Value: ' + item['value'] + '\n')
                    f.write('Reason: ' + item['reason'] + '\n')
                    f.write('Doc Type: ' + doc['type'] + '\n')
                    f.write('\n')
                    count += 1
                except Exception as e:
                    logging.exception(e)
    print('count : ', count)


if __name__ == '__main__':
    connect(**config.Config.MONGODB_SETTINGS)
    analysis_reason()
