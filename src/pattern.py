from abc import ABC, abstractmethod
from tokens import TokenType, Token
from stream import Stream


class Match:
    def __init__(self, is_match, groups=None):
        if groups is None:
            groups = []
        self.is_match = is_match
        self.groups = groups

    def __bool__(self):
        return self.is_match

    def __str__(self):
        return str(self.__bool__())


class Pattern(ABC):
    @abstractmethod
    def match(self, token_stream):
        """
        pattern for matching against fixed sequence of tokens
        :param tokens: iterator of tokens
        :return: Match object
        """
        pass

    def __add__(self, other):
        if not isinstance(other, Pattern):
            raise TypeError("cannot combine Pattern object with non-pattern")
        # in the case of other + self, other.__add__ gets called
        # reduce self + other to that case
        elif isinstance(other, CombinedPattern):
            return other + self
        # must be two non-CombinedPattern objects as CombinedPattern overrides __add__
        else:
            return CombinedPattern(self, other)


class CombinedPattern(Pattern):
    def __init__(self, *patterns):
        self.patterns = patterns

    def match(self, token_stream):
        matches = []
        for i, pattern in enumerate(self.patterns):
            m = pattern.match(token_stream)
            if not m:
                if i != 0:
                    raise SyntaxError("unable to parse expected {}".format(pattern))
                return Match(False)
            matches.append(m)
        else:
            return Match(True,
                         groups=[m.groups for m in matches if m.groups])

    def __add__(self, other):
        if isinstance(other, CombinedPattern):
            return CombinedPattern(self.patterns + other.patterns)
        elif isinstance(other, Pattern):
            return CombinedPattern(*self.patterns, other)


class TokenSequence(Pattern):
    def __init__(self, *pattern):
        """
        directly matches against provided Token objects
        :param pattern: Any combination of Token objects and TokenTypes to match against
        """
        # type checks pattern
        assert all(isinstance(p, (str, TokenType)) for p in pattern)
        self.pattern = pattern
        self.pattern_len = len(self.pattern)

    def match(self, token_stream):
        groups = Stream()
        try:
            for i, p in enumerate(self.pattern):
                token = token_stream[i]
                if isinstance(p, TokenType) and token.token_type == p:
                    groups.append(token)
                elif isinstance(p, str) and token == Token(p):
                    continue
                else:
                    break
            else:
                token_stream.consume(self.pattern_len)
                return Match(True, groups=groups)
        except StopIteration:
            pass
        return Match(False)

    def __str__(self):
        body = []
        for p in self.pattern:
            if isinstance(p, TokenType):
                body.append(p.name.lower())
            elif isinstance(p, Token):
                body.append(p.value)
        return "sequence: {}".format(", ".join(body))


class TerminatingSequence(Pattern):
    def __init__(self, terminator=";"):
        self.terminator = Token(terminator)

    def match(self, token_stream):
        """
        consumes tokens until a terminator is found
        :return: Match(True) (error if terminator not found)
        """
        try:
            for i, token in enumerate(token_stream.stream()):
                if token == self.terminator:
                    groups = token_stream[:i]
                    token_stream.consume(i + 1)
                    return Match(True, groups=groups)
        except StopIteration:
            raise EOFError(
                "attempted to parse terminating sequence against stream without terminator")

    def __str__(self):
        return "terminator: {}".format(self.terminator)


class BracketedSequence(Pattern):
    def __init__(self, open, close):
        self.open = Token(open)
        self.close = Token(close)

    def match(self, token_stream):
        """
        reads tokens until there is a balanced amount of open_bracketing and closing bracket-types
        :param open_bracket: open_bracketing bracket-type
        :param close_bracket: closing bracket-type
        :return: the number of read tokens, the read tokens if successful, else None
        """
        if not token_stream[0] == self.open:
            return Match(False, groups=None)
        else:
            level = 0
            for i, token in enumerate(token_stream.stream()):
                if token == self.open:
                    level += 1
                elif token == self.close:
                    level -= 1
                if not level:
                    break
            else:
                raise SyntaxError("unbalanced bracketed expression detected")
            groups = token_stream[1:i]
            token_stream.consume(i + 1)
            return Match(bool(groups), groups=groups)

    def __str__(self):
        return "bracketed sequence: {0}...{1}".format(self.open.value, self.close.value)


class DelimitedSequence(Pattern):
    def __init__(self, delimiter=",", filter_func=lambda token: True):
        """
        pattern for matching against a delimited sequence e.g list, function args, etc.
        :param delimiter: str delimiter- default is separator comma
        :param filter_func: filtering function for elements
        """
        self.delimiter = Token(delimiter)
        self.filter_func = filter_func

    def match(self, token_stream):
        groups = Stream()
        while True:
            e = token_stream.peek()
            if self.filter_func(e):
                groups.append(e)
                next(token_stream)
            else:
                break
            d = token_stream.peek()
            if d == self.delimiter:
                next(token_stream)
            else:
                break
        return Match(True, groups=groups)

    def __str__(self):
        return "delimited sequence: {}".format(self.delimiter)


# some predefined patterns
eof = TerminatingSequence()
parenthetical = BracketedSequence("(", ")")
code_block = BracketedSequence("{", "}")
