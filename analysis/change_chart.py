import os, json, random, pickle
import logging
from mongoengine import connect
from mongoengine.queryset.visitor import Q
from datetime import datetime
from tqdm import tqdm
from collections import defaultdict

from nltk import ngrams, word_tokenize
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer
from nltk.stem import WordNetLemmatizer

stop_words = set(stopwords.words('english'))
lemmatizer = WordNetLemmatizer()
stemmer = SnowballStemmer("english", ignore_stopwords=True)

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
                dumps.append(annotation.dump())
            except Exception as e:
                logging.exception(e)
                annotation.delete()
        pickle.dump(dumps, open(bin_path, "wb"))

    random.shuffle(dumps)

    for annotation in tqdm(dumps):
        date = datetime(annotation['createdAt'])
        print('date :', date)



if __name__ == '__main__':
    connect(**config.Config.MONGODB_SETTINGS)
    draw_daily_amount_chart()
