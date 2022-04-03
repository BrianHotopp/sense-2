"""
Performs mapping of words between two input word embeddings A and B
"""
from sklearn.neighbors import NearestNeighbors


def perform_mapping(wva, wvb, k=5, metric="cosine"):
    """
    Given aligned wv_a and wv_b, performs mapping (translation) of words in a to those in b
    Returns (distances, indices) as n-sized lists of distances and the indices of the top neighbors
    """
    nbrs = NearestNeighbors(n_neighbors=k, n_jobs=12, metric=metric).fit(wvb.vectors)
    distances, indices = nbrs.kneighbors(wva.vectors)

    return distances, indices
