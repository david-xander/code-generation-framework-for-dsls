import sys
from antlr4 import *
from antlr4.InputStream import InputStream

from OCLLexer import OCLLexer as OCLLexer
from OCLParser import OCLParser as OCLParser


if __name__ == '__main__':
    if len(sys.argv) > 1:
        input_stream = FileStream(sys.argv[1])
    else:
        input_stream = FileStream("t.expr")

    lexer = OCLLexer(input_stream)
    token_stream = CommonTokenStream(lexer)
    parser = OCLParser(token_stream)
    tree = parser.multipleContextSpecifications()
    