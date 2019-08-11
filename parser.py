from tree import *
from tokens import *


def read_until_char(tokens, char):
    """
    reads tokens until a specific value
    :param tokens: tuple of token objects
    :param char: the character to read until
    :return: the number of read tokens, the read tokens
    """
    i = 0
    while tokens[i].value != char:
        i += 1
    return i, tokens[:i]

def read_until_balanced(tokens, open, close):
    """
    reads tokens until there is a balanced amount of opening and closing bracket-types
    :param tokens: tuple of token objects
    :param open: opening bracket-type
    :param close: closing bracket-type
    :return: the number of read tokens, the read tokens
    """
    assert tokens[0].value == open
    buffer = []
    level = 0
    for token in tokens:
        if isinstance(token, Token):
            if token.value == open:
                level += 1
            elif token.value == close:
                level -= 1
        buffer.append(token)
        if not level:
            break
    else:
        raise SyntaxError("unbalanced bracketed expression detected")
    return len(buffer), buffer[1:-1]


class Parser:
    def __init__(self, tokens, module_name="main"):
        """
        :param tokens: generator yielding Token objects
        :param module_name: string used to name the Module object assigned to self.head
        """
        self.head = Module(self.parse(tuple(tokens)), module_name)

    def parse(self, tokens):
        parsed = []
        buffer = []
        i = 0
        while i < len(tokens):
            token = tokens[i]
            # split semicolons
            if token.value == ";":
                parsed.append(self.parse_statement(buffer))
                buffer.clear()
                i += 1
            elif token.token_type == TokenType.CONTROL_FLOW:
                if token.value == "if":
                    i, last = self.parse_conditional(i, tokens, True)
                    parsed.append(last)
                    while i < len(tokens) and tokens[i].value in ("elif", "else"):
                        is_else = tokens[i].value == "else"
                        i, current = self.parse_conditional(i, tokens, not is_else)
                        last.next_node = current
                        last = current
                        if is_else:
                            break
            else:
                buffer.append(token)
                i += 1
        return parsed

    def parse_conditional(self, i, tokens, has_condition):
        i += 1
        if has_condition:
            conditional_length, condition = read_until_balanced(tokens[i:], "(", ")")
            condition = self.parse_expr(condition)
            i += conditional_length
        else:
            condition = ObjectLookup("true")
        block_length, statements = read_until_balanced(tokens[i:], "{", "}")
        i += block_length
        return i, Conditional(condition, self.parse(statements))

    def parse_statement(self, statement):
        """
        :param statement: tuple of Token objects to be parsed into Expression nodes
        :return: appropriate AST_Node object
        """
        for i, token in enumerate(statement):
            if token.value == "=":
                return Assignment(
                    statement [i - 1].value,
                    self.parse_expr(statement[i + 1:])
                )
            elif token.value == "print":
                return Output(
                    self.parse_expr(statement[i + 1:])
                )

    def parse_expr(self, expr):
        expr = tuple(self.parse_values(expr))
        return self.combine(expr)

    def parse_values(self, expr):
        """
        :param expr: tuple of Token objects
        :yield: stream of tokens with primitives parsed as nodes
        """
        for token in expr:
            if token.token_type == TokenType.VALUE:
                Node = token.node_type
                yield Node(Node.cast(token.value))
            elif token.token_type == TokenType.IDENTIFIER:
                yield ObjectLookup(token.value)
            else:
                yield token

    def combine(self, expr):
        """
        :param expr: tuple of Token objects to be parsed into Expression nodes
        :return: appropriate Expression node
        """
        expr = tuple(self.combine_parenthesis(expr))
        for operators in operator_precedence:
            expr = tuple(self.combine_binary_operators(expr, operators))
        return expr[0]


    def combine_parenthesis(self, expr):
        """
        :param expr: tuple of Token objects
        :yield: stream of tokens with parenthesized expressions parsed as nodes
        """
        i = 0
        while i < len(expr):
            token = expr[i]
            if isinstance(token, Token) and token.value == "(":
                length, sub = read_until_balanced(expr[i:], "(", ")")
                i += length
                yield self.combine(sub)
            else:
                yield token
            i += 1

    def combine_binary_operators(self, expr, operators):
        """
        :param expr: tuple of Token objects
        :param operators: operators to be combined
        :yield: stream of tokens with binary operators and adjacent tokens parsed as nodes
        """
        i = 0
        while i < len(expr) - 2:
            left, middle, right = expr[i : i + 3]
            if isinstance(middle, Token) and middle.value in operators:
                combined = (
                    BinaryOperator(binary_operators[middle.value], left, right),
                    *expr[i + 3:]
                )
                yield from self.combine_binary_operators(combined, operators)
                break
            else:
                yield left
                i += 1
        else:
            for token in expr[i:]:
                yield token
