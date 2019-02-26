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

definitions = {
    'Knowledge_Awareness': {
        'I_did_not_know_the_information.': 'I did not know the information.',
        'I_already_knew_the_information_before_I_read_this_document.': 'I already knew the information before I read this document.',
        'I_did_not_know_the_information_before,_but_came_to_know_it_by_reading_the_previous_sentences.': 'I did not know the information before I read this document, but came to know it by reading the previous sentences in this document.',
    },
    'Verifiability': {
        'I_can_verify_it_using_my_knowledge.': 'I can verify it using my knowledge. It is a common sense. I don’t need to google it to verify.',
        'I_can_verify_it_by_short-time_googling.': 'I can verify it by short-time googling.',
        'I_can_verify_it_by_long-time_googling.': 'I can verify it by long-time googling. I could verify it using deduction if I google it for some time for deeper understanding.',
        'I_might_find_an_off-line_way_to_verify_it,_but_it_will_be_very_hard.': 'I might find an off-line way to verify it, but it will be very hard. It needs specific witness or testimony to verify, and there may not be any evidence in written form.',
        'There_is_no_way_to_verify_it.': 'There is no way to verify it.',
        'None_of_the_above': 'None of the above',
    },
    'Disputability': {
        'Highly_Disputable': 'Whether or not it is reasonable to accept the information given by the sentence as true, it is Highly Disputable.',
        'Disputable': 'Whether or not it is reasonable to accept the information given by the sentence as true, it is Disputable.',
        'Weakly_Disputable': 'Whether or not it is reasonable to accept the information given by the sentence as true, it is Weakly Disputable.',
        'Not_Disputable': 'Whether or not it is reasonable to accept the information given by the sentence as true, it is Not Disputable.',
    },
    'Acceptance': {
        'Strong_Accept': 'Strong Accept I accept the information given by the sentence to be true. I have sound and cogent arguments to justify my acceptance. I am sure that I can effectively convince others that my judgement is reasonable.',
        'Accept': 'Accept I accept the information given by the sentence to be true. I have some arguments to justify my acceptance. But I am not sure whether I can effectively convince others that my judgement is reasonable.',
        'Weak_Accept': 'Weak Accept I accept the information given by the sentence to be true. I don’t have arguments justifying my acceptance. Still, I will accept it rather than reject it.',
        'Hard_to_judge': 'Hard to judge It is hard to judge whether I should accept or reject the information given by the sentence to be true.',
        'Weak_Reject': 'Weak Reject I reject the information given by the sentence to be true. I don’t have arguments for the rejection. Still, I will reject it rather than accept it.',
        'Reject': 'Reject I reject the information given by the sentence to be true, and I have arguments for the rejection. But I am not sure whether I can effectively convince others that my judgement is reasonable.',
        'Strong_Reject': 'Strong Reject I reject the information given by the sentence to be true. I have sound and cogent arguments for the rejection. I am sure that I can effectively convince others that my judgement is reasonable.',
    },
}


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
    words = [word for word in words if word not in stop_words or word == 'not']
    for word in words: stems.append(lemmatizer.lemmatize(word, pos='v'))
    return stems


def get_ngrams(tokens, n):
    ngrams_ = ngrams(tokens, n)
    return [' '.join(grams) for grams in ngrams_]


def get_attribute_words(attribute_key, attribute_value):
    tokens = word_tokenize(attribute_key.replace('_', ' '))
    tokens += word_tokenize(attribute_value.replace('_', ' '))
    result = []
    for token in tokens:
        token = lemmatizer.lemmatize(token, pos='v')
        result.append(token.lower())
    return result


def draw_word_cloud():
    attribute_reason = defaultdict(lambda: defaultdict(lambda: []))

    annotations = Annotation.objects(type='sentence')
    dumps = []
    bin_path = './bin/annotations_frequency.bin'
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

    reason_set = set()
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
            tokens = tokenize_and_lemmatize(reason)

            reason_key = '{}-{}'.format(option['user'], ''.join(tokens))
            if reason_key in reason_set:
                continue
            reason_set.add(reason_key)

            attribute_reason[attribute_key][value] += get_ngrams(tokens, 3)

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
        # plt.savefig('./wordcloud/{}-{}'.format(attribute_key, option))


def write_attribute_frequency(key, frequencies):
    with open('./frequency/{}.txt'.format(key), 'w+') as f:
        count = len(frequencies)
        for item in frequencies[:10]:
            f.write('{} ({}, {:.2f}%)\n'.format(item[0], item[1], (item[1] / count) * 100))


if __name__ == '__main__':
    connect(**config.Config.MONGODB_SETTINGS)

    draw_word_cloud()
