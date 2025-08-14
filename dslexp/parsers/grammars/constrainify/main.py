import sys
from antlr4 import *
from antlr4.InputStream import InputStream

from ConstrainifyLexer import ConstrainifyLexer
from ConstrainifyParser import ConstrainifyParser


if __name__ == '__main__':
    if len(sys.argv) > 1:
        input_stream = FileStream(sys.argv[1])
    else:
        input_stream = FileStream("t.expr")

    lexer = ConstrainifyLexer(input_stream)
    token_stream = CommonTokenStream(lexer)
    parser = ConstrainifyParser(token_stream)
    tree = parser.program()
    