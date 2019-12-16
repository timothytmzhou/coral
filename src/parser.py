import re
from tree import *
from tokens import *


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

    def parse(self, tokens):
        parsed = []
        for f, args in self.match(tuple(tokens)):
            parsed.append(f(self, *args))

        return parsed

    def parse_assignment(self, identifier, expr):
        return Assignment(identifier, self.parse_expr(expr))

    def parse_output(self, expr):
        return Output(self.parse_expr(expr))

    def parse_while(self, expr, statements):
        return While(self.parse_expr(expr), self.parse(statements))

    def parse_conditional(self, expr, statements):
        if_block = Conditional(self.parse_expr(expr), self.parse(statements))
        while self.check_pattern(r"elif ( \e ) \b")



    def match(self, tokens):
        token_index = 0
        while token_index < len(tokens):
            for p, func in Parser.patterns.items():
                is_match, args, length = self.check_pattern(p, tokens[token_index:])
                if is_match:
                    yield func, args
                    token_index += length
                    break
            else:
                # TODO: more descriptive error
                raise RuntimeError

    def check_pattern(self, pattern, tokens):
        """
        iterate over tokens until they match entire pattern or they fail to match
        :param pattern: string containing pattern to match against - see parse pattern for more info
        :param tokens: tuple of tokens to match the pattern against
        :return: (if the pattern matches, list of all variable tokens (\i, \e, \b, etc.))
        """
        # TODO: parse the pattern string properly
        pattern = pattern.split()
        token_index = 0
        tokens_length = len(tokens)
        args = []

        for pattern_index, token_seq in enumerate(pattern):
            if token_seq == r"\i":
                if tokens[token_index].token_type == TokenType.IDENTIFIER:
                    args.append(tokens[token_index].value)
                    token_index += 1
                else:
                    return False, None, 0

            elif token_seq == r"\e":
                expression = []
                next_in_pattern = pattern[pattern_index + 1]
                if next_in_pattern in r"\i\e":
                    # TODO: descriptive error for incorrect parse pattern
                    raise RuntimeError
                elif next_in_pattern == r"\b":
                    next_in_pattern = "{"

                while tokens[token_index].value != next_in_pattern:
                    if token_index == tokens_length:
                        return None, False
                    expression.append(tokens[token_index].value)
                    token_index += 1

                args.append(expression)

            elif token_seq == r"\b":
                balanced = self.read_until_balanced(tokens[token_index:], "{", "}")
                if balanced:
                    length, block = balanced
                    token_index += length
                    args.append(block)
                else:
                    return None, False, 0

            else:
                if re.match(token_seq, tokens[token_index].value):
                    token_index += 1
                else:
                    return None, False, 0

        return True, args, token_index

    def read_until_balanced(self, tokens, open_bracket, close_bracket):
        """
        reads tokens until there is a balanced amount of open_bracketing and closing bracket-types
        :param tokens: tuple of token objects
        :param open_bracket: open_bracketing bracket-type
        :param close_bracket: closing bracket-type
        :return: the number of read tokens, the read tokens if successful, else None
        """

        if tokens[0].value == open_bracket:
            buffer = []
            level = 0
            for token in tokens:
                if token.value == open_bracket:
                    level += 1
                elif token.value == close_bracket:
                    level -= 1
                buffer.append(token)
                if not level:
                    break
            else:
                raise SyntaxError("unbalanced bracketed expression detected")
            return len(buffer), buffer[1:-1]

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
        r"\i = \e ;": parse_assignment,
        r"print \e ;": parse_output,
        r"while ( \e ) \b": parse_while,
        r"if ( \e ) \b": parse_conditional  # elif and else pattern defined in parse_conditional
    }
