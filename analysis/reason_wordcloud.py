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
    'Perceived_Author_Credibility': {
        'Strong_Credibility_for_the_upcoming_sentences': 'Strong Credibility for the upcoming sentences For the upcoming sentences, I anticipate to strongly accept them.',
        'Credibility_for_the_upcoming_sentences': 'Credibility for the upcoming sentences For the upcoming sentences, I anticipate to accept them.',
        'Weak_Credibility_for_the_upcoming_sentences': 'Weak Credibility for the upcoming sentences For the upcoming sentences, I anticipate to weakly accept them.',
        'Hard_to_Judge': 'Hard to Judge',
        'Weak_Suspicion_for_the_upcoming_sentencese':'Weak Suspicion for the upcoming sentences For the upcoming sentences, I anticipate to weakly reject them',
        'Suspicion_for_the_upcoming_sentences':'Suspicion for the upcoming sentences For the upcoming sentences, I anticipate to reject them.',
        'Strong_Suspicion_for_the_upcoming_sentences':'Strong Suspicion for the upcoming sentences For the upcoming sentences, I anticipate to strongly reject them.',
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

title_map = {
    'Knowledge_Awareness': {
        'I_did_not_know_the_information.': 'did not know',
        'I_already_knew_the_information_before_I_read_this_document.': 'already knew',
        'I_did_not_know_the_information_before,_but_came_to_know_it_by_reading_the_previous_sentences.': 'came to know',
    },
    'Verifiability': {
        'I_can_verify_it_using_my_knowledge.': 'using my knowledge',
        'I_can_verify_it_by_short-time_googling.': 'short-time googling',
        'I_can_verify_it_by_long-time_googling.': 'long-time googling',
        'I_might_find_an_off-line_way_to_verify_it,_but_it_will_be_very_hard.': 'off-line way',
        'There_is_no_way_to_verify_it.': 'no way to verify',
        'None_of_the_above': 'none of the above',
    },
    'Disputability': {
        'Highly_Disputable': 'highly disputable',
        'Disputable': 'disputable',
        'Weakly_Disputable': 'weakly disputable',
        'Not_Disputable': 'not disputable',
    },
    'Acceptance': {
        'Strong_Accept': 'strong accept',
        'Accept': 'accept',
        'Weak_Accept': 'weak accept',
        'Hard_to_judge': 'hard to judge',
        'Weak_Reject': 'weak reject',
        'Reject': 'reject',
        'Strong_Reject': 'strong reject',
    },
}

import spacy

nlp = spacy.load('en_core_web_sm')

def remove_name_entity(reason):
    doc = nlp(reason)
    result = reason
    for e in doc.ents:
        # result = result.replace(' {} '.format(e.text), ' ')
        result = result.replace(e.text, ' ')
    return result


def filtering_from_definition(reason_tokens, key, value):
    try:
        sent_filter = definitions[key][value]
    except KeyError:
        print('key :', key, ', value :', value)
        exit(0)

    sent_filter = clean_reason(sent_filter)
    sent_filter = tokenize_and_lemmatize(sent_filter)

    result = []
    for token in reason_tokens:
        if not (token in sent_filter):
            result.append(token)

    return result


def clean_reason(reason):
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
    # for word in words: stems.append(lemmatizer.lemmatize(word, pos='v'))
    for word in words: stems.append(word)
    return stems


def get_ngrams(tokens, n):
    ngrams_ = ngrams(tokens, n)
    return [' '.join(grams) for grams in ngrams_]


def draw_wordcloud():
    attribute_reason = defaultdict(lambda: defaultdict(lambda: []))


    dumps = []
    bin_path = './data/pkl/annotations_frequency.bin'
    if os.path.exists(bin_path):
        dumps = pickle.load(open(bin_path, "rb"))
    else:
        print('generate ' + bin_path)

        docs = Doc.objects.filter(type='v1')
        for doc in tqdm(docs):
            annotations = Annotation.objects(type='sentence', doc=doc)
            for annotation in annotations:
                try:
                    if not ('Acceptance' in annotation['basket']):
                        continue
                    dumps.append(annotation.dump())
                except Exception as e:
                    logging.exception(e)
        pickle.dump(dumps, open(bin_path, "wb"))
    random.shuffle(dumps)

    def ddict2dict(d):
        for k, v in d.items():
            if isinstance(v, dict):
                d[k] = ddict2dict(v)
        return dict(d)

    bin_path = './data/pkl/annotations_frequency_step2.bin'
    frequencies = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: 0)))
    if False and os.path.exists(bin_path):
        frequencies = pickle.load(open(bin_path, "rb"))
    else:
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

                reason = clean_reason(reason)
                # reason = remove_name_entity(reason)
                tokens = tokenize_and_lemmatize(reason)
                tokens = filtering_from_definition(tokens, attribute_key, value)

                str_reason = ' '.join(tokens)
                if 'ground author' in str_reason:
                    print(reason)

                reason_key = '{}-{}'.format(annotation['user'], ''.join(tokens))
                if reason_key in reason_set:
                    continue
                reason_set.add(reason_key)

                attribute_reason[attribute_key][value] += get_ngrams(tokens, 3)

        for attribute_key in attribute_reason:
            for option in attribute_reason[attribute_key]:
                for reason in attribute_reason[attribute_key][option]:
                    frequencies[attribute_key][option][reason] += 1

        pickle.dump(ddict2dict(frequencies), open(bin_path, "wb"))

    import matplotlib
    import matplotlib.pyplot as plt
    from wordcloud import WordCloud

    # attribute_key = 'Knowledge_Awareness'
    # attribute_key = 'Verifiability'
    # attribute_key = 'Disputability'
    # attribute_key = 'Perceived_Author_Credibility'
    attribute_key = 'Acceptance'
    max_words = 100

    # ['Knowledge_Awareness', 'Verifiability', 'Disputability', 'Acceptance']
    keys = ['Acceptance']
    for attribute_key in keys:
        for option in definitions[attribute_key]:
            target = frequencies[attribute_key][option]

            if len(target.keys()) < max_words:
                continue

            print('{}-{}'.format(attribute_key, option))
            print('target.keys() :', len(target.keys()))

            top_phrase = target.items()
            top_phrase = sorted(top_phrase, key=lambda x: -x[1])
            write_attribute_frequency('{}-{}'.format(attribute_key, option), top_phrase)

            wordcloud = WordCloud(
                width=1200,
                height=1200,
                font_path='/Library/Fonts/NotoSans-Black.ttf',
                background_color='white',
                max_font_size=170,
                max_words=max_words,
            ).generate_from_frequencies(target)

            import matplotlib.font_manager as fm
            my_font = fm.FontProperties(fname='/Library/Fonts/Times New Roman Bold.ttf')

            plt.figure(figsize=(25, 25))
            plt.imshow(wordcloud)
            # plt.title(title_map[attribute_key][option], fontsize=70, y=-0.05, fontproperties=my_font)
            # plt.tight_layout(pad=0)
            plt.axis('off')
            plt.savefig('./data/wordcloud_v2/{}-{}'.format(attribute_key, option), bbox_inches='tight')
            plt.close()


def write_attribute_frequency(key, frequencies):
    with open('./data/frequency_v2/{}.txt'.format(key), 'w+') as f:
        count = len(frequencies)
        for item in frequencies[:20]:
            f.write('{} ({}, {:.2f}%)\n'.format(item[0], item[1], (item[1] / count) * 100))


if __name__ == '__main__':
    connect(**config.Config.MONGODB_SETTINGS)

    draw_wordcloud()
