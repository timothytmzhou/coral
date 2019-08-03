from token import *
from tree import *
import itertools


def sorted_groupby(iterable, key=lambda x: x, reverse=True):
    """
    sorts elements according to a key function, then groups them
    :param iterable: the iterable to sort and group
    :param key: key function by which elements are grouped
    :param reverse: whether to reverse the order of the sorted elements or not
    :return: tuples of the form (key value, group) in sorted order
    """
    s = sorted(iterable, key=key, reverse=reverse)
    return itertools.groupby(s, key)


def unpack(grouped):
    """
    flattens a groupby object
    :param grouped: itertools.groupby object
    :return: list containing tuples of form (key_val, element) for every element in all groups
    """
    return [
        (key_val, e) for key_val, group in grouped
        for e in group
    ]


class Scanner:
    def __init__(self, source):
        self.pos = 0
        self.source = source
        self.len = len(source)

    def stream(self):
        """
        streams characters from source
        :yield: tuples of form (index, char) similar to enumerate()
        """
        while self.pos < len(self.source):
            yield self.pos, self.source[self.pos]
            self.pos += 1

    def peek(self, n):
        """
        get source n characters ahead from current position without advancing self.pos
        :param n: how many characters to peek ahead
        :return: next n characters of source
        """
        return self.source[self.pos: self.pos + n]

    def peek_at(self, n):
        """
        get specific character n indices ahead of current position without advancing self.pos
        :param n: how many characters to peek ahead
        :return: character at self.pos + n
        """
        if self.pos + n >= self.len:
            return None
        else:
            return self.source[self.pos + n]

    def advance(self, n):
        """
        advances current position n times ahead
        :param n: how many steps to advance
        """
        self.pos += n


class Lexer:
    def __init__(self, source):
        self.scanner = Scanner(source)

    def tokenize(self):
        """
        performs lexical analysis on source to split it into more easily parsed tokens
        :yield: Token objects
        """
        sorted_token_types = unpack(sorted_groupby(token_types, key=lambda x: len(x)))
        for index, char in self.scanner.stream():
            if char in (" ", "\n"):
                continue
            # check if the index is the start of a pre-defined token
            for length, token in sorted_token_types:
                if self.scanner.peek(length) == token:
                    if not (
                            token_types[token] == TokenType.KEYWORD and
                            self.scanner.peek_at(length) in allowed_identifier_chars
                    ):
                        yield Token(token_types[token], token)
                        self.scanner.advance(length - 1)
                    break
            else:
                # check if the character is the start of a string
                if char in "\"'":
                    string = self.read_string(char)
                    yield Token(TokenType.VALUE, string, String)
                # check if the character is the start of an int or float
                elif char.isdigit():
                    num, is_float = self.read_num()
                    yield Token(TokenType.VALUE, num, Float if is_float else Integer)
                # check if the character is the start of an identifier
                elif char in allowed_identifier_chars:
                    identifier = self.read_identifier()
                    yield Token(TokenType.IDENTIFIER, identifier)
                else:
                    raise SyntaxError("improper token found")

    def read_string(self, quote_type):
        """
        reads from scanner until end quote
        :param quote_type: type of quotation to read until
        :return: read string
        """
        string = ""
        i = 1
        while True:
            s = self.scanner.peek_at(i)
            i += 1
            if s is None or (s == quote_type and string[-1] != "\\"):
                break
            string += s
        # advance scanner and yield string token
        self.scanner.advance(i - 1)
        return string

    def read_num(self):
        """
        reads from scanner until a non-numeric character
        :return: tuple containing the read number and whether it was a float
        """
        num = ""
        is_float = False
        i = 0
        while True:
            s = self.scanner.peek_at(i)
            if s is None:
                break
            if s.isdigit():
                num += s
            elif s == "." and not is_float:
                num += s
                is_float = True
            else:
                break
            i += 1
        # advance scanner and yield int/float token
        self.scanner.advance(i - 1)
        return num, is_float

    def read_identifier(self):
        """
        reads from scanner until non-valid identifier character
        :return: read identifier
        """
        identifier = ""
        i = 0
        while True:
            s = self.scanner.peek_at(i)
            if s is None:
                break
            if s in allowed_identifier_chars:
                identifier += s
            else:
                break
            i += 1
        # advance scanner and yield identifier token
        self.scanner.advance(i - 1)
        return identifier
