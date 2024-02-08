from pyPars import *
from pyPars import _
from pyPars.text.string import *
from pyPars.so_modifiers import *
import json


class WS(SyntaxObject, metaclass=GrammarClass):
    grammar = re.compile("[ \t]*")


class NL(SyntaxObject, metaclass=GrammarClass):
    grammar = re.compile("\n")


class Num(SyntaxObject, TextSaver, metaclass=GrammarClass):
    grammar = re.compile("[1-9][0-9]*")


class Id(SyntaxObject, TextSaver, metaclass=GrammarClass):
    grammar = re.compile("[a-zA-Z_][0-9a-zA-Z_]*")


class Literal(SyntaxObject, SelfReplacable, metaclass=GrammarClass):
    grammar = {"self": Id / Num}


class Expression(SyntaxObject, SelfReplacable, metaclass=GrammarClass):
    grammar = None  # to be set later


Expression.grammar = (
    SelectionFirst()
    / ({"left": Expression}, WS, SelectionFirst("+", "-"), WS, {"right": Expression})
    / ({"left": Expression}, WS, SelectionFirst("*", "/"), WS, {"right": Expression})
    / {"self": Literal}
)


class Assignment(SyntaxObject, metaclass=GrammarClass):
    grammar = atr("assignee")(Id), WS, "=", WS, atr("value")(Expression)


class Program(SyntaxObject, metaclass=GrammarClass):
    grammar = ({"stat": Assignment} / NL) * K


progInput = """
a = 1
b = 2
c = a + b


d = c + a + b



"""

prog = Program()
pos = parse(StringText(progInput), 0, Program, prog)
print(json.dumps(prog.__dict__(), indent=4, default=lambda o: o.__dict__()))
