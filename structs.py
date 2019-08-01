from enum import Enum
import string


allowed_identifier_chars = string.ascii_letters + string.digits + "_"


class Token:
    def __init__(self, token_type, value, node_type=None):
        self.token_type = token_type
        self.value = value
        self.node_type = node_type

    def __str__(self):
        string = f"{self.token_type}: {self.value}"
        if self.node_type is not None:
            string += f", {self.node_type.__name__}"
        return string


class TokenType(Enum):
    UNARY = 1
    BINARY = 2
    IDENTIFIER = 3
    VALUE = 4
    KEYWORD = 5
    SYMBOL = 6
    GROUPING = 7
    SEPARATOR = 8


# token types initialization
token_types = {}

def add_tokens(token_type, tokens):
    token_types.update({token: token_type for token in tokens})

add_tokens(TokenType.UNARY, ("!", "++", "--"))
add_tokens(TokenType.BINARY, ("=", "+", "-", "*", "/", "%", "&&", "||", "<", ">"))
add_tokens(TokenType.KEYWORD, ("if", "elif", "else", "while", "for", "do", "func", "return"))
add_tokens(TokenType.SYMBOL, (";",))
add_tokens(TokenType.GROUPING, ("(", ")", "{", "}"))
add_tokens(TokenType.SEPARATOR, (" ", ","))
