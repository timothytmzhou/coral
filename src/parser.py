from tree import *
from tokens import *
from pattern import *


# TODO: update/add docstrings
class Parser:
    def __init__(self, token_stream, module_name="main"):
        """
        :param token_stream: Stream object from lexer
        :param module_name: string used to name the Module object assigned to self.head
        """
        self.token_stream = token_stream
        self.head = Module(self.parse(), module_name)

    def parse(self, token_stream=None, patterns=None, raise_error=True):
        """
        parse token_stream against a patterns dict
        :param patterns: dict of form {pattern: func}
        :return: list of Statement nodes
        """
        if patterns is None:
            patterns = Parser.patterns
        if token_stream is None:
            token_stream = self.token_stream
        parsed = []
        while token_stream:
            for pattern, func in patterns.items():
                m = pattern.match(token_stream)
                if m:
                    if isinstance(pattern, CombinedPattern):
                        parsed.append(func(self, *m.groups))
                    else:
                        parsed.append(func(self, m.groups))
                    break
            else:
                if raise_error:
                    raise SyntaxError
                else:
                    break
        return parsed

    def parse_assignment(self, identifier, expr):
        return Assignment(identifier[0].value, self.parse_expr(expr))

    def parse_output(self, expr):
        return Output(self.parse_expr(expr))

    def parse_while(self, expr, statements):
        return While(self.parse_expr(expr), self.parse(statements))

    def parse_if(self, expr, statements):
        root = Conditional(self.parse_expr(expr), self.parse(statements))
        elifs = self.parse(
            patterns={TokenSequence(Token("elif")) + parenthetical + code_block:
                          Parser.parse_elif},
            raise_error=False
        )
        else_block = self.parse(patterns={
            TokenSequence(Token("else")) + code_block:
                Parser.parse_else},
            raise_error=False
        )
        previous = root
        for conditional in elifs + else_block:
            previous.next_node = conditional
            previous = conditional
        return root

    def parse_elif(self, expr, statements):
        return Conditional(self.parse_expr(expr), self.parse(statements))

    def parse_else(self, statements):
        return Conditional(ObjectLookup("true"), self.parse(statements))

    def parse_expr(self, expr, rbp=0):
        # modified pratt parser
        left = self.nud(expr)
        while expr and operator_precedence[(op := expr.peek().value)] > rbp:
            next(expr)
            left = self.led(left, op, expr)
        return left

    def nud(self, expr):
        token = expr.peek()
        if token.token_type is TokenType.VALUE:
            next(expr)
            Object_Type = token.node_type
            return Value(Object_Type(Object_Type.cast(token.value)))
        elif token.token_type is TokenType.IDENTIFIER:
            next(expr)
            return ObjectLookup(token.value)
        elif token.token_type is TokenType.GROUPING:
            m = parenthetical.match(expr)
            if m:
                return self.parse_expr(m.groups)
        elif token.token_type is TokenType.OPERATOR:
            if token.value == "-":
                next(expr)
                return UnaryOperator(unary_operators[token.value],
                                     self.parse_expr(expr, rbp=operator_precedence["-"]))
        else:
            raise SyntaxError("non-value {}".format(token))

    def led(self, left, op, expr):
        precedence = operator_precedence[op]
        # right associativity
        if op == "**":
            precedence -= 1
        return BinaryOperator(
            binary_operators[op],
            left,
            self.parse_expr(expr, rbp=precedence)
        )

    patterns = {
        TokenSequence(TokenType.IDENTIFIER, "=") + eof: parse_assignment,
        TokenSequence("print") + eof: parse_output,
        TokenSequence("while") + parenthetical + code_block: parse_while,
        TokenSequence("if") + parenthetical + code_block: parse_if
    }
