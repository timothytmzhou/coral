from abc import ABC, abstractmethod
from tokens import TokenType


class Pattern(ABC):
    @abstractmethod
    def match(self, tokens):
        pass

class Block(Pattern):
    pass

class DelimitedSequence(Pattern):
    pass

class TokenSequence:
    pass
