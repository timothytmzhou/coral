from enum import Enum
import string
import operator as op

allowed_identifier_chars = string.ascii_letters + string.digits + "_"

binary_operators = {
    "+": op.add,
    "-": op.sub,
    "*": op.mul,
    "/": op.truediv,
    "**": op.pow,
    "@": op.matmul,
    "%": op.mod,
    ">": op.gt,
    "<": op.lt,
    "===": op.is_,
    "!==": op.is_not,
    "==": op.eq,
    "!=": op.ne,
    ">=": op.ge,
    "<=": op.le,
    ">>": op.rshift,
    "<<": op.lshift,
    "&": op.and_,
    "|": op.or_,
    "^": op.xor,
    "&&": lambda a, b: a and b,
    "||": lambda a, b: a or b,
    "^^": lambda a, b: bool(a) != bool(b),
    ":>": lambda a, b: a in b,
}

operator_precedence = (
    ("**",),
    ("*", "/", "@", "%"),
    ("+", "-"),
    ("<<", ">>"),
    ("&",),
    ("^",),
    ("|",),
    (":>", "<", ">", "<=", ">=", "!=", "==", "===", "!=="),
    ("&&",),
    ("^^",),
    ("||",),
)


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
    CONTROL_FLOW = 5
    KEYWORD = 6
    SYMBOL = 7
    GROUPING = 8
    SEPARATOR = 9


# token types initialization
token_types = {}


def add_tokens(token_type, tokens):
    token_types.update({token: token_type for token in tokens})


add_tokens(TokenType.UNARY, ("!", "++", "--"))
add_tokens(TokenType.BINARY, tuple(binary_operators))
add_tokens(TokenType.CONTROL_FLOW, ("if", "elif", "else", "while", "for", "do"))
add_tokens(TokenType.KEYWORD, ("print",))
add_tokens(TokenType.SYMBOL, ("=", ":", "=>"))
add_tokens(TokenType.GROUPING, ("(", ")", "{", "}", ";"))
add_tokens(TokenType.SEPARATOR, (" ", ","))
