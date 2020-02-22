from more_itertools import peekable


class StreamMeta(type):
    no_override = ["__new__", "__getattribute__", "__setattr__", "__delattr__", "__class__"]

    def __new__(cls, name, parents, dct):
        for m in dir(peekable):
            if m not in dct and m not in StreamMeta.no_override:
                dct[m] = lambda self, *args, m=m: getattr(peekable, m)(self.iterator, *args)
        return type.__new__(cls, name, parents, dct)


class Stream(metaclass=StreamMeta):
    def __init__(self, iterator):
        """
        wrapper class for peekable (that's a lot of wrapping!)
        :param iterator: base iterator
        """
        self.iterator = peekable(iterator)

    def get(self, n):
        """
        pop n elements
        :param n: number of elements to pop
        :return: whether n elements were left in self.iterator, popped elements
        """
        buffer = peekable[:n]
        return len(buffer) == n, buffer

    def consume(self, n):
        """
        consume n elements
        :param n: number of elements to consume
        :return: True if there were n elements left to consume
        """
        try:
            for i in range(n):
                next(self.iterator)
        except StopIteration:
            return False
        else:
            return True
