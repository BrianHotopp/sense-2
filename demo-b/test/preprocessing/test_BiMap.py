import unittest
from app.preprocessing.BiMap import BiMap 
class BiMapTest(unittest.TestCase):
    def test_bimap_init(self):
        words = list(set("the quick brown fox jumps over the lazy dog and says hello world test one two three".split()))
        a, b = zip(*enumerate(words))
        bm = BiMap(a, b)
        # check has the correct number of words
        assert(len(bm) == len(words))
        # check ab keys are the passed in words 
        l = set(bm.a_b.values())
        r = set(words)
        assert(l == r)
        # check ab keys are ba values
        l = set(bm.a_b.keys())
        r = set(bm.b_a.values())
        assert(l == r)
        # check ab values are ba keys
        l = set(bm.a_b.values())
        r = set(bm.b_a.keys())
        assert(l == r)
if __name__ == '__main__':
    unittest.main()