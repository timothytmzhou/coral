from lexer import Lexer
from parser import Parser
from namespace import *


lexer = Lexer(input())
parser = Parser(lexer.tokenize(), "test")
parser.head.walk()
