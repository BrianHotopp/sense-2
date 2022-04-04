import numpy as np
from multiprocessing import Pool
import nltk


def tok_w_i(il):
    """
    il: tuple, il[0] is the line number, il[1] is the line
    returns tuple of line number, tokenized line
    """
    return (il[0], nltk.word_tokenize(il[1]))


def get_occurrences(file_in, limit=10000, workers=48):
    """
    file_in: path object pointing to the plaintext
    limit: int - maximum number of lines to record as containing the word of interest
    returns: dict(str: set(int)) - dictionary of which lines contain which words
    """
    # read in the lines
    occurrences = dict()
    with file_in.open() as f:
        with Pool(workers) as p:
            for i, line in p.map(tok_w_i, enumerate(f)):
                for tok in line:
                    if tok not in occurrences:
                        occurrences[tok] = set()
                    if len(occurrences[tok]) < limit:
                        occurrences[tok].add(i)
    return occurrences


def _embed_line(line, wv, c, vectors):
    """
    embeds a line in the corpus by adding the vector representations of its words
    line: list(str) - list of words
    wv1: WordVectors - word vectors to use
    returns: none, mutates input array vectors
    """
    for word in nltk.word_tokenize(line):
        if word in wv:
            vectors[c] += wv[word]


def embed_lines(file_in, line_ind, wv):
    """
    embeds lines in the corpus by adding the vector representations of their words
    file_in: Path obj file in
    line_ind: set of indices of the lines in file_in we should embed
    wv1: WordVectors - word vectors to use
    returns:
    indices: list(int) - list of indices of lines in the original file
    vectors: list of embedded sentences
    the i'th line in vectors is the indices[i]th line in the original file
    """
    # pre-allocate np array
    indices = np.zeros(len(line_ind))
    vectors = np.zeros((len(line_ind), wv.get_vector_dimension()), dtype=float)
    c = 0
    with file_in.open() as f:
        for i, line in enumerate(f):
            if i in line_ind:
                _embed_line(line, wv, c, vectors)
                indices[c] = i
                c += 1
    return indices, vectors


def line_from_file(file, line_index):
    """
    returns the line at line_index from file
    file: path object pointing to the plaintext
    line_index: int - line number to return
    returns: str - line
    """
    with file.open() as f:
        for i, line in enumerate(f):
            if i == line_index:
                return line

