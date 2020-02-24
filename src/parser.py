from tree import *
from tokens import *
from pattern import *


# TODO: update/add docstrings
class Parser:
    def __init__(self, tokens, module_name="main"):
        """
        :param tokens: generator yielding Token objects
        :param module_name: string used to name the Module object assigned to self.head
        """
        for f, args in self.match(tuple(tokens)):
            print(f"{f}: {args}")
        # self.head = Module(self.parse(tuple(tokens)), module_name)

    def parse(self, token_stream, patterns):
        parsed = []
        # TODO: write this
        return parsed

    def parse_assignment(self, identifier, expr):
        return Assignment(identifier, self.parse_expr(expr))

    def parse_output(self, expr):
        return Output(self.parse_expr(expr))

    def parse_while(self, expr, statements):
        return While(self.parse_expr(expr), self.parse(statements))

    def parse_conditional(self, expr, statements):
        # note: use elif/else patterns and self.parse for this
        pass

    def parse_expr(self, expr):
        # TODO: switch to Pratt parser
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
            left, middle, right = expr[i: i + 3]
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

    patterns = {
        TokenSequence(TokenType.IDENTIFIER, Token("=")) + eof: parse_assignment,
        TokenSequence(Token("print")) + eof: parse_output,
        TokenSequence(Token("while")) + parenthetical + code_block: parse_while,
        # TODO: conditionals (make parse take patterns and return list)
    }
