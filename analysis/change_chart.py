import os, json, random, pickle
import logging
from mongoengine import connect
from tqdm import tqdm
from collections import defaultdict

from models import Doc, User, Sent, Annotation
import config


def get_annotations():
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
    return dumps


def draw_daily_amount_chart(annotations):
    day_count = defaultdict(lambda: 0)
    import dateutil.parser
    from datetime import datetime, timedelta

    for annotation in tqdm(annotations):
        date = dateutil.parser.parse(annotation['created_at'])
        day_count[date.strftime('%y-%m-%d')] += 1

    x = []
    y = []
    date = datetime.strptime('18-10-10', '%y-%m-%d')
    while date < datetime.now():
        date_key = date.strftime('%y-%m-%d')
        x.append(date_key)
        s = day_count[date_key]
        if len(y):
            s += y[-1]
        y.append(s)
        date += timedelta(days=1)

    def sampling(x, y):
        rs = []
        ry = []
        for i in range(0, len(x)):
            if i % 8 == 0:
                rs.append(x[i])
                ry.append(y[i])
        return rs, ry

    x, y = sampling(x, y)

    # print(list(zip(x, y)))

    from matplotlib import pyplot as plt
    fig, ax = plt.subplots()

    fig.autofmt_xdate()
    plt.bar(x, y)

    plt.grid(b=True, which='major', color='#999999', linestyle='-', alpha=0.2)

    plt.show()


if __name__ == '__main__':
    connect(**config.Config.MONGODB_SETTINGS)
    annotations = get_annotations()
    draw_daily_amount_chart(annotations)
