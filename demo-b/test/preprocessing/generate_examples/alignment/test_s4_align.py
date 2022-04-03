import unittest
import numpy as np
from app.preprocessing.WordVectors import WordVectors
from app.preprocessing.generate_embeddings.generate_embeddings import main as generate_embeddings_main
from app.preprocessing.generate_examples.generate_examples import main as generate_examples_main
import app.preprocessing.generate_examples.alignment.s4_align as s4_align
from scipy.spatial.distance import cosine, euclidean

class S4AlignTest(unittest.TestCase):
    def setUp(self):
        pass
    def tearDown(self):
        pass
    def test_inject_change_single(self):
        wv1_path = "test/preprocessing/generate_examples/alignment/test_data/embeddings/a1b35050-53d8-4a6d-ae66-fb31c352f39b.txt"
        wv2_path = "test/preprocessing/generate_examples/alignment/test_data/embeddings/b5d9f20c-55d2-4a7e-9558-9eea4723a2db.txt"
        wv1 = WordVectors.from_file(wv1_path)
        wv2 = WordVectors.from_file(wv2_path)
        words = wv1.get_words()
        word = words[0]
        v_a = wv2.get_vector(word)
        alpha = 0.5
        replace = False
        max_tries = 50
        modified = s4_align.inject_change_single(wv1, word, wv1.get_words(), v_a, alpha, replace, max_tries)
        # The modified vector of w must have a higher cosine distance to v_a
        # than its original version
        og_cos_dist = cosine(wv1.get_vector(word), wv2.get_vector(word))
        mod_cos_dist = cosine(modified, wv2.get_vector(word))
        assert(mod_cos_dist > og_cos_dist)
    def test_get_features(self):
        x = np.array([
            [0.1, 0.2, 0.4, 0.5],
            [0.3, 0.4, 0.3, 0.1]]
            )
        feat = s4_align.get_features(x) 
        assert(True)
    #@unittest.skip("testing dependencies")
    def test_align(self):
        wv1_path = "test/preprocessing/generate_examples/alignment/test_data/embeddings/a1b35050-53d8-4a6d-ae66-fb31c352f39b.txt"
        wv2_path = "test/preprocessing/generate_examples/alignment/test_data/embeddings/b5d9f20c-55d2-4a7e-9558-9eea4723a2db.txt"
        wv1 = WordVectors.from_file(wv1_path)
        wv2 = WordVectors.from_file(wv2_path)
        a = s4_align.S4AlignConfig()
        wv1_, wv2, Q = a.align(wv1, wv2)
        #p = "test/preprocessing/generate_examples/alignment/test_data/embeddings/out.txt"
        #wv1.to_file(p)
        return

if __name__ == '__main__':
    unittest.main()
