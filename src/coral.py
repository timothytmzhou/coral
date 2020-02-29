from lexer import Lexer
from parser import Parser


def run(file="test.coral"):
    with open(file) as f:
        source = f.read()
    lexer = Lexer(source)
    parser = Parser(lexer.tokenize())
    parser.head.walk()


if __name__ == "__main__":
    run()
