import os, random, pickle
import logging
from mongoengine import connect
from tqdm import tqdm
from collections import defaultdict
import pandas as pd
import matplotlib as mpl
from matplotlib import pyplot as plt
import numpy as np

from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer
from nltk.stem import WordNetLemmatizer

stop_words = set(stopwords.words('english'))
lemmatizer = WordNetLemmatizer()
stemmer = SnowballStemmer("english", ignore_stopwords=True)

from models import Doc, User, Sent, Annotation
import config


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

            from analysis.data_util import tokenize_and_lemmatize
            reason_key = '{}-{}'.format(option['user'], ''.join(tokenize_and_lemmatize(reason)))
            if reason_key in reason_set:
                continue
            reason_set.add(reason_key)
            attribute_reason[attribute_key][attribute_value].append(option)

    return attribute_reason


def clustering(reasons, w2v, file_key):
    from scipy.cluster import hierarchy
    from analysis.data_util import clean_text, tokenize_and_lemmatize

    X = []
    for reason in reasons:
        line = clean_text(reason)
        words = tokenize_and_lemmatize(line)
        words = [w2v[w] for w in words if w in w2v]
        vector = np.mean(words or [np.zeros(300)], axis=0)
        X.append(vector)

    from sklearn.metrics.pairwise import cosine_similarity
    dist = 1 - cosine_similarity(X)

    linkage_matrix = hierarchy.ward(dist)  # define the linkage_matrix using ward clustering pre-computed distances

    from matplotlib.pyplot import cm
    cmap = cm.rainbow(np.linspace(0, 1, 5))
    hierarchy.set_link_color_palette([mpl.colors.rgb2hex(rgb[:3]) for rgb in cmap])

    # hierarchy.set_link_color_palette(['m', 'c', 'y', 'k'])
    fig, ax = plt.subplots(figsize=(20, 40))  # set size
    ax = hierarchy.dendrogram(linkage_matrix, orientation="right", labels=reasons)

    plt.tick_params(
        axis='x',  # changes apply to the x-axis
        which='both',  # both major and minor ticks are affected
        bottom='off',  # ticks along the bottom edge are off
        top='off',  # ticks along the top edge are off
        labelbottom='off')
    plt.tight_layout()  # show plot with tight layout

    # uncomment below to save figure
    plt.savefig('./data/dendrogram/{}.png'.format(file_key), dpi=200)
    plt.close()


if __name__ == '__main__':
    connect(**config.Config.MONGODB_SETTINGS)
    attribute_reason = get_attribute_reason()

    # ['Knowledge_Awareness', 'Verifiability', 'Disputability', 'Perceived_Author_Credibility', 'Acceptance']
    attribute_keys = ['Acceptance']
    from analysis.data_util import load_glove

    w2v = load_glove()
    for attribute_key in attribute_keys:
        for attribute_value in attribute_reason[attribute_key]:
            options = attribute_reason[attribute_key][attribute_value]

            file_key = '{}-{}'.format(attribute_key, attribute_value)
            reasons = [option['reason'] for option in options]
            random.shuffle(reasons)

            print('file_key :', file_key)
            from summa import keywords

            print(keywords.keywords('\n'.join(reasons)))
            # clustering(reasons[:300], w2v, file_key)

            break
