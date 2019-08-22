# useful data structures
class MultiDict:
    def __init__(self, key_value_pairs=None):
        """
        initializes a dictionary which maps multiple keys to the same value
        :param key_value_pairs: dict with items of form {(key1, key2): val}
        example:
            my_dict = MultiDict({("cat", "dog"): "animal"})
            my_dict["cat"] = "four-legged animal"
            assert my_dict["cat"] is my_dict["dog"]
        """
        if key_value_pairs is None:
            key_value_pairs = dict()
        else:
            self.key_value_pairs = key_value_pairs

    def __getitem__(self, item):
        for keyset in self.key_value_pairs:
            if item in keyset:
                return self.key_value_pairs[keyset]
        raise KeyError("invalid key passed")

    def __setitem__(self, key, value):
        for keyset in self.key_value_pairs:
            if key in keyset:
                self.key_value_pairs[keyset] = value
                break
        else:
            if not isinstance(key, tuple):
                raise TypeError("new keys must be given as tuple")
            self.key_value_pairs[key] = value

    def __contains__(self, key):
        return any(key in keyset for keyset in self.key_value_pairs)

    def __iter__(self):
        return iter(key for keyset in self.key_value_pairs for key in keyset)

    def pop(self, key):
        for keyset in self.key_value_pairs:
            if key in keyset:
                return self.key_value_pairs.pop(keyset)
        raise KeyError("invalid key passed")

    def __str__(self):
        return str(self.key_value_pairs).replace("(", "").replace(")", "")
