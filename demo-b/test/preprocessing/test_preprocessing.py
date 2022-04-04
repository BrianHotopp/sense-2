import unittest
from pathlib import Path

from app.preprocessing.WordVectors import WordVectors
from app.preprocessing.generate_embeddings.embed import (
    initial_scrub,
    generate_embedding,
)


class WordVectorsTest(unittest.TestCase):
    def test_preprocessing(self):
        in_path_s = "/home/brianhotopp/Dropbox/Spring 2022/Research/sense-demo/demo-b/test/preprocessing/test_data/english-1800-degenerate.txt"
        in_path = Path(in_path_s)
        out_path_s = "/home/brianhotopp/Dropbox/Spring 2022/Research/sense-demo/demo-b/test/preprocessing/test_data/english-1800-scrubbed.txt"
        out_path = Path(out_path_s)
        initial_scrub(in_path, out_path, 48)
        wv = generate_embedding(out_path)
        print(wv.words)
        assert True
        pass


if __name__ == "__main__":
    unittest.main()
