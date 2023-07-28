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

class Operation(SyntaxObject, metaclass = GrammarClass):
    grammar = atr('left')(Id|Num), WS, Selection('+', '-'), WS, atr('right')(Id|Num)

class Assignment(SyntaxObject, metaclass = GrammarClass):
    grammar = atr('left')(Id), WS, '=', WS, atr('expression')(Id|Num|Operation)

class Program(SyntaxObject, metaclass = GrammarClass):
    grammar =  ZeroOrMore((Attr('stat', Assignment), NL))


progInput = '''
a = 1
b = 2

c = a + b


d = c



'''

prog = Program()
pos = parse(StringText(progInput), 0, Program.grammar, prog)
prog.span = (prog.span[0], pos)
print(json.dumps(prog.__dict__(), indent=4))