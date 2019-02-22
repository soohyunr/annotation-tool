import os, json, random, pickle
import logging
from mongoengine import connect
from tqdm import tqdm
from collections import defaultdict

from models import Doc, User, Sent, Annotation
import config


def draw_daily_amount_chart():
    annotations = Annotation.objects(type='sentence')

    dumps = []
    bin_path = './annotations.bin'
    if os.path.exists(bin_path):
        dumps = pickle.load(open(bin_path, "rb"))
    else:
        print('generate ' + bin_path)
        for annotation in tqdm(annotations):
            try:
                if not ('Acceptance' in annotation['basket']):
                    continue
                if not ('value' in annotation['basket']['Acceptance']):
                    continue
                dumps.append(annotation.dump())
            except Exception as e:
                logging.exception(e)
        pickle.dump(dumps, open(bin_path, "wb"))

    random.shuffle(dumps)

    day_count = defaultdict(lambda: 0)
    import dateutil.parser
    for annotation in tqdm(dumps):
        date = dateutil.parser.parse(annotation['created_at'])
        date_str = '{}-{}-{}'.format(date.year, date.month, date.day)
        day_count[date_str] += 1

    xy = day_count.items()

    def compare(item):
        s = item[0].split('-')
        s = [int(si) for si in s]
        return s[0] * 365 + s[1] * 31 + s[2]

    xy = sorted(xy, key=compare)
    x = [item[0] for item in xy]
    y = [item[1] for item in xy]
    sy = [0] * len(x)
    sy[0] = y[0]
    for i in range(1, len(sy)):
        sy[i] = y[i] + sy[i - 1]

    print('sy :', sy)


if __name__ == '__main__':
    connect(**config.Config.MONGODB_SETTINGS)
draw_daily_amount_chart()
