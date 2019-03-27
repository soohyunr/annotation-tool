from scipy.cluster.hierarchy import dendrogram, linkage, to_tree
from matplotlib import pyplot as plt

# X = [[i] for i in [2, 8, 0, 4, 1, 9, 9, 0]]
#
# Z = linkage(X, 'ward')
# fig = plt.figure(figsize=(25, 10))
#
# rootnode, nodelist = to_tree(Z, rd=True)
#
# dn = dendrogram(Z)
# plt.savefig('./data/dendrogram/practice.png', dpi=200)

import numpy as np
from scipy.cluster.hierarchy import dendrogram, linkage
from matplotlib import pyplot as plt

# generate two clusters: a with 10 points, b with 5:
np.random.seed(1)
a = np.random.multivariate_normal([10, 0], [[3, 1], [1, 4]], size=[10,])
b = np.random.multivariate_normal([0, 20], [[3, 1], [1, 4]], size=[5,])
X = np.concatenate((a, b),)
Z = linkage(X, 'ward')
# make distances between pairs of children uniform
# (re-scales the horizontal (distance) axis when plotting)
Z[:,2] = np.arange(Z.shape[0])+1

def plot_dendrogram(linkage_matrix, **kwargs):
    ddata = dendrogram(linkage_matrix, **kwargs)
    idx = 0
    for i, d, c in zip(ddata['icoord'], ddata['dcoord'],
                       ddata['color_list']):
        x = 0.5 * sum(i[1:3])
        y = d[1]
        plt.plot(y, x, 'o', c=c)
        plt.annotate("hello %.3g" % idx, (y, x), xytext=(23, 5),
                             textcoords='offset points',
                             va='top', ha='center')
        idx += 1

    plt.savefig('./data/dendrogram/practice.png', dpi=200)

plot_dendrogram(Z, labels=np.arange(X.shape[0]),
                truncate_mode='level', show_leaf_counts=False,
               orientation='left')

