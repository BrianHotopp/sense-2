from time import time
import numpy as np
import json
from scipy.spatial.distance import cosine
from ...mapping import perform_mapping
from app.preprocessing.WordVectors import WordVectors
from .global_align import GlobalAlignConfig
from .noise_aware_align import NoiseAwareAlignConfig
from .s4_align import S4AlignConfig
from pathlib import Path
from sklearn.metrics.pairwise import paired_cosine_distances
from sklearn.metrics import pairwise_distances


class Alignment:
    def __init__(self, common, v1, v2, shifts, dists):
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
        wv1_aligned = cfg_obj.align(wv1, wv2)[0]
        # vectors for each word
        v1 = wv1_aligned.vectors
        v2 = wv2.vectors

        common = wv1.get_words()
        print("Number of words in common: {}".format(len(common)))
        # semantic shift for each word
        shifts = Alignment.compute_shifts(v1, v2)
        dists = Alignment.compute_dists(v1, v2)
        return Alignment(common, v1, v2, shifts, dists)

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
    def compute_shifts(wv1, wv2):
        """
        computes the semantic shift for each word in the example
        """
        # compute row-wise cosine similarity    
        # time how long it takes
        start = time()
        cosDist = True
        if not cosDist:
            # cos sim
            r = paired_cosine_distances(wv1, wv2) * -1 + 1
        else:
            r = paired_cosine_distances(wv1, wv2)
        end = time()
        print("Computing shifts took {} seconds".format(end - start))
        return r

    @staticmethod
    def compute_dists(v1, v2):
        """
        computes the distance between each word vector in the two examples
        """
        # time how long it takes
        start = time()
        # compute pairwise euclidean distance
        dists = pairwise_distances(v1, v2, metric='euclidean')
        end = time()
        print("Computing pairwise distances took {} seconds".format(end - start))
        return dists
