import os, json, random, pickle, datetime, pytz
import logging
from mongoengine import connect
from mongoengine.queryset.visitor import Q
from tqdm import tqdm
from collections import defaultdict
import pandas as pd
from matplotlib import pyplot as plt
import dateutil.parser
import numpy as np

from nltk import ngrams, word_tokenize
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer
from nltk.stem import WordNetLemmatizer

stop_words = set(stopwords.words('english'))
lemmatizer = WordNetLemmatizer()
stemmer = SnowballStemmer("english", ignore_stopwords=True)

from models import Doc, User, Sent, Annotation
import config


def get_annotations():
    dumps = []
    bin_path = './data/bin/annotations_time.bin'
    if os.path.exists(bin_path):
        dumps = pickle.load(open(bin_path, "rb"))
    else:
        print('generate ' + bin_path)
        annotations = Annotation.objects(type='sentence')
        for annotation in tqdm(annotations):
            try:
                if not ('Acceptance' in annotation['basket']):
                    continue
                dump = annotation.dump()
                dump['is_turk'] = not annotation.user.is_active
                dumps.append(dump)
            except Exception as e:
                logging.exception(e)
        pickle.dump(dumps, open(bin_path, "wb"))

    random.shuffle(dumps)
    return dumps


def draw_attribute_distribution(anntations):
    keys = ['Knowledge_Awareness', 'Verifiability', 'Disputability', 'Perceived_Author_Credibility', 'Acceptance']
    for key in keys:
        success = 0
        fail = 0
        time_avg = 0
        times = []
        for annotation in tqdm(annotations):
            if not ('opened_at' in annotation['basket'][key]):
                fail += 1
                continue
            if not ('updated_at' in annotation['basket'][key]):
                fail += 1
                continue

            opened_at = dateutil.parser.parse(annotation['basket'][key]['opened_at'])
            updated_at = dateutil.parser.parse(annotation['basket'][key]['updated_at'])
            diff = (updated_at - opened_at)
            if diff.total_seconds() < 0:
                fail += 1
                continue

            if diff.total_seconds() > 60:
                fail += 1
                continue

            success += 1
            times.append(diff.total_seconds())
            time_avg += diff.total_seconds()

        time_avg /= success
        print('{} : {}\n'.format(key, time_avg))
        print('success: {}, fail: {}\n\n'.format(success, fail))

        # print('times :', times)
        times = np.array(times)
        plt.hist(times, [i for i in range(0, 30, 1)], histtype='bar', rwidth=0.9)
        plt.ylabel('Frequency')
        plt.xlabel('Seconds')
        plt.title('{} (avg: {:.2f})'.format(key, times.mean()), y=1.05)
        # plt.show()
        plt.grid(b=True, which='major', color='#999999', linestyle='-', alpha=0.2)
        plt.savefig('./data/time/{}.png'.format(key))
        plt.close()


def draw_group_distribution(annotations):
    success = 0
    fail = 0
    times = []
    for annotation in tqdm(annotations):
        if annotation['is_turk']:
            continue

        created_at = dateutil.parser.parse(annotation['created_at'])
        updated_at = dateutil.parser.pmarse(annotation['updated_at'])

        diff = (updated_at - created_at)

        if diff.total_seconds() > 1000:
            fail += 1
            continue

        success += 1
        times.append(diff.total_seconds())

    times = np.array(times)
    plt.hist(times, [i for i in range(0, 400, 20)], histtype='bar', rwidth=0.9)
    print('success: {}, fail: {}\n\n'.format(success, fail))
    plt.ylabel('Frequency')
    plt.xlabel('Seconds')
    plt.title('Student Annotation (avg: {:.2f})'.format(times.mean()), y=1.05)
    # plt.show()
    plt.grid(b=True, which='major', color='#999999', linestyle='-', alpha=0.2)
    plt.savefig('./data/time/student_annotation.png')
    plt.close()


def check_reason_ratio(annotations):
    keys = ['Knowledge_Awareness', 'Verifiability', 'Disputability', 'Acceptance']
    for key in keys:
        found = 0
        not_found = 0
        total = 0
        for annotation in annotations:

            total += 1
            reason = annotation['basket'][key]['reason']

            if reason:
                found += 1
            else:
                not_found += 1

        print('{} : {}/{}({:.2f}%)'.format(key, found, total, found / total * 100))


def check_select_reason_diff(annotations):
    # 'Knowledge_Awareness', 'Verifiability', 'Disputability', 'Perceived_Author_Credibility', 'Acceptance'
    keys = ['Knowledge_Awareness', 'Verifiability', 'Disputability', 'Acceptance']

    success = 0
    fail = 0
    select_time_sum = 0
    annotation_time_sum = 0
    for annotation in tqdm(annotations):
        select_time = 0
        annotation_time = dateutil.parser.parse(annotation['updated_at']) - dateutil.parser.parse(annotation['created_at'])
        annotation_time = annotation_time.total_seconds()
        if annotation_time > 1800:
            fail += 1
            continue
        try:
            for key in keys:
                opened_at = dateutil.parser.parse(annotation['basket'][key]['opened_at'])
                updated_at = dateutil.parser.parse(annotation['basket'][key]['updated_at'])
                diff = (updated_at - opened_at)
                if diff.total_seconds() < 0 or diff.total_seconds() > 600:
                    fail += 1
                    raise ValueError
                select_time += diff.total_seconds()
        except Exception as e:
            fail += 1
            # logging.exception(e)
            continue

        success += 1
        annotation_time_sum += annotation_time
        select_time_sum += select_time

    print('success: {}, fail: {}\n'.format(success, fail))
    print('total: {}, select: {}, reason: {}\n'.format(annotation_time_sum / success, select_time_sum / success, (annotation_time_sum - select_time_sum) / success))


if __name__ == '__main__':
    # connect(**config.Config.MONGODB_SETTINGS)
    annotations = get_annotations()

    # draw_attribute_distribution(annotations)
    # draw_group_distribution(annotations)
    # check_reason_ratio(annotations)
    check_select_reason_diff(annotations)
