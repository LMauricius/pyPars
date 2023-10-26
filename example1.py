from pyPars import *
from pyPars.text.string import *
import json

class WS(SyntaxObject, metaclass = GrammarClass):
    grammar = re.compile("[ \t]*")

class NL(SyntaxObject, metaclass = GrammarClass):
    grammar = re.compile("\n")

class Num(SyntaxObject, metaclass = GrammarClass):
    grammar = re.compile("[1-9][0-9]*")

class Id(SyntaxObject, metaclass = GrammarClass):
    grammar = re.compile("[a-zA-Z_][0-9a-zA-Z_]*")

Expression = fw.FwDecl()
class Expression(SyntaxObject, metaclass = GrammarClass):
    grammar \
        = Id \
        / Num \
        / (atr('left')("Expression"), WS, SelectionFirst('+', '-'), WS, atr('right')("Expression"))

class Assignment(SyntaxObject, metaclass = GrammarClass):
    grammar = atr('assignee')(Id), WS, '=', WS, atr('value')(Expression)

class Program(SyntaxObject, metaclass = GrammarClass):
    grammar =  ZeroOrMore(Attr('stat', Assignment)/NL)


progInput = '''
a = 1
b = 2
c = a + b


d = c + a + b



'''

prog = Program()
pos = parse(StringText(progInput), 0, Program, prog)
prog.so_span = (prog.so_span[0], pos)
print(json.dumps(prog.__dict__(), indent=4))