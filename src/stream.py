from more_itertools import peekable, consume


class Stream(peekable):
    def __init__(self, iterable):
        """
        wrapper class for peekable (that's a lot of wrapping!)
        :param iterator: base iterator
        """
        super().__init__(iterable)

    def stream(self):
        """
        allows for iteration without consuming tokens
        :yield: sequential tokens
        """
        i = 0
        while True:
            try:
                yield self[i]
            except IndexError:
                raise StopIteration
            i += 1


    def get(self, n):
        """
        pop n elements
        :param n: number of elements to pop
        :return: whether n elements were left in self.iterator, popped elements
        """
        buffer = self[:n]
        return len(buffer) == n, buffer

    def consume(self, n=None):
        """
        consume n elements
        :param n: number of elements to consume (if None consume all)
        :return: True if there were n elements left to consume
        """
        try:
            for i in range(n):
                next(self)
        except StopIteration:
            return False
        else:
            return True
