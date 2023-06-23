from pyPars import *
from pyPars.text.string import *
import json

class WS(AttributeStorage, metaclass = GrammarClass):
    grammar = re.compile("[ \t]*")

class NL(AttributeStorage, metaclass = GrammarClass):
    grammar = re.compile("\n")

class Num(AttributeStorage, metaclass = GrammarClass):
    grammar = re.compile("[1-9][0-9]*")

class Id(AttributeStorage, metaclass = GrammarClass):
    grammar = re.compile("[a-zA-Z_][0-9a-zA-Z_]*")

class Operation(AttributeStorage, metaclass = GrammarClass):
    grammar = {'left':(Id|Num)}, WS, Selection(['+', '-']), WS, {'right':(Id | Num)}

class Assignment(AttributeStorage, metaclass = GrammarClass):
    grammar = {'left': Id}, WS, '=', WS, {'expression': (Id | Num | Operation)}

class Program(AttributeStorage, metaclass = GrammarClass):
    grammar =  ZeroOrMore([Attr('stat', Assignment), NL])


progInput = '''
a = 1
b = 2

c = a + b


d = c



'''

prog = Program()
pos = parse(StringText(progInput), 0, Program.grammar, prog)
prog.span = (prog.span[0], pos)
print(json.dumps(attributeStore2dict(prog), indent=4))