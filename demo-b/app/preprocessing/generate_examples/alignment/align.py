from time import time
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from app.preprocessing.WordVectors import WordVectors
import app.preprocessing.generate_embeddings.occurrences as occ
from .global_align import GlobalAlignConfig
from .noise_aware_align import NoiseAwareAlignConfig
from .s4_align import S4AlignConfig
from pathlib import Path
from sklearn.metrics.pairwise import paired_cosine_distances
from sklearn.metrics import pairwise_distances



class Alignment:
    def __init__(self, common, v1, v2, shifts, dists, Q):
        """
        creates an alignment object
        :param common: list of common words
        :param v1: word vectors 1
        :param v2: word vectors 2
        :param shifts: list of shifts
        :param dists: list of distances
        """
        self.common = common
        self.v1 = v1
        self.v2 = v2
        self.shifts = shifts
        self.dists = dists
        self.Q = Q
    @staticmethod
    def top_shifted_words(common, shifts, num_words=10):
        """
        returns the top num_words shifted words in the alignment
        """
        # error check inputs
        if len(common) != len(shifts):
            raise ValueError("common and shifts must be the same length")
        # if num words is the wrong type
        if not isinstance(num_words, int):
            raise TypeError("num_words must be an integer")
        if num_words < 0:
            raise ValueError("num_words must be greater than 0")
        if num_words == 0:
            return []

        # get the top shifted words
        num_words = min(num_words, len(shifts)-1)
        indices = np.argpartition(shifts, -1*num_words)[-1*num_words:]
        top_shifted_words = [(common[i], shifts[i]) for i in indices]
        top_shifted_words.sort(key=lambda x: x[1], reverse=True)
        return top_shifted_words
    @staticmethod
    def get_context(common, v1, v2, dists, target, first, num_neighbors = 10):
        """
        get the nearest neighbors of the target word in the adjacent context
        """
        # this is bad o(n) in the number of words in the intersection
        # but fixing will require ds refactor
        # todo
        wi = common.index(target)
        # get the nearest neighbors
        if first:
            # target word is in the first context
            # find nearest neighbors in the second context
            indices = np.argpartition(dists[wi, :], num_neighbors)[:num_neighbors]
            r = [(common[i], dists[wi, i], v2[i]) for i in indices]
            iv = v1[wi]
        else:
            # target word is in the second context
            # find nearest neighbors in the first context
            indices = np.argpartition(dists[:, wi], num_neighbors)[:num_neighbors]
            r = [(common[i], dists[i, wi], v1[i]) for i in indices]
            iv = v2[wi]
        r.sort(key=lambda x: x[1])
        # return unzipped r
        words, distances, vectors = zip(*r)
        return words, distances, vectors, iv

    @staticmethod
    def from_wv_and_config(wv1, wv2, config_dict):
        """
        generates an alignment object from wv1 and wv2
        assumes the embeddings have already been intersected
        wv1: WordVectors object
        wv2: WordVectors object
        config_dict: dict() of the config for the alignment
        """
        cfg_obj = Alignment.config_from_dict(config_dict)
        # intersect wv1, wv2
        wv1, wv2 = WordVectors.intersect(wv1, wv2)
        wv1_aligned, _, Q = cfg_obj.align(wv1, wv2)
        # vectors for each word
        v1 = wv1_aligned.vectors
        v2 = wv2.vectors

        common = wv1.get_words()
        # semantic shift for each word
        shifts = Alignment.compute_shifts(v1, v2)
        dists = Alignment.compute_dists(v1, v2)
        return Alignment(common, v1, v2, shifts, dists, Q)

    @staticmethod
    def config_from_dict(config_dict):
        """
        Generate an alignment configuration
        config_json: dict() of the alignment configuration
        returns: AlignmentConfig object
        """
        args = config_dict["args"]
        if config_dict["alignment_type"] == "s4":
            return S4AlignConfig(**args)
        elif config_dict["alignment_type"] == "global":
            return GlobalAlignConfig(**args)
        elif config_dict["alignment_type"] == "noise-aware":
            return NoiseAwareAlignConfig(**args)
        else:
            raise ValueError("Unknown alignment type encountered in config")

    @staticmethod
    def compute_shifts(wv1, wv2, verbose=False):
        """
        computes the semantic shift for each word in the example
        """
        # compute row-wise cosine similarity
        # time how long it takes
        if verbose:
            start = time()
        cosDist = True
        if not cosDist:
            # cos sim
            r = paired_cosine_distances(wv1, wv2) * -1 + 1
        else:
            r = paired_cosine_distances(wv1, wv2)
        if verbose:
            end = time()
            print("Computing shifts took {} seconds".format(end - start))
        return r

    @staticmethod
    def compute_dists(v1, v2, verbose=False):
        """
        computes the distance between each word vector in the two examples
        """
        if verbose:
            # time how long it takes
            start = time()
        # compute pairwise euclidean distance
        dists = pairwise_distances(v1, v2, metric="euclidean")
        if verbose:
            end = time()
            print("Computing pairwise distances took {} seconds".format(end - start))
        return dists
    @staticmethod
    def get_example_sentences(target, occ1, occ2, spt_path1, spt_path2, Q, wv1, wv2, max_sent=1000):
        """
        gets a pair of example sentences
        target: word to find example sentences for
        occ1: dictionary containing the number of times each word occurs in each line of pt1
        occ2: dictionary containing the number of times each word occurs in each line of pt2
        spt_path1: path object to the scrubbed plaintext 1
        spt_path2: path object to the scrubbed plaintext 2
        Q: rotation matrix of the associated alignment
        wv1: WordVectors to embed the sentences from pt1 with
        wv2: WordVectors to embed the sentences from pt2 with
        max_sent: the maximum number of sentences to return
        """
        i1 = occ1[target]
        i2 = occ2[target]
        indices1, s1te = occ.embed_lines(spt_path1, i1, wv1)
        indices2, s2te = occ.embed_lines(spt_path2, i2, wv2)
        # align embedded sentences using Q
        s1tea = np.matmul(s1te, Q)
        max_sent = min(max_sent, len(indices1), len(indices2))
        indices = np.argpartition(
            cosine_similarity(s1tea, s2te),
            max_sent,
            axis=None,
            kind="introselect",
            order=None
        )
        indices = indices[:min(len(indices), max_sent)]
        spt1inds =  []
        spt2inds = []
        used_i = set()
        used_j = set()
        for ind in indices:
            i, j = np.unravel_index(ind, (len(s1tea), len(s2te)))
            if i not in used_i and j not in used_j:
                spt1inds.append(indices1[i])
                spt2inds.append(indices2[j])
                used_i.add(i)
                used_j.add(j)
        # zip and return
        sents = []
        for i1, i2 in zip(spt1inds, spt2inds):
            sents.append((occ.line_from_file(spt_path1, i1), occ.line_from_file(spt_path2, i2)))
        return sents


    @staticmethod
    def get_random_sentence(target, occ1, occ2, spt_path1, spt_path2, Q, wv1, wv2, max_sent=1000):
        """
        gets a pair of example sentences
        a pair looks liks (sent1, list(sent2))
        where sent1 is from spt_path1 and sent2 is from spt_path2
        target: word to find example sentences for
        occ1: dictionary containing the number of times each word occurs in each line of pt1
        occ2: dictionary containing the number of times each word occurs in each line of pt2
        spt_path1: path object to the scrubbed plaintext 1
        spt_path2: path object to the scrubbed plaintext 2
        Q: rotation matrix of the associated alignment
        wv1: WordVectors to embed the sentences from pt1 with
        wv2: WordVectors to embed the sentences from pt2 with
        max_sent: the maximum number of sentences to return
        """
        i1 = occ1[target]
        i2 = occ2[target]
        indices1, s1te = occ.embed_lines(spt_path1, i1, wv1)
        indices2, s2te = occ.embed_lines(spt_path2, i2, wv2)
        # align embedded sentences using Q
        s1tea = np.matmul(s1te, Q)
        max_sent = min(max_sent, len(indices1), len(indices2))
        sims = cosine_similarity(s1tea, s2te)
        # randomly pick some sentence from the first context
        i = int(np.random.choice(range(len(indices1)), 1)[0])
        # subset sims to only compare to the sentence we picked
        sims = sims[i, :]
        max_sent = min(3, sims.shape[0])
        indices = np.argpartition(
            sims,
            max_sent,
            axis=None,
            kind="introselect",
            order=None
        )
        indices = indices[:min(len(indices), max_sent)]
        spt2inds = []
        for ind in indices:
            j = ind 
            spt2inds.append(indices2[j])
        sents = []
        for i2 in spt2inds:
            sents.append(occ.line_from_file(spt_path2, i2))
        ts = occ.line_from_file(spt_path1, indices1[i])
        return ts, sents


        