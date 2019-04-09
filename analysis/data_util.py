from tqdm import tqdm
import random


def clean_text(text):
    text = text.lower()
    text = text.replace("'d", ' had')
    text = text.replace("n't", ' not')

    for punct in "/-'":
        text = text.replace(punct, ' ')
    for punct in '&':
        text = text.replace(punct, ' {} '.format(punct))
    for punct in '?!.,"#$%\'()*+-/:;<=>@[\\]^_`{|}~' + '“”’':
        text = text.replace(punct, '')
    return text


def tokenize_and_lemmatize(text):
    from nltk import word_tokenize
    from nltk.stem import WordNetLemmatizer
    from nltk.corpus import stopwords
    lemmatizer = WordNetLemmatizer()

    stop_words = set(stopwords.words('english'))
    stems = []
    text = text.lower()
    words = [word for word in word_tokenize(text) if word.isalpha()]
    words = [word for word in words if word not in stop_words]
    for word in words: stems.append(lemmatizer.lemmatize(word, pos='v'))
    return stems


def load_glove():
    import os, pickle
    print('[load_glove]')
    pkl_path = './data/pkl/glove.pkl'
    if os.path.exists(pkl_path):
        print('loaded from glove.pkl')
        w2v = pickle.load(open(pkl_path, "rb"))
        return w2v
    else:
        from tqdm import tqdm
        with open("./data/glove/glove.6B.300d.txt", "rb") as lines:
            w2v = dict()
            print('generate glove.pkl')
            for line in tqdm(lines):
                word = line.split()[0].decode('utf-8')
                vector = list(map(float, line.split()[1:]))
                w2v[word] = vector
            pickle.dump(w2v, open(pkl_path, "wb"))
            return w2v


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


class Annotation:
    knowledge_awareness = 'Knowledge_Awareness'
    verifiability = 'Verifiability'
    disputability = 'Disputability'
    acceptance = 'Acceptance'
    _map = dict()
    ATTR_KEYS = [knowledge_awareness, verifiability, disputability, acceptance]

    did_not_know = 'I_did_not_know_the_information.'
    already_knew = 'I_already_knew_the_information_before_I_read_this_document.'
    but_came_to_know = 'I_did_not_know_the_information_before,_but_came_to_know_it_by_reading_the_previous_sentences.'

    using_my_knowledge = 'I_can_verify_it_using_my_knowledge.'
    short_time_googling = 'I_can_verify_it_by_short-time_googling.'
    long_time_googling = 'I_can_verify_it_by_long-time_googling.'
    off_line = 'I_might_find_an_off-line_way_to_verify_it,_but_it_will_be_very_hard.'
    now_way_to_verify = 'There_is_no_way_to_verify_it.'
    none_of_the_above = 'None_of_the_above'

    highly_disputable = 'Highly_Disputable'
    weakly_disputable = 'Weakly_Disputable'
    disputable = 'Disputable'
    not_disputable = 'Not_Disputable'

    strong_accept = 'Strong_Accept'
    accept = 'Accept'
    weak_accept = 'Weak_Accept'
    hard_to_judge = 'Hard_to_judge'
    weak_reject = 'Weak_Reject'
    reject = 'Reject'
    strong_reject = 'Strong_Reject'

    def __init__(self, pkl_path='./data/pkl/annotations_clustering.pkl', redundant=True):
        import os, pickle, logging
        from models import Annotation
        from mongoengine import connect
        import config

        connect(**config.Config.MONGODB_SETTINGS)
        self.redundant = redundant

        dumps = []
        if os.path.exists(pkl_path):
            dumps = pickle.load(open(pkl_path, "rb"))
        else:
            print('generate pkl' + pkl_path)
            annotations = Annotation.objects(type='sentence')
            for annotation in tqdm(annotations):
                try:
                    row = annotation.dump()
                    user = annotation.user
                    row['user_name'] = '{} {}'.format(user.first_name, user.last_name)
                    dumps.append(row)
                except Exception as e:
                    logging.exception(e)
            pickle.dump(dumps, open(pkl_path, "wb"))

        random.shuffle(dumps)
        self.annotations = dumps
        self.build_map()

    def build_map(self):
        from collections import defaultdict
        self._map = defaultdict(lambda: defaultdict(lambda: []))

        reason_set = set()
        for annotation in tqdm(self.annotations):
            basket = annotation['basket']

            for attr_k in basket:
                option = basket[attr_k]
                if not ('reason' in option):
                    continue

                attr_v = option['value']
                reason = option['reason']

                if not reason:
                    continue

                if not self.redundant:
                    reason_key = reason.strip()
                    reason_key = clean_text(reason_key)
                    reason_key = ' '.join(tokenize_and_lemmatize(reason_key))
                    if reason_key in reason_set:
                        continue
                    reason_set.add(reason_key)

                self._map[attr_k][attr_v].append(option)
        return self._map

    def get_reasons(self, attr_k, attr_v=''):
        reasons = list()
        if not attr_v:
            for attr_v in self._map[attr_k]:
                options = self._map[attr_k][attr_v]
                reasons.extend([option['reason'] for option in options])
        else:
            reasons.extend([option['reason'] for option in self._map[attr_k][attr_v]])

        random.shuffle(reasons)
        return reasons
