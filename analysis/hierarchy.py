import matplotlib as mpl
from matplotlib import pyplot as plt
import numpy as np

from scipy.cluster.hierarchy import to_tree, dendrogram, linkage

from analysis.entailment import Predictor

predictor = Predictor()


def plot_dendrogram(linkage_matrix, **kwargs):
    ddata = dendrogram(linkage_matrix, **kwargs)

    leaves = ddata['leaves']
    rootnode, nodelist = to_tree(linkage_matrix, rd=True)

    leave2text = dict()
    for i in range(len(leaves)):
        leave2text[leaves[i]] = ddata['ivl'][i]

    children = dict()
    main_text = dict()

    def dfs(node):
        if node.left is None:
            children[node.id] = [node.id]
            main_text[node.id] = leave2text[node.id]
            return
        dfs(node.left)
        dfs(node.right)
        children[node.id] = children[node.left.id] + children[node.right.id]

        left_text = main_text[node.left.id]
        right_text = main_text[node.right.id]

        if predictor.predict(left_text, right_text)[0] >= predictor.predict(right_text, left_text)[0]:
            main_text[node.id] = right_text
        else:
            main_text[node.id] = left_text

    dfs(rootnode)

    idx = 0
    for i, d, c, txt in zip(ddata['icoord'], ddata['dcoord'], ddata['color_list'], ddata['ivl']):
        x = 0.5 * sum(i[1:3])
        y = d[1]

        node_id = idx + len(leaves)

        plt.plot(y, x, 'o', c=c)
        text = plt.annotate(main_text[node_id],
                            (y, x),
                            xytext=(23, 15),
                            textcoords='offset points',
                            va='top',
                            ha='center')
        text.set_fontsize(8)
        idx += 1


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
    linkage_matrix = hierarchy.linkage(dist, 'ward')

    # rootnode, nodelist = hierarchy.to_tree(linkage, rd=True)
    # assignments = hierarchy.fcluster(linkage, 4, 'distance')

    from matplotlib.pyplot import cm
    cmap = cm.rainbow(np.linspace(0, 1, 5))
    hierarchy.set_link_color_palette([mpl.colors.rgb2hex(rgb[:3]) for rgb in cmap])

    fig, ax = plt.subplots(figsize=(20, len(reasons) * 0.7))
    plot_dendrogram(linkage_matrix,
                    labels=reasons,
                    # truncate_mode='level',
                    show_leaf_counts=False,
                    color_threshold=2,
                    orientation='left')

    plt.tick_params(
        axis='x',
        which='both',
        bottom='off',
        top='off',
        labelbottom='off')

    plt.tight_layout()
    # plt.title(file_key)

    plt.savefig('./data/dendrogram/{}.png'.format(file_key), dpi=200)
    plt.close()


if __name__ == '__main__':
    from analysis.data_util import load_glove, Annotation

    anno = Annotation()
    reasons = anno.get_reasons(anno.acceptance, anno.strong_accept)

    w2v = load_glove()

    selected = list()
    for reason in reasons:
        if 20 <= len(reason) <= 50:
            selected.append(reason)

    clustering(selected[:50], w2v, '{} {}'.format(anno.acceptance, anno.strong_accept))
