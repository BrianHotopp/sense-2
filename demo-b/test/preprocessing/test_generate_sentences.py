from ctypes import alignment
from pathlib import Path
import time
import numpy as np
import random

# import pairwise cosine from sklearn
from sklearn.metrics.pairwise import cosine_similarity
from app.preprocessing.WordVectors import WordVectors
import app.preprocessing.generate_embeddings.embed as embed
import app.preprocessing.generate_embeddings.occurrences as occ
import app.preprocessing.generate_examples.alignment.global_align as galign
from app.preprocessing.generate_examples.alignment.align import Alignment
import unittest


class ExampleSentencesTest(unittest.TestCase):
    def test_generate_examples(self):
        # process is as follows
        # W1, W2 = generate word embedding for pt1 and pt2
        # S1, S2 = generate sentence embedding for pt1 and pt2 using W1, W2
        # align words to find Q
        # S1A = align sentence embeddings for pt1 using Q found from word alignment
        # do argpartition (pairwise cosine similarity between S1A, S2)
        # unravel result of argpartition to find i, j where i is the index of the sentence in pt1 and j is the index of the sentence in pt2
        # return sentence i from pt1 and sentence j from pt2
        p1 = "/home/brianhotopp/Dropbox/Spring 2022/Research/sense-demo/demo-b/test/preprocessing/test_data/english-1800.txt"
        pt1_p = Path(p1)
        p2 = "/home/brianhotopp/Dropbox/Spring 2022/Research/sense-demo/demo-b/test/preprocessing/test_data/english-2000.txt"
        pt2_p = Path(p2)
        p1s = "/home/brianhotopp/Dropbox/Spring 2022/Research/sense-demo/demo-b/test/preprocessing/test_data/english-1800-scrubbed.txt"
        pt1_s = Path(p1s)
        p2s = "/home/brianhotopp/Dropbox/Spring 2022/Research/sense-demo/demo-b/test/preprocessing/test_data/english-2000-scrubbed.txt"
        pt2_s = Path(p2s)
        # generate scrubbed file for these two
        embed.initial_scrub(pt1_p, pt1_s)
        embed.initial_scrub(pt2_p, pt2_s)
        # generate embeddings for these two
        wv1 = embed.generate_embedding(pt1_s)
        wv2 = embed.generate_embedding(pt2_s)
        print("embeddings generated")
        # generate occurrences map for the embeddings
        occs1 = occ.get_occurrences(pt1_s)
        occs2 = occ.get_occurrences(pt2_s)
        print("occurrences generated")
        # create global alignment config to align the two wv using the default global align
        cfg = galign.GlobalAlignConfig()
        # intersect before alignment
        wv1i, wv2i = WordVectors.intersect(wv1, wv2)
        wv1a, wv2a, Q = cfg.align(wv1i, wv2i)
        # example target word
        target = "margin"
        print(f"there are at least {len(occs1[target])} sentences in pt1 with {target}")
        print(f"there are at least {len(occs2[target])} sentences in pt2 with {target}")
        # indices of sentences in pt1 and pt2 that contain the target word
        # time it
        start = time.time()
        sexs = Alignment.get_example_sentences(target, occs1, occs2, pt1_s, pt2_s, Q, wv1, wv2)
        # end
        end = time.time()
        c = 0
        print(f"Found {len(sexs)} examples in {end-start} seconds")
        for sents in sexs:
            print(f"Example {c}:")
            print("Sentence 1")
            print(sents[0])
            print("Sentence 2")
            print(sents[1])
        
if __name__ == "__main__":
    unittest.main()
