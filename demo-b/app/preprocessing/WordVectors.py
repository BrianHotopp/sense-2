import numpy as np
from sklearn import preprocessing
import os
from .BiMap import BiMap
from pathlib import Path
import time


class WordVectors:
    """
    Implements a WordVector class that performs mapping of word tokens to vectors
    """

    def __init__(self, words=None, vectors=None, centered=True, normalized=False):
        """
        words: BiMap of word, id pairs
        vectors: dimension len(words)*n numpy array containing floats
        ith row corresponds to the embedding for the ith word in words
        centered: flag controlling whether we will center the vectors on initialization
        normalized: flag controlling whether we will normalize the vectors on initializtion
        """
        # input sanitization
        # we should never feed a length 0 wordvector in
        assert len(words) != 0
        # BiMap containing word->id pairs
        b, a = zip(*enumerate(words))
        self.words = BiMap(a, b)
        # vectors for each word
        self.vectors = np.array(vectors, dtype=float)
        # int containing the length of each individual vector
        self.vector_dimension = len(vectors[0])
        self.length = len(self.words)
        # optional intialization transforms
        self.centered = False
        self.normalized = False
        if centered:
            self.center()
            self.centered = True
        if normalized:
            self.normalize()
            self.normalized = True

    def __len__(self):
        """returns the number of words contained"""
        return len(self.words)

    def __getitem__(self, key):
        """
        Overload [], given word w returns its vector
        """
        return self.get_vector(key)

    def __contains__(self, word):
        """
        Overload in keyword
        true if word is in wordvectors
        """
        return word in self.words

    def center(self):
        """
        centers word vectors so they have 0 mean
        """
        self.vectors = self.vectors - self.vectors.mean(axis=0, keepdims=True)

    def normalize(self):
        """
        normalizes all word vectors (l2 norm)
        mutates the current wordvectors object O(len(self)*self.get_vector_dimension())
        """
        self.vectors = preprocessing.normalize(self.vectors, norm="l2")

    def get_words(self):
        """
        returns the list of words contained in this wordvectors object
        """
        return list(self.words.keys())

    def vectors_for_words(self, input_words):
        """
        input_words: list[str]
        returns: a len(input_words)*self.vector_dimension numpy array
        where the ith row corresponds to the vector
        for the ith word in input_words
        """
        indices = []
        for word in input_words:
            indices.append(self.words.get_value(word))
        # todo test my use of np take
        return np.take(self.vectors, indices, axis=0)

    def get_vector(self, input_word):
        """
        get the 1*self.vector_dimension vector associated with input_word
        """
        return self.vectors[self.words.get_value(input_word)]

    def get_count(self, word):
        """
        get the number of times word occures in this WordVectors object
        """
        return self.freq[self.word_id[word]]

    def get_word(self, word_id):
        """
        get the word associated with a particular word id
        """
        return self.words.get_key(word_id)

    def get_id(self, input_word):
        """
        get the id associated with an input word
        """
        return self.words.get_value(input_word)

    def get_vector_dimension(self):
        """
        returns the length of the vectors contained
        """
        return self.vector_dimension

    def to_file(self, path):
        """
        write a WordVectors object to a text file
        path: pathlib path object to path we want to write to
        will create intermediate directories in the input path if they do not exist
        will overwrite if there already exists file at path
        """
        # create the path if it doesn't exist
        path.parent.mkdir(parents=True, exist_ok=True)
        # write the file with the contents of the WordVectors object
        with path.open("w") as fout:
            lines = []
            for word, vec in zip(self.get_words(), self.vectors):
                v_string = " ".join(map(str, vec))
                line = f"{word} {v_string}"
                lines.append(line)
            fout.write("\n".join(lines))

    @staticmethod
    def from_file(path):
        """
        read a WordVectors object from a text file
        path: pathlib path object to path
        returns: WordVectors object, or throws an OSError if the file is not found
        """
        # open the file if it exists
        with path.open("r") as fin:

            def process_line(line):
                line_list = line.rstrip().split(" ")
                w = line_list[0]
                v = np.array(line_list[1:], dtype=float)
                return w, v

            # skip the first line containing dimensions
            fin.readline()
            data = map(process_line, fin.readlines())
            words, vectors = zip(*data)
            return WordVectors(words, vectors)

    @staticmethod
    def same_vector_dimension(*args):
        """
        *args: some number of WordVector objects
        returns: True if all passed in WordVector objects have the same vector_size
        """
        if len(args) == 0:
            return False
        for arg in args:
            if args[0].get_vector_dimension() != arg.get_vector_dimension():
                return False
        return True

    @staticmethod
    def union(*args, f=lambda x: sum(x) / len(x)):
        """
        Performs union of two or more word vectors
        returns a new WordVectors object or None if no WordVectors objects were passed in
        *args: some number of WordVectors objects to union
        f: function of n numpy vectors of equal dimension
        (defaults to average)
        this function is used to combine the vectors of words in the union
        """
        if len(args) == 0:
            return None
        # error check; every WordVectors object should have the same vector_dim
        assert WordVectors.same_vector_dimension(*args)
        # compute the union of the words
        union_words = set.union(*(set(wv.get_words()) for wv in args))
        # allocate space for each word in the union
        vectors = np.zeros(
            (len(union_words), args[0].get_vector_dimension()), dtype=float
        )
        # union the vectors for each word
        for i, word in enumerate(union_words):
            vecs = np.array([wv[word] for wv in args if word in wv])
            vectors[i] = f(vecs)  # Combine vectors
        return WordVectors(union_words, vectors)

    @staticmethod
    def intersect(*args):
        """
        args: list of wordvectors objects
        returns: a list of WordVectors objects
        the ith WordVector object in the output list is the a copy of the ith WordVectors
        object in the input list with the words not in the the overall intersection removed
        the order of the words in each output vector is the same
        """
        # time how long it takes
        start = time.time()
        # check we have at least one argument
        if len(args) == 0:
            return None
        # error check; every WordVectors object should have the same vector_dim
        for arg in args:
            if args[0].get_vector_dimension() != arg.get_vector_dimension():
                raise ValueError("All arguments must have the same vector_dimension")

        common_words = set.intersection(*[set(wv.get_words()) for wv in args])
        # Get intersecting words following the order of first WordVector
        wv0_order = [w for w in args[0].get_words() if w in common_words]
        # Retrieve vectors from a and b for intersecting words
        wv_out = list()  # list of output WordVectors
        for wv in args:
            vectors = np.array([wv.get_vector(w) for w in wv0_order])
            wv_out.append(WordVectors(wv0_order, vectors))
        end = time.time()
        return wv_out
