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

# rbp is set to multiples of 10 to support right associativity during parsing
operator_precedence = {op: i * 10 for i, ops in enumerate((
    ("||",),
    ("^^",),
    ("&&",),
    (":>", "<", ">", "<=", ">=", "!=", "==", "===", "!=="),
    ("|",),
    ("^",),
    ("&",),
    ("<<", ">>"),
    ("+", "-"),
    ("*", "/", "@", "%"),
    ("**",),
)) for op in ops}


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


class Token:
    def __init__(self, value, token_type=None, node_type=None):
        if token_type is None:
            token_type = token_types[value]
        self.token_type = token_type
        self.value = value

    def __str__(self):
        string = f"{self.token_type}: {self.value}"
        return string

    def __eq__(self, other):
        if isinstance(other, Token):
            return (
                    self.token_type == other.token_type and
                    self.value == other.value
            )
        else:
            return False


# token types initialization
token_types = {
    token: token_type for token_type, tokens in (
        (TokenType.UNARY, ("!", "++", "--")),
        (TokenType.BINARY, tuple(binary_operators)),
        (TokenType.CONTROL_FLOW, ("if", "elif", "else", "while", "for", "do")),
        (TokenType.KEYWORD, ("func", "return")),
        (TokenType.SYMBOL, (":", "=>", "=", "+=", "-=", "*=", "/=", "**=", "%=", "@=", ">>=",
                            "<<=", "&=", "|=", "^=")),
        (TokenType.GROUPING, ("(", ")", "{", "}", ";")),
        (TokenType.SEPARATOR, (" ", ","))
    ) for token in tokens
}
