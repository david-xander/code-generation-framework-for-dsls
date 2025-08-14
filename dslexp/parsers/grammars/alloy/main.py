import sys
from antlr4 import *
from antlr4.InputStream import InputStream

from alloyLexer import alloyLexer
from alloyParser import alloyParser


if __name__ == '__main__':
    if len(sys.argv) > 1:
        input_stream = FileStream(sys.argv[1])
    else:
        input_stream = FileStream("t.expr")

    lexer = alloyLexer(input_stream)
    token_stream = CommonTokenStream(lexer)
    parser = alloyParser(token_stream)
    tree = parser.alloyModule()
    