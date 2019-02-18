import os, json, random, pickle
import logging
from mongoengine import connect
from mongoengine.queryset.visitor import Q
from tqdm import tqdm
from collections import defaultdict

from models import Doc, User, Sent, Annotation
import config


def clean_text(x):
    x = str(x)
    for punct in "/-'":
        x = x.replace(punct, ' ')
    for punct in '&':
        x = x.replace(punct, ' {} '.format(punct))
    for punct in '?!.,"#$%\'()*+-/:;<=>@[\\]^_`{|}~' + '“”’':
        x = x.replace(punct, '')
    return x


def draw_word_cloud():
    """
    attribute_reason = {
        'Knowledge_Awareness': {
            'I_did_not_know_the_information': [],
        },
    }
    """
    attribute_reason = defaultdict(lambda: defaultdict(lambda: []))

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

    from nltk import ngrams, word_tokenize
    from nltk.corpus import stopwords
    from nltk.stem.snowball import SnowballStemmer
    from nltk.stem import WordNetLemmatizer

    stop_words = set(stopwords.words('english'))
    lemmatizer = WordNetLemmatizer()
    stemmer = SnowballStemmer("english", ignore_stopwords=True)

    def get_ngrams(tokens, n):
        ngrams_ = ngrams(tokens, n)
        return [' '.join(grams) for grams in ngrams_]

    for annotation in tqdm(dumps):
        basket = annotation['basket']

        for attribute_key in basket:
            option = basket[attribute_key]
            if not ('reason' in option):
                continue

            value = option['value']
            reason = option['reason']

            if not reason:
                continue

            reason = reason.lower()
            reason = reason.replace("'s", '')
            reason = reason.replace("'d", ' had')
            reason = reason.replace("n't", ' not')
            reason = reason.replace('.', '')
            reason = reason.replace(',', '')
            reason = reason.replace('the', '')
            reason = reason.replace('would', '')
            reason = reason.replace('could', '')

            reason = clean_text(reason)

            tokens = word_tokenize(reason)
            clean_tokens = []
            for token in tokens:
                if token not in stop_words or token == 'not':
                    # token = stemmer.stem(token)
                    token = lemmatizer.lemmatize(token, pos='v')
                    clean_tokens.append(token)

            # attribute_reason[attribute_key][value] += get_ngrams(clean_tokens, 2)
            attribute_reason[attribute_key][value] += get_ngrams(clean_tokens, 3)

    frequencies = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: 0)))
    for attribute_key in attribute_reason:
        for option in attribute_reason[attribute_key]:
            for reason in attribute_reason[attribute_key][option]:
                frequencies[attribute_key][option][reason] += 1

    import matplotlib.pyplot as plt
    from wordcloud import WordCloud

    # attribute_key = 'Perceived_Author_Credibility'
    # attribute_key = 'Knowledge_Awareness'
    # attribute_key = 'Verifiability'
    # attribute_key = 'Disputability'
    attribute_key = 'Acceptance'
    max_words = 150

    for option in attribute_reason[attribute_key]:
        target = frequencies[attribute_key][option]

        if len(target.keys()) < max_words:
            continue

        print('{}-{}'.format(attribute_key, option))

        wordcloud = WordCloud(
            width=1200,
            height=1200,
            font_path='/Library/Fonts/NotoSans-Black.ttf',
            background_color='white',
            max_font_size=140,
            max_words=max_words,
        ).generate_from_frequencies(target)

        plt.figure(figsize=(20, 20))
        plt.imshow(wordcloud)
        plt.axis('off')
        plt.savefig('./plt/{}-{}'.format(attribute_key, option))


if __name__ == '__main__':
    connect(**config.Config.MONGODB_SETTINGS)

    draw_word_cloud()
