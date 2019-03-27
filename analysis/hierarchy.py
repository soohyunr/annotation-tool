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


def clustering(reasons, w2v, file_key):
    print('[clustering] {}'.format(file_key))
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

    # linkage_matrix = hierarchy.ward(dist)  # define the linkage_matrix using ward clustering pre-computed distances
    linkage = hierarchy.linkage(dist, 'ward')

    rootnode, nodelist = hierarchy.to_tree(linkage, rd=True)
    assignments = hierarchy.fcluster(linkage, 4, 'distance')

    from matplotlib.pyplot import cm
    cmap = cm.rainbow(np.linspace(0, 1, 5))
    hierarchy.set_link_color_palette([mpl.colors.rgb2hex(rgb[:3]) for rgb in cmap])

    from scipy.cluster.hierarchy import fcluster
    fig, ax = plt.subplots(figsize=(20, len(reasons) * 0.3))
    ddata = hierarchy.dendrogram(linkage, orientation="right", labels=reasons)

    plt.tick_params(
        axis='x',
        which='both',
        bottom='off',
        top='off',
        labelbottom='off')
    plt.tight_layout()

    for i, d in zip(ddata['icoord'], ddata['dcoord']):
        x = 0.5 * sum(i[1:3])
        y = d[1]
        plt.plot(x, y, 'ro')
        plt.annotate("%.3g" % y,
                     (x, y),
                     xytext=(0, -8),
                     textcoords='offset points',
                     va='top', ha='center')

    plt.savefig('./data/dendrogram/{}.png'.format(file_key), dpi=200)
    plt.close()


if __name__ == '__main__':
    attribute_keys = ['Acceptance']
    from analysis.data_util import load_glove, Annotation

    anno = Annotation()
    reasons = anno.get_reasons(anno.acceptance, anno.strong_accept)

    w2v = load_glove()
    clustering(reasons[:100], w2v, '{} {}'.format(anno.acceptance, anno.strong_accept))
