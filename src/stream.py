from more_itertools import peekable


class Stream(peekable):
    def __init__(self, iterable):
        """
        subclass for peekable providing several helper methods
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
