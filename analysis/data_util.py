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
    print('[load_glove]')
    from tqdm import tqdm
    with open("/Users/seungwon/Desktop/data/glove/glove.6B.300d.txt", "rb") as lines:
        print('Load glove')
        w2v = dict()
        for line in tqdm(lines):
            word = line.split()[0].decode('utf-8')
            vector = list(map(float, line.split()[1:]))
            w2v[word] = vector
        return w2v
