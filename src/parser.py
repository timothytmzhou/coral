import re
from tree import *
from tokens import *


# TODO: update/add docstrings


class Parser:
    patterns = {
        "\i = \e ;": Assignment,
        "print \e ;": Output,
        r"while ( \e ) \b": While
    }

    def __init__(self, tokens, module_name="main"):
        """
        :param tokens: generator yielding Token objects
        :param module_name: string used to name the Module object assigned to self.head
        """
        for f, args in self.match(tuple(tokens)):
            print(f"{f}: {args}")
        # self.head = Module(self.parse(tuple(tokens)), module_name)

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
                if token_seq == tokens[token_index].value:
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

    # def parse(self, tokens):
    #     parsed = []
    #     buffer = []
    #     i = 0
    #     while i < len(tokens):
    #         token = tokens[i]
    #         # split semicolons
    #         if token.value == ";":
    #             parsed.append(self.parse_statement(buffer))
    #             buffer.clear()
    #             i += 1
    #         elif token.token_type == TokenType.CONTROL_FLOW:
    #             if token.value == "if":
    #                 i, condition, statements = self.parse_control_flow(i, tokens)
    #                 last = Conditional(condition, statements)
    #                 parsed.append(last)
    #                 while i < len(tokens) and tokens[i].value in ("elif", "else"):
    #                     is_else = tokens[i].value == "else"
    #                     i, condition, statements = self.parse_control_flow(i, tokens, not is_else)
    #                     current = Conditional(condition, statements)
    #                     last.next_node = current
    #                     last = current
    #                     if is_else:
    #                         break
    #             elif token.value == "while":
    #                 i, condition, statements = self.parse_control_flow(i, tokens)
    #                 parsed.append(While(condition, statements))
    #         else:
    #             buffer.append(token)
    #             i += 1
    #     return parsed
    #
    # def parse_control_flow(self, i, tokens, has_expression=True):
    #     i += 1
    #     if has_expression:
    #         expression_len, expression = read_until_balanced(tokens[i:], "(", ")")
    #         expression = self.parse_expr(expression)
    #         i += expression_len
    #     else:
    #         expression = ObjectLookup("true")
    #     block_len, statements = read_until_balanced(tokens[i:], "{", "}")
    #     i += block_len
    #     return i, expression, self.parse(statements)
    #
    # def parse_statement(self, statement):
    #     """
    #     :param statement: tuple of Token objects to be parsed into Expression nodes
    #     :return: appropriate AST_Node object
    #     """
    #     for i, token in enumerate(statement):
    #         if token.token_type == TokenType.SYMBOL:
    #             if token.value == "=":
    #                 return Assignment(
    #                     statement[i - 1].value,
    #                     self.parse_expr(statement[i + 1:])
    #                 )
    #             elif re.match(".*=", token.value):
    #                 identifier = statement[i - 1].value
    #                 return Assignment(
    #                     identifier,
    #                     BinaryOperator(
    #                         binary_operators[token.value[:-1]],
    #                         ObjectLookup(identifier),
    #                         self.parse_expr(statement[i + 1:])
    #                     )
    #                 )
    #
    #         elif token.value == "print":
    #             return Output(
    #                 self.parse_expr(statement[i + 1:])
    #             )
    #
    # def parse_expr(self, expr):
    #     expr = tuple(self.parse_values(expr))
    #     return self.combine(expr)
    #
    # def parse_values(self, expr):
    #     """
    #     :param expr: tuple of Token objects
    #     :yield: stream of tokens with primitives parsed as nodes
    #     """
    #     for token in expr:
    #         if token.token_type == TokenType.VALUE:
    #             Node = token.node_type
    #             yield Node(Node.cast(token.value))
    #         elif token.token_type == TokenType.IDENTIFIER:
    #             yield ObjectLookup(token.value)
    #         else:
    #             yield token
    #
    # def combine(self, expr):
    #     """
    #     :param expr: tuple of Token objects to be parsed into Expression nodes
    #     :return: appropriate Expression node
    #     """
    #     expr = tuple(self.combine_parenthesis(expr))
    #     for operators in operator_precedence:
    #         expr = tuple(self.combine_binary_operators(expr, operators))
    #     return expr[0]
    #
    # def combine_parenthesis(self, expr):
    #     """
    #     :param expr: tuple of Token objects
    #     :yield: stream of tokens with parenthesized expressions parsed as nodes
    #     """
    #     i = 0
    #     while i < len(expr):
    #         token = expr[i]
    #         if isinstance(token, Token) and token.value == "(":
    #             length, sub = read_until_balanced(expr[i:], "(", ")")
    #             i += length
    #             yield self.combine(sub)
    #         else:
    #             yield token
    #         i += 1
    #
    # def combine_binary_operators(self, expr, operators):
    #     """
    #     :param expr: tuple of Token objects
    #     :param operators: operators to be combined
    #     :yield: stream of tokens with binary operators and adjacent tokens parsed as nodes
    #     """
    #     i = 0
    #     while i < len(expr) - 2:
    #         left, middle, right = expr[i: i + 3]
    #         if isinstance(middle, Token) and middle.value in operators:
    #             combined = (
    #                 BinaryOperator(binary_operators[middle.value], left, right),
    #                 *expr[i + 3:]
    #             )
    #             yield from self.combine_binary_operators(combined, operators)
    #             break
    #         else:
    #             yield left
    #             i += 1
    #     else:
    #         for token in expr[i:]:
    #             yield token
