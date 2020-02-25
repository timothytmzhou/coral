from lexer import Lexer
from parser import Parser

with open("test.coral") as f:
    source = f.read()
lexer = Lexer(source)
parser = Parser(lexer.tokenize(), "test")
parser.head.walk()
