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
        name = identifier[0].value
        expr = self.parse_expr(expr)
        return Assignment(name, expr)

    def parse_expr(self, expr, rbp=0):
        # Pratt parsing
        left = self.nud(expr)
        while expr and operator_precedence[(op := expr.peek().value)] > rbp:
            next(expr)
            left = self.led(left, op, expr)
        return left

    def nud(self, expr, parse_func=True):
        token = expr.peek()
        if token.token_type is TokenType.VALUE:
            next(expr)
            return Value(token.value)
        elif token.token_type is TokenType.IDENTIFIER:
            ahead = next(expr)
            # function calls
            if expr and (p := expr.peek().value) not in binary_operators and parse_func:
                func_name = ahead.value
                args = []
                while expr and expr.peek().value not in binary_operators:
                    args.append(self.nud(expr, parse_func=False))
                return Call(func_name, args)
            else:
                return ObjectLookup(token.value)
        elif token.token_type is TokenType.GROUPING:
            m = parenthetical.match(expr)
            if m:
                return self.parse_expr(m.groups)
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

    def parse_while(self, expr, statements):
        return While(self.parse_expr(expr), self.parse(statements))

    def parse_if(self, expr, statements):
        root = Conditional(self.parse_expr(expr), self.parse(statements))
        elifs = self.parse(
            patterns={TokenSequence("elif") + parenthetical + code_block:
                          Parser.parse_elif},
            raise_error=False
        )
        else_block = self.parse(patterns={
            TokenSequence("else") + code_block:
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

    def parse_func(self, name, args, statements):
        name = name[0].value
        if args:
            args = tuple(token.value for token in args)
        else:
            args = None
        return FuncDef(name, args, self.parse(statements))

    def parse_return(self, expr=None):
        if expr is None:
            return Return(ObjectLookup("null"))
        else:
            return Return(self.parse_expr(expr))

    patterns = {
        TokenSequence(TokenType.IDENTIFIER, "=") + eof: parse_assignment,
        TokenSequence("while") + parenthetical + code_block: parse_while,
        TokenSequence("if") + parenthetical + code_block: parse_if,
        TokenSequence("func", TokenType.IDENTIFIER) + TerminatingSequence("=") + code_block: parse_func,
        TokenSequence("return") + eof: parse_return,
        eof: parse_expr
    }
