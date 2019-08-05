from tree import *
from token import *
import operator as op
import itertools


class Parser:
    binary_operators = {
        "+": op.add,
        "-": op.sub,
        "*": op.mul,
        "/": op.truediv,
        "%": op.mod,
        "&&": lambda a, b: a and b,
        "||": lambda a, b: a or b
    }

    def __init__(self, tokens, module_name="main"):
        """
        :param tokens: generator yielding Token objects
        :param module_name: string used to name the Module object assigned to self.head
        """
        self.tokens = tokens
        self.head = Module(self.parse(), module_name)

    def parse(self):
        parsed = []
        buffer = []
        for token in self.tokens:
            if token.token_type == TokenType.GROUPING:
                if token.value == ";":
                    parsed.append(self.parse_statement(buffer))
                    buffer.clear()
            elif token.token_type == TokenType.CONTROL_FLOW:
                pass
            else:
                buffer.append(token)
        return parsed

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
        expr = tuple(self.combine_binary_operators(expr, "*", "/"))
        expr = next(self.combine_binary_operators(expr, "+", "-"))
        return expr

    def combine_parenthesis(self, expr):
        """
        :param expr: tuple of Token objects
        :yield: stream of tokens with parenthesized expressions parsed as nodes
        """
        paren_stack = []
        i = 0
        while i < len(expr):
            token = expr[i]
            if isinstance(token, Token) and token.value == "(":
                start = i + 1
                paren_stack.append(token)
                while len(paren_stack):
                    i += 1
                    if i == len(expr):
                        raise SyntaxError("unbalanced parenthesized expression")
                    elif expr[i].value == "(":
                        paren_stack.append(expr[i])
                    elif expr[i].value == ")":
                        paren_stack.pop()
                yield self.combine(expr[start: i])
            else:
                yield token
            i += 1

    def combine_binary_operators(self, expr, *operators):
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
                    BinaryOperator(Parser.binary_operators[middle.value], left, right),
                    *expr[i + 3:]
                )
                yield from self.combine_binary_operators(combined, *operators)
                break
            else:
                yield left
                i += 1
        else:
            for token in expr[i:]:
                yield token
