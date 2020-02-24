from abc import ABC, abstractmethod
from tokens import TokenType, Token


class Match:
    def __init__(self, is_match, groups=None):
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
                    raise SyntaxError("unable to parse expected {}".format(pattern[i]))
                return Match(False)
            matches.append(m)
        else:
            return Match(True, groups=sum((match.groups for match in matches), []))

    def __add__(self, other):
        if isinstance(other, CombinedPattern):
            return CombinedPattern(self.patterns + other.patterns)


class TokenSequence(Pattern):
    def __init__(self, *pattern):
        """
        directly matches against provided Token objects
        :param pattern: Any combination of Token objects and TokenTypes to match against
        """
        # TODO: type check pattern
        self.pattern = pattern
        self.pattern_len = len(self.pattern)

    def check_token(self, i, token):
        """
        checks if token matches ith element of self.pattern
        :param i: index of self.pattern to check against
        :param token: Token object
        :return: boolean indicating match
        """
        p = self.pattern[i]
        if isinstance(p, TokenType):
            return token.token_type == p
        else:
            return token == p

    def match(self, token_stream):
        try:
            for i, token in enumerate(token_stream.stream()):
                if not self.check_token(i, token):
                    break
            else:
                token_stream.consume(self.pattern_len)
                return Match(True)
        except StopIteration:
            pass
        return Match(False)

    def __str__(self):
        stringified = []
        for p in self.pattern:
            if isinstance(p, TokenType):
                stringified.append(p.name.lower())
            elif isinstance(p, Token):
                stringified.append(p.value)
        return "sequence: {}".format(", ".join(stringified))


class TerminatingSequence(Pattern):
    def __init__(self, terminator=Token(";")):
        self.terminator = terminator

    def match(self, token_stream):
        """
        consumes tokens until a terminator is found
        :return: Match(True) (error if terminator not found)
        """
        try:
            for token in token_stream:
                if token == self.terminator:
                    return Match(True)
        except StopIteration:
            raise EOFError(
                "attempted to parse terminating sequence against stream without terminator")

    def __str__(self):
        return "terminator: {}".format(self.terminator)


class BracketedSequence(Pattern):
    def __init__(self, open, close):
        self.open = open
        self.close = close

    def match(self, token_stream):
        """
        reads tokens until there is a balanced amount of open_bracketing and closing bracket-types
        :param open_bracket: open_bracketing bracket-type
        :param close_bracket: closing bracket-type
        :return: the number of read tokens, the read tokens if successful, else None
        """
        buffer = []
        level = 0
        for token in token_stream:
            if token == self.open:
                level += 1
            elif token.value == self.close:
                level -= 1
            buffer.append(token)
            if not level:
                break
        else:
            raise SyntaxError("unbalanced bracketed expression detected")
        return Match(len(buffer), buffer[1:-1])

    def __str__(self):
        return "bracketed sequence: {0}...{1}".format(self.open, self.close)


class DelimitedSequence(Pattern):
    def __init__(self, filter_func=lambda x: True, delimiter=Token(",")):
        """
        pattern for matching against a delimited sequence e.g list, function args, etc.
        :param delimiter: Token delimiter - default is separator comma
        :param filter_func: filtering function for elements
        """
        self.delimiter = delimiter
        self.filter_func = filter_func

    def match(self, token_stream):
        groups = []
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
        return Match(True, groups)

    def __str__(self):
        return "delimited sequence: {}".format(self.delimiter)


# some predefined patterns
eof = TerminatingSequence()
parenthetical = BracketedSequence(Token("("), Token(")"))
code_block = BracketedSequence(Token("{"), Token("}"))
