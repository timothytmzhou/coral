from lexer import Lexer
from parser import Parser


lexer = Lexer(input())
parser = Parser(lexer.tokenize(), "test")
parser.head.walk()
