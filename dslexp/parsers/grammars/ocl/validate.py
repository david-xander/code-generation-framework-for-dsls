import sys
from antlr4 import *
from antlr4 import InputStream
from antlr4.error.ErrorListener import ErrorListener

from .OCLLexer import OCLLexer as Lexer
from .OCLParser import OCLParser as Parser


class Validation():
    def __init__(self):
        pass
    def validate(self, input_string)->int:
        try:
            input_stream = InputStream(input_string)
            lexer = Lexer(input_stream)
            token_stream = CommonTokenStream(lexer)
            try:
                parser = Parser(token_stream)
                parser.removeErrorListeners()
                parser.addErrorListener( MyErrorListener() )
                tree = parser.multipleContextSpecifications() 
                return {"result": 1, "desc": "OK"}
            except Exception as e:
                return {"result": -2, "desc": str(e)}
        except Exception as e:
            return {"result": -1, "desc": str(e)}
    

class MyErrorListener( ErrorListener ):

    def __init__(self):
        super(MyErrorListener, self).__init__()

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        raise Exception({line, column, msg})

# cosa = OCLValidation()
# print(cosa.validate("context MyContext inv: history->last().bindings->any(p | name = n).value"))
