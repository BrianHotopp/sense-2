from tkinter import W
from scipy.linalg import orthogonal_procrustes
import numpy as np
from app.preprocessing.WordVectors import WordVectors


class GlobalAlignConfig:
    def __init__(
        self,
        name="unnamed",
        anchor_indices=None,
        anchor_top=None,
        anchor_bot=None,
        anchor_random=None,
        anchor_words=None,
        exclude=[],
    ):
        """
        initializes a global alignment config
        """
        self._name = name
        self._anchor_indices = anchor_indices
        self._anchor_top = anchor_top
        self._anchor_bot = anchor_bot
        self._anchor_random = anchor_random
        self._anchor_words = anchor_words
        self._exclude = set(exclude)

    def add_excludes(self, words_to_exclude: set[str]):
        """
        adds words to the config's list of words to exclude when performing alignment
        words_to_exclude: set of words to exclude
        returns: None, mutates the current config object
        """
        self._excludes = self._excludes.union(words_to_exclude)

    def add_anchors(self, more_anchor_words: set[str]):
        """
        adds words to perform orthogonal procrustes alignment on
        anchor_words: set of words to add to the set of words to align on
        returns: None, modifies the current object
        """
        self._anchor_words.update(more_anchor_words)

    # Word alignment module
    def align(self, wv1, wv2):
        """
        Implement OP alignment for a given set of landmarks.
        If no landmark is given, performs global alignment.
        Arguments:
            wv1 - WordVectors object to align to wv2
            wv2 - Target WordVectors. Will align wv1 to it
            anchor_indices - (optional) uses word indices as landmarks
            anchor_words - (optional) uses words as landmarks
            exclude - set of words to exclude from alignment
        """
        # they should have the same number of words
        assert len(wv1) == len(wv2)
        # might be no efficient way to do this
        words = wv1.get_words()
        if self._anchor_top is not None:
            v1 = [
                wv1.vectors[i]
                for i in range(self._anchor_top)
                if wv1.get_word(i) not in self._exclude
            ]
            v2 = [
                wv2.vectors[i]
                for i in range(self._anchor_top)
                if wv2.get_word(i) not in self._exclude
            ]
        elif self._anchor_bot is not None:
            # not sure this works quite as expected, grabs the first word and the last anchor_bot-1
            v1 = [
                wv1.vectors[-i]
                for i in range(self._anchor_bot)
                if wv1.get_word(i) not in self._exclude
            ]
            v2 = [
                wv2.vectors[-i]
                for i in range(self._anchor_bot)
                if wv2.get_word(i) not in self._exclude
            ]
        elif self._anchor_random is not None:
            anchors = np.random.choice(range(len(wv1.vectors)), self._anchor_random)
            v1 = [
                wv1.vectors[i] for i in anchors if wv1.get_word(i) not in self._exclude
            ]
            v2 = [
                wv2.vectors[i] for i in anchors if wv2.get_word(i) not in self._exclude
            ]
        elif self._anchor_indices is not None:
            v1 = [
                wv1.vectors[i]
                for i in self._anchor_indices
                if wv1.get_word(i) not in self._exclude
            ]
            v2 = [
                wv2.vectors[i]
                for i in self._anchor_indices
                if wv2.get_word(i) not in self._exclude
            ]
        elif self._anchor_words is not None:
            v1 = [wv1[w] for w in self._anchor_words if w not in self._exclude]
            v2 = [wv2[w] for w in self._anchor_words if w not in self._exclude]
        else:  # just use all words
            v1 = [wv1[w] for w in words if w not in self._exclude]
            v2 = [wv2[w] for w in words if w not in self._exclude]
        v1 = np.array(v1)
        v2 = np.array(v2)
        Q, _ = orthogonal_procrustes(v1, v2)
        wv1_ = WordVectors(words=wv1.get_words(), vectors=np.matmul(wv1.vectors, Q))
        return wv1_, wv2, Q
