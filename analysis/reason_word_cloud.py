import os, json, random, pickle
import logging
from mongoengine import connect
from mongoengine.queryset.visitor import Q
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


def clean_reason(reason):
    reason = reason.lower()
    reason = reason.replace("'d", ' had')
    reason = reason.replace("n't", ' not')

    for word in ['could', 'would', 'the', "'s"]:
        reason = reason.replace(word, '')
    for punct in "/-'":
        reason = reason.replace(punct, ' ')
    for punct in '&':
        reason = reason.replace(punct, ' {} '.format(punct))
    for punct in '?!.,"#$%\'()*+-/:;<=>@[\\]^_`{|}~' + '“”’':
        reason = reason.replace(punct, '')
    return reason


def get_attribute_words(attribute_key, attribute_value):
    tokens = word_tokenize(attribute_key.replace('_', ' '))
    tokens += word_tokenize(attribute_value.replace('_', ' '))
    result = []
    for token in tokens:
        token = lemmatizer.lemmatize(token, pos='v')
        result.append(token.lower())
    return result


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
        pickle.dump(dumps, open(bin_path, "wb"))

    random.shuffle(dumps)

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

            attribute_words = get_attribute_words(attribute_key, value)
            reason = clean_reason(reason)

            tokens = word_tokenize(reason)
            clean_tokens = []
            for token in tokens:
                # token = stemmer.stem(token)
                token = lemmatizer.lemmatize(token, pos='v')

                if token in stop_words and token != 'not':
                    continue

                if token in attribute_words and token != 'not':
                    continue

                clean_tokens.append(token)

            # attribute_reason[attribute_key][value] += get_ngrams(clean_tokens, 2)

            if value == 'Weak_Reject':
                print('Weak_Reject reason :', reason, ', annotation :', annotation)

            attribute_reason[attribute_key][value] += get_ngrams(clean_tokens, 3)

            if value == 'Weak_Reject':
                print('Week_Reject :', attribute_reason['Acceptance']['Weak_Reject'])

    frequencies = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: 0)))
    for attribute_key in attribute_reason:
        for option in attribute_reason[attribute_key]:
            for reason in attribute_reason[attribute_key][option]:
                frequencies[attribute_key][option][reason] += 1

    import matplotlib.pyplot as plt
    from wordcloud import WordCloud

    # attribute_key = 'Knowledge_Awareness'
    # attribute_key = 'Verifiability'
    # attribute_key = 'Disputability'
    # attribute_key = 'Perceived_Author_Credibility'
    attribute_key = 'Acceptance'
    max_words = 150

    for option in attribute_reason[attribute_key]:
        target = frequencies[attribute_key][option]

        if len(target.keys()) < max_words:
            continue

        print('{}-{}'.format(attribute_key, option))
        print('target.keys() :', len(target.keys()))

        # top_phrase = target.items()
        # top_phrase = sorted(top_phrase, key=lambda x: -x[1])
        # write_attribute_frequency('{}-{}'.format(attribute_key, option), top_phrase)

        # wordcloud = WordCloud(
        #     width=1200,
        #     height=1200,
        #     font_path='/Library/Fonts/NotoSans-Black.ttf',
        #     background_color='white',
        #     max_font_size=140,
        #     max_words=max_words,
        # ).generate_from_frequencies(target)
        #
        # plt.figure(figsize=(25, 25))
        # plt.imshow(wordcloud)
        # plt.axis('off')
        # plt.savefig('./plt/{}-{}'.format(attribute_key, option))


def write_attribute_frequency(key, frequencies):
    with open('./frequency/{}.txt'.format(key), 'w+') as f:
        count = len(frequencies)
        for item in frequencies[:10]:
            f.write('{} ({}, {:.2f}%)\n'.format(item[0], item[1], (item[1] / count) * 100))


if __name__ == '__main__':
    connect(**config.Config.MONGODB_SETTINGS)

    draw_word_cloud()
