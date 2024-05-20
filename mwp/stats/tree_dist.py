import zss
import numpy as np
from scipy.cluster.hierarchy import dendrogram, linkage, fcluster

def get_children(T):
    children = T[1]

    if not isinstance(children, list):
        return []
    
    return children

def get_value(T):
    return T[0]

def val_distance(v1, v2):
    return int(v1 != v2)

def get_distance(T1, T2):
    return zss.simple_distance(
        T1,
        T2,
        get_children,
        get_value,
        val_distance
    )

def cluster(trees, dist_func, thresh=16):
    n = len(trees)
    dissimilarity_matrix = np.zeros((n, n))

    for i in range(n):
        for j in range(i + 1, n):
            distance = dist_func(trees[i], trees[j])
            dissimilarity_matrix[i, j] = distance
            dissimilarity_matrix[j, i] = distance

    condensed_dissimilarity_matrix = dissimilarity_matrix[np.triu_indices(n, 1)]

    Z = linkage(condensed_dissimilarity_matrix, method='average')

    threshold = 5
    return fcluster(Z, t=thresh, criterion='distance')
