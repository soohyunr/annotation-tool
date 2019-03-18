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


def clean_reason(reason):
    reason = reason.lower()
    reason = reason.replace("'d", ' had')
    reason = reason.replace("n't", ' not')

    for punct in "/-'":
        reason = reason.replace(punct, ' ')
    for punct in '&':
        reason = reason.replace(punct, ' {} '.format(punct))
    for punct in '?!.,"#$%\'()*+-/:;<=>@[\\]^_`{|}~' + '“”’':
        reason = reason.replace(punct, '')
    return reason


def tokenize_and_lemmatize(text):
    stems = []
    text = text.lower()
    words = [word for word in word_tokenize(text) if word.isalpha()]
    # words = [word for word in words if word not in stop_words]
    for word in words: stems.append(lemmatizer.lemmatize(word, pos='v'))
    return stems


def get_attribute_reason():
    attribute_reason = defaultdict(lambda: defaultdict(lambda: []))
    dumps = []
    bin_path = './data/bin/annotations_clustering.bin'
    if os.path.exists(bin_path):
        dumps = pickle.load(open(bin_path, "rb"))
    else:
        print('generate ' + bin_path)
        annotations = Annotation.objects(type='sentence')
        for annotation in tqdm(annotations):
            try:
                row = annotation.dump()
                row['user_name'] = annotation.user.first_name + ' ' + annotation.user.last_name
                dumps.append(row)
            except Exception as e:
                logging.exception(e)
        pickle.dump(dumps, open(bin_path, "wb"))

    random.shuffle(dumps)

    reason_set = set()
    for annotation in tqdm(dumps):
        basket = annotation['basket']

        for attribute_key in basket:
            option = basket[attribute_key]
            if not ('reason' in option):
                continue

            attribute_value = option['value']
            reason = option['reason']

            if not reason:
                continue

            option['user'] = annotation['user']
            option['user_name'] = annotation['user_name']

            reason_key = '{}-{}'.format(option['user'], ''.join(tokenize_and_lemmatize(reason)))
            if reason_key in reason_set:
                continue
            reason_set.add(reason_key)
            attribute_reason[attribute_key][attribute_value].append(option)

    return attribute_reason


def load_glove():
    with open("/Users/seungwon/Desktop/data/glove/glove.6B.300d.txt", "rb") as lines:
        print('Load glove')
        w2v = dict()
        for line in tqdm(lines):
            word = line.split()[0].decode('utf-8')
            vector = list(map(float, line.split()[1:]))
            w2v[word] = vector
        return w2v


def clustering(reasons, w2v):
    from scipy.cluster.hierarchy import ward, dendrogram

    X = []
    for reason in reasons:
        line = clean_reason(reason)
        words = tokenize_and_lemmatize(line)
        words = [w2v[w] for w in words if w in w2v]
        vector = np.mean(words or [np.zeros(300)], axis=0)
        X.append(vector)

    from sklearn.metrics.pairwise import cosine_similarity
    dist = 1 - cosine_similarity(X)

    linkage_matrix = ward(dist)  # define the linkage_matrix using ward clustering pre-computed distances

    fig, ax = plt.subplots(figsize=(15, 20))  # set size
    ax = dendrogram(linkage_matrix, orientation="right", labels='');

    plt.tick_params(
        axis='x',  # changes apply to the x-axis
        which='both',  # both major and minor ticks are affected
        bottom='off',  # ticks along the bottom edge are off
        top='off',  # ticks along the top edge are off
        labelbottom='off')
    plt.tight_layout()  # show plot with tight layout

    # uncomment below to save figure
    plt.savefig('./data/dendrogram/ward_clusters.png', dpi=200)


if __name__ == '__main__':
    connect(**config.Config.MONGODB_SETTINGS)
    attribute_reason = get_attribute_reason()

    attribute_keys = ['Knowledge_Awareness', 'Verifiability', 'Disputability', 'Perceived_Author_Credibility', 'Acceptance']

    w2v = load_glove()
    for attribute_key in attribute_keys:
        for attribute_value in attribute_reason[attribute_key]:
            options = attribute_reason[attribute_key][attribute_value]

            reasons = [option['reason'] for option in options]
            clustering(reasons, w2v)

            break
