class BiMap():
    """
    implements a bidirectional dictionary
    """
    def __init__(self, a, b):
        """
        a: collection containing variables of a hashable type 
        b: collection containing variables of a hashable type 
        """
        # todo somehow assert that a and b are both collections
        # containing hashable types
        assert(len(a) == len(b))
        self.a_b = dict(zip(a, b))
        self.b_a = dict(zip(b, a))
    def __len__(self):
        """returns the number of key, value pairs in the BiMap (the length of the BiMap)"""
        return len(self.a_b)
    def __contains__(self, key):
        """returns true if the BiMap contains key"""
        return key in self.a_b
    def get_value(self, key):
        """gets a value corresponding to a key in a BiMap"""
        return self.a_b.get(key)
    def get_key(self, value):
        """gets a key corresponding to a value in a BiMap"""
        return self.b_a.get(value)
    def add(self, key, value):
        """adds a key, value pair from the Bimap"""
        self.a_b[key] = value
        self.b_a[value] = key
    def remove(self, key, value):
        """removes a key, value pair from the BiMap"""
        del self.a_b[key]
        del self.b_a[value]
    def keys(self):
        """returns a list of the keys in the BiMap"""
        return self.a_b.keys()
    def values(self):
        """returns a list of the values in the BiMap"""
        return self.b_a.keys()
