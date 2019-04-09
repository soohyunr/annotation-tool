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

    node_map = dict()
    for node in nodelist:
        node_map[node.id] = node

    def flatten(l):
        return [item for sublist in l for item in sublist]

    Y = flatten(ddata['icoord'])
    X = flatten(ddata['dcoord'])
    leave_coords = [(x, y) for x, y in zip(X, Y) if x == 0]

    sorted_coords = sorted(leave_coords, key=lambda item: item[1])
    leave_coords = [sorted_coords[0]]
    for coord in sorted_coords:
        if leave_coords[-1][1] != coord[1]:
            leave_coords.append(coord)

    for i in range(len(leaves)):
        node = node_map[leaves[i]]
        node.text = ddata['ivl'][i]
        node.coord = leave_coords[i]
        node_map[node.id] = node

    children_to_parent_coords = dict()
    for i, d in zip(ddata['icoord'], ddata['dcoord']):
        x = d[1]
        y = (i[1] + i[2]) * 0.5
        parent_coord = (x, y)
        left_coord = (d[0], i[0])
        right_coord = (d[-1], i[-1])

        children_to_parent_coords[left_coord] = parent_coord
        children_to_parent_coords[right_coord] = parent_coord

    def dfs(node, depth=0):
        node_map[node.id].depth = depth
        if node.left is None:
            return

        dfs(node.left, depth + 1)
        dfs(node.right, depth + 1)
        node_map[node.id].coord = children_to_parent_coords[node_map[node.left.id].coord]

        left_text = node_map[node.left.id].text
        right_text = node_map[node.right.id].text

        if predictor.predict(left_text, right_text)[0] >= predictor.predict(right_text, left_text)[0]:
            node_map[node.id].text = right_text
        else:
            node_map[node.id].text = left_text

    dfs(rootnode)

    def coord2node(coord):
        for node_id in node_map:
            node = node_map[node_id]
            if node.coord == coord:
                return node
        return None

    for node_id in node_map:
        node = node_map[node_id]
        if node.depth == 4:
            print(node.text)

    idx = 0
    for i, d, c in zip(ddata['icoord'], ddata['dcoord'], ddata['color_list']):
        x = d[1]
        y = (i[1] + i[2]) * 0.5

        node = coord2node((x, y))
        if node is not None:
            plt.plot(y, x, 'o', c=c)
            text = plt.annotate('{}'.format(node.text),
                                (x, y),
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

    fig, ax = plt.subplots(figsize=(20, len(reasons) * 0.5))
    plot_dendrogram(linkage_matrix,
                    labels=reasons,
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

    anno = Annotation(redundant=False)
    reasons = anno.get_reasons(anno.acceptance, anno.strong_accept)

    w2v = load_glove()

    selected = list()
    for reason in reasons:
        if 20 <= len(reason) <= 50:
            selected.append(reason)

    clustering(selected, w2v, '{} {}'.format(anno.acceptance, anno.strong_accept))
