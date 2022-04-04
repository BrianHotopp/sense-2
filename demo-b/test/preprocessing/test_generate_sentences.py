from ctypes import alignment
from pathlib import Path
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
        i1 = occs1[target]
        i2 = occs2[target]
        # embed sentences
        indices1, s1_t_e = occ.embed_lines(pt1_s, i1, wv1)
        indices2, s2_t_e = occ.embed_lines(pt2_s, i2, wv2)
        print("sentences embedded")
        # align sentence embeddings using Q
        s1_t_e_a = np.matmul(s1_t_e, Q)
        print("sentences aligned")
        # find argmin of cosine similarity between s1_t_e_a and s2_t_e
        top_n_unique = 1000
        indices = np.argpartition(
            cosine_similarity(s1_t_e_a, s2_t_e),
            top_n_unique,
            axis=None,
            kind="introselect",
            order=None,
        )
        indices = indices[: min(len(indices), top_n_unique)]
        # indices = np.argmin(cosine_similarity(s1_t_e_a, s2_t_e))
        # unravel indices to get indices of sentences in pt1 and pt2
        print(f"length of indices {len(indices)}")
        match = 0
        used_i = set()
        used_j = set()
        for ind in indices:
            i, j = np.unravel_index(ind, (len(s1_t_e_a), len(s2_t_e)))
            if i not in used_i and j not in used_j:
                og_1 = indices1[i]
                og_2 = indices2[j]
                print(f"Match {match+1}")
                print("sentence 1")
                print(occ.line_from_file(pt1_s, og_1))
                print("sentence 2")
                print(occ.line_from_file(pt2_s, og_2))
                match += 1
                used_i.add(i)
                used_j.add(j)
                match += 1
            else:
                pass


if __name__ == "__main__":
    unittest.main()
