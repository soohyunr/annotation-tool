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


def tokenize_and_lemmatize(text):
    stems = []
    text = text.lower()
    words = [word for word in word_tokenize(text) if word.isalpha()]
    words = [word for word in words if word not in stop_words]
    for word in words: stems.append(lemmatizer.lemmatize(word, pos='v'))
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
    bin_path = './data/pkl/annotations_with_sent.pkl'
    if os.path.exists(bin_path):
        dumps = pickle.load(open(bin_path, "rb"))
    else:
        print('generate ' + bin_path)
        annotations = Annotation.objects(type='sentence')
        for annotation in tqdm(annotations):
            try:
                row = annotation.dump()
                row['sentence'] = annotation.sent.text
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
            option['sentence'] = annotation['sentence']

            # reason_key = '{}-{}'.format(option['user'], ''.join(tokenize_and_lemmatize(reason)))
            # if reason_key in reason_set:
            #     continue
            # reason_set.add(reason_key)

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
            # ('user', Pipeline([
            #     ('selector', NumberSelector(key='user')),
            #     ('onehot', OneHotEncoder(categories='auto'))
            # ])),
        ],
        # weight components in FeatureUnion
        transformer_weights={
            'reason': 1.0,
            # 'user': 0.5,
        },
    )

    X = vectorizer.fit_transform(df)

    true_k = 10
    from sklearn.cluster import KMeans
    model = KMeans(n_clusters=true_k, init='k-means++', max_iter=100, n_init=1)
    model.fit(X)

    df['cluster'] = model.labels_

    for c in range(true_k):
        print('\ncluster {}'.format(c))

        dis = model.transform(X)[:, c]
        dis = [(i, dis[i]) for i in range(len(dis))]
        dis = sorted(dis, key=lambda x: x[1])

        # dis = dis[:50]
        # random.shuffle(dis)

        for item in dis[:10]:
            doc_id = item[0]
            print('[{}] reason: {}'.format(df.iloc[doc_id]['user_name'], df.iloc[doc_id]['reason']))


def load_glove():
    with open("/Users/seungwon/Desktop/data/glove/glove.6B.300d.txt", "rb") as lines:
        print('Load glove')
        w2v = dict()
        for line in tqdm(lines):
            word = line.split()[0].decode('utf-8')
            vector = list(map(float, line.split()[1:]))
            w2v[word] = vector
        return w2v


def get_ngrams(tokens, n):
    ngrams_ = ngrams(tokens, n)
    return [' '.join(grams) for grams in ngrams_]


def get_top_phrase(sents):
    frequencies = defaultdict(lambda: 0)
    grams = []
    for sent in sents:
        grams += get_ngrams(tokenize_and_lemmatize(clean_reason(sent)), 2)

    for gram in grams:
        frequencies[gram] += 1

    top_phrase = frequencies.items()
    top_phrase = sorted(top_phrase, key=lambda x: -x[1])
    return top_phrase


def clustering_with_glove(df, w2v, file_key):
    from sklearn.base import BaseEstimator, TransformerMixin
    from sklearn.pipeline import FeatureUnion, Pipeline
    from sklearn.preprocessing import OneHotEncoder, LabelEncoder
    from sklearn.feature_extraction.text import TfidfVectorizer

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

    class MeanEmbeddingVectorizer(object):
        def __init__(self, word2vec):
            self.word2vec = word2vec
            # if a text is empty we should return a vector of zeros
            # with the same dimensionality as all the other vectors
            self.dim = 300

        def fit(self, X, y):
            return self

        def transform(self, X):
            arr = []
            for line in tqdm(X):
                line = clean_reason(line)
                words = tokenize_and_lemmatize(line)
                words = [self.word2vec[w] for w in words if w in self.word2vec]
                vector = np.mean(words or [np.zeros(self.dim)], axis=0)

                arr.append(vector)
            return np.array(arr)

    vectorizer = FeatureUnion(
        transformer_list=[
            ('reason', Pipeline([
                ('selector', TextSelector(key='reason')),
                ('glove mean', MeanEmbeddingVectorizer(w2v))
            ])),
            # ('user', Pipeline([
            #     ('selector', NumberSelector(key='user')),
            #     ('onehot', OneHotEncoder(categories='auto'))
            # ])),
        ],
        # weight components in FeatureUnion
        transformer_weights={
            'reason': 1.0,
            # 'user': 0.5,
        },
    )

    X = vectorizer.fit_transform(df)

    true_k = 6
    from sklearn.cluster import KMeans
    model = KMeans(n_clusters=true_k, init='k-means++', max_iter=300, n_init=1)
    model.fit(X)

    df['cluster'] = model.labels_

    with open('./data/clustering/{}.txt'.format(file_key), 'w+') as f:
        f.write(file_key + '\n')
        for c in range(true_k):
            f.write('\ncluster {}\n'.format(c))
            dis = model.transform(X)[:, c]
            dis = [(i, dis[i]) for i in range(len(dis))]
            dis = sorted(dis, key=lambda x: x[1])

            dis = dis[:30]
            random.shuffle(dis)

            reasons = []
            for item in dis:
                doc_id = item[0]
                reasons.append(df.iloc[doc_id]['reason'])
            top_phrase = get_top_phrase(reasons)
            top_phrase = ['{}({})'.format(phrase[0], phrase[1]) for phrase in top_phrase]
            f.write('title: {}\n\n'.format(', '.join(top_phrase[:4])))

            for item in dis[:10]:
                doc_id = item[0]
                f.write('[{}] reason: {}\n'.format(df.iloc[doc_id]['user_name'], df.iloc[doc_id]['reason']))


def write_all_reason(df, file_key):
    with open('./data/reason/{}.txt'.format(file_key), 'w+') as f:
        for index in range(len(df)):
            # f.write(df.iloc[index]['sentence'] + '\n')
            f.write('[{}] reason: {}\n'.format(df.iloc[index]['user_name'], df.iloc[index]['reason']))



if __name__ == '__main__':
    connect(**config.Config.MONGODB_SETTINGS)
    attribute_reason = get_attribute_reason()

    attribute_keys = ['Knowledge_Awareness', 'Verifiability', 'Disputability', 'Acceptance']

    w2v = load_glove()
    total = 0
    for attribute_key in attribute_keys:
        for attribute_value in attribute_reason[attribute_key]:
            options = attribute_reason[attribute_key][attribute_value]

            file_key = '{}-{}'.format(attribute_key, attribute_value)
            print(file_key)
            print('options number :', len(options))
            total += len(options)

            df = pd.DataFrame({
                'reason': [option['reason'] for option in options],
                'user': [option['user'] for option in options],
                'user_name': [option['user_name'] for option in options],
                'sentence': [option['sentence'] for option in options],
            })
            # print(df['reason'])
            write_all_reason(df, file_key)
            # try:
            #     clustering_with_glove(df, w2v, file_key)
            #     # clustering(df)
            # except Exception as e:
            #     logging.exception(e)

    print('total : ', total)
