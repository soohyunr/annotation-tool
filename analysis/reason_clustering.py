import os, json, random, pickle
import logging
from mongoengine import connect
from mongoengine.queryset.visitor import Q
from tqdm import tqdm
from collections import defaultdict
import pandas as pd
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


def tokenize_and_stem(text):
    stems = []
    text = text.lower()
    words = [word for word in word_tokenize(text) if word.isalpha()]
    words = [word for word in words if word not in stop_words]
    for word in words: stems.append(stemmer.stem(word))
    return stems


def get_attribute_reason():
    """
    attribute_reason = {
        'Knowledge_Awareness': {
            'I_did_not_know_the_information': [],
        },
    }
    """
    attribute_reason = defaultdict(lambda: defaultdict(lambda: []))
    dumps = []
    bin_path = './annotations.bin'
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
                annotation.delete()
        pickle.dump(dumps, open(bin_path, "wb"))

    random.shuffle(dumps)

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

            attribute_reason[attribute_key][attribute_value].append(option)

    return attribute_reason


def clustering(df):
    from sklearn.base import BaseEstimator, TransformerMixin
    from sklearn.pipeline import FeatureUnion, Pipeline
    from sklearn.preprocessing import OneHotEncoder, LabelEncoder
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics import pairwise_distances_argmin_min, pairwise

    encoder = LabelEncoder()
    encoder.fit(df['user'])
    df['user'] = encoder.transform(df['user'])

    class TextSelector(BaseEstimator, TransformerMixin):
        def __init__(self, key):
            self.key = key

        def fit(self, x, y=None):
            return self

        def transform(self, data_dict):
            return data_dict[self.key]

    class NumberSelector(BaseEstimator, TransformerMixin):
        def __init__(self, key):
            self.key = key

        def fit(self, x, y=None):
            return self

        def transform(self, data_dict):
            return data_dict[[self.key]]

    vectorizer = FeatureUnion(
        transformer_list=[
            ('reason', Pipeline([
                ('selector', TextSelector(key='reason')),
                ('tfidf', TfidfVectorizer(min_df=0.1, tokenizer=tokenize_and_stem, ngram_range=(1, 2)))
            ])),
            ('user', Pipeline([
                ('selector', NumberSelector(key='user')),
                ('onehot', OneHotEncoder(categories='auto'))
            ])),
        ],
        # weight components in FeatureUnion
        transformer_weights={
            'reason': 2.0,
            'user': 0.5,
        },
    )

    X = vectorizer.fit_transform(df)

    true_k = 10
    from sklearn.cluster import KMeans
    model = KMeans(n_clusters=true_k, init='k-means++', max_iter=100, n_init=1)
    model.fit(X)

    df['cluster'] = model.labels_

    closest, _ = pairwise_distances_argmin_min(model.cluster_centers_, X)
    # print('closest :', closest)

    for c in range(true_k):
        print('\ncluster {}'.format(c))

        dis = model.transform(X)[:, c]
        dis = [(i, dis[i]) for i in range(len(dis))]
        dis = sorted(dis, key=lambda x: x[1])

        for item in dis[:5]:
            doc_id = item[0]
            print('[{}] reason: {}'.format(df.iloc[doc_id]['user_name'], df.iloc[doc_id]['reason']))


if __name__ == '__main__':
    connect(**config.Config.MONGODB_SETTINGS)

    attribute_reason = get_attribute_reason()

    # ['Knowledge_Awareness', 'Verifiability', 'Disputability', 'Perceived_Author_Credibility', 'Acceptance']
    attribute_keys = ['Acceptance']

    for attribute_key in attribute_keys:
        for attribute_value in attribute_reason[attribute_key]:
            options = attribute_reason[attribute_key][attribute_value]

            print('{}-{}'.format(attribute_key, attribute_value))
            print('options :', len(options))

            df = pd.DataFrame({
                'reason': [option['reason'] for option in options],
                'user': [option['user'] for option in options],
                'user_name': [option['user_name'] for option in options],
            })
            # print(df['reason'])

            print('Clustering')
            try:
                clustering(df)
            except:
                print('pass!!!!')
