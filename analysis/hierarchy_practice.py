from scipy.cluster.hierarchy import dendrogram, linkage, to_tree
from matplotlib import pyplot as plt

X = [[i] for i in [2, 8, 0, 4, 1, 9, 9, 0]]

Z = linkage(X, 'ward')
fig = plt.figure(figsize=(25, 10))

rootnode, nodelist = to_tree(Z, rd=True)

dn = dendrogram(Z)
plt.savefig('./data/dendrogram/practice.png', dpi=200)
