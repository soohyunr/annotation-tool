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
    bin_path = './data/bin/annotations.bin'
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
                dump = annotation.dump()
                dump['is_turk'] = not annotation.user.is_active
                dumps.append(dump)
            except Exception as e:
                logging.exception(e)
        pickle.dump(dumps, open(bin_path, "wb"))

    random.shuffle(dumps)
    return dumps


def draw_daily_amount_chart_with_turk(annotations):
    day_student_count = defaultdict(lambda: 0)
    day_turk_count = defaultdict(lambda: 0)
    import dateutil.parser
    from datetime import datetime, timedelta

    for annotation in tqdm(annotations):
        date = dateutil.parser.parse(annotation['created_at'])
        date_key = date.strftime('%y-%m-%d')
        if annotation['is_turk']:
            day_turk_count[date_key] += 1
        else:
            day_student_count[date_key] += 1

    x = []
    sy = []
    ty = []
    date = datetime.strptime('18-10-10', '%y-%m-%d')
    while date < datetime.now():
        date_key = date.strftime('%y-%m-%d')
        x.append(date_key)
        item = day_student_count[date_key]
        if len(sy):
            item += sy[-1]
        sy.append(item)
        item = day_turk_count[date_key]
        if len(ty):
            item += ty[-1]
        ty.append(item)
        date += timedelta(days=1)

    import pandas as pd
    df = pd.DataFrame(columns=['date', 'student', 'turker', 'sum'])
    for i in range(len(x)):
        df.loc[i] = [x[i], sy[i], ty[i], sy[i]+ty[i]]

    writer = pd.ExcelWriter('./data/chart/number_of_annotations.xlsx', engine='xlsxwriter')
    df.to_excel(writer, sheet_name='Sheet1')
    writer.save()

    def sampling(x):
        res = []
        for i in range(0, len(x)):
            if i % 8 == 0:
                res.append(x[i])
        return res

    x = sampling(x)
    ty = sampling(ty)
    sy = sampling(sy)

    # print(list(zip(x, y)))

    from matplotlib import pyplot as plt
    fig, ax = plt.subplots()

    fig.autofmt_xdate()
    plt.bar(x, sy, label='Student')
    plt.bar(x, ty, bottom=sy, label='Turker')

    plt.grid(b=True, which='major', color='#999999', linestyle='-', alpha=0.2)
    plt.legend(loc='upper left')

    plt.show()
    fig.savefig('./data/chart/number_of_annotations2.png')





if __name__ == '__main__':
    connect(**config.Config.MONGODB_SETTINGS)
    annotations = get_annotations()
    draw_daily_amount_chart_with_turk(annotations)
