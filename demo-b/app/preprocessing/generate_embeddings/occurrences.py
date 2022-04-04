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


def get_relevance(occurrences, shared_words):
    """
    returns a score for each line representing how many words from shared_words it contains
    occurrences: dict(str: set(int)) - dictionary of which lines contain which words
    shared_words: set(str) - set of words to compare to
    """
    relevance = dict()
    for word in occurrences:
        if word in shared_words:
            for line in occurrences[word]:
                if line in relevance:
                    relevance[line] += 1
                else:
                    relevance[line] = 1
    return relevance


def get_lines(occurrences, word):
    """
    returns a list of lines that contain the word
    occurrences: dict(str: set(int)) - dictionary of which lines contain which words
    word: str - word to search for
    """
    if word in occurrences:
        return occurrences[word]
    else:
        return set()


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


def get_best_lines(pt_path, occurrences, alignment, target):
    """
    get the most "robust" example sentence showcasing semantic dissimilarity
    pt_path: path object pointing to the plaintext
    lines: list(list(str)) - list of sentences
    alignment: alignment object with vectors for the common words
    target: word to get dissimilar examples for
    returns: list(list(str)) - list of sentences
    """
    # read in the lines
    with pt_path.open() as f:
        lines = f.readlines()
    # get the indices of the lines that contain the target word
    indices = get_lines(occurrences, target)
    # get the lines
    lines = sentences_from_indices(lines, indices)
    # embed the lines using wv1
    lv1 = embed_lines(lines, alignment.wv1)
    # embed the lines using wv2
    lv2 = embed_lines(lines, alignment.wv2)
    # get the relevance of the lines
    relevance = get_relevance(occurrences, set([target]))
