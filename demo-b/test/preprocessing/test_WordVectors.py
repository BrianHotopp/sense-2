import unittest
from app.preprocessing.WordVectors import WordVectors
class WordVectorsTest(unittest.TestCase):
    def test_wordvectors_initialization_from_disk(self):
        input_path = "test/test_data/wordvectors_short.txt"
        wv = WordVectors.from_file(input_path)
        # todo test wordvectors
        assert(True)
if __name__ == '__main__':
    unittest.main()