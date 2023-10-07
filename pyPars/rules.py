from dataclasses import dataclass, field
from typing import Union, Callable
from .text import Text, NatT, PosT, PatternT, MatchT
from .syntax_object import SyntaxObject

import forward_decl as fw


@dataclass
class Opt:
    rule: "GrammarRule"


@dataclass
class OneOrMore:
    rule: "GrammarRule"


@dataclass
class ZeroOrMore:
    rule: "GrammarRule"


class Attr:
    def __init__(self, name: str, attrClasses: "GrammarClass|SelectionFirst|str") -> None:
        self.name = name
        if isinstance(attrClasses, str):
            self.attrClasses = SelectionFirst(*[
                fw.OpaqueFwRef(id) for id in attrClasses.split('/')
            ])
        else:
            self.attrClasses = attrClasses

def atr(name: str) -> Callable[["GrammarClass|SelectionFirst|str"], Attr]:
    return lambda attrClasses: Attr(name, attrClasses)


class SelectionFirst:
    def __init__(self, option1: "GrammarRule|SelectionFirst", *otheroptions: "GrammarRule|SelectionFirst") -> None:
        self.options = (option1.options if isinstance(option1, SelectionFirst) else [option1]) + [
            opt 
            for options in [
                opt.options if isinstance(opt, SelectionFirst) else [opt] for opt in otheroptions
            ]
            for opt in options 
        ]

    def __truediv__(self, right: "GrammarRule"):
        if isinstance(right, SelectionFirst):
            return SelectionFirst(self.options + right.options)
        else:
            return SelectionFirst(self.options + [right])

    def __rtruediv__(self, left: "GrammarRule"):
        if isinstance(left, SelectionFirst):
            return SelectionFirst(left.options + self.options)
        else:
            return SelectionFirst([left] + self.options)

class SelectionShortest:
    def __init__(self, option1: "GrammarRule|SelectionShortest", *otheroptions: "GrammarRule|SelectionShortest") -> None:
        self.options = (option1.options if isinstance(option1, SelectionShortest) else [option1]) + [
            opt 
            for options in [
                opt.options if isinstance(opt, SelectionShortest) else [opt] for opt in otheroptions
            ]
            for opt in options 
        ]

    def __or__(self, right: "GrammarRule"):
        if isinstance(right, SelectionShortest):
            return SelectionShortest(self.options + right.options)
        else:
            return SelectionShortest(self.options + [right])

    def __ror__(self, left: "GrammarRule"):
        if isinstance(left, SelectionShortest):
            return SelectionShortest(left.options + self.options)
        else:
            return SelectionShortest([left] + self.options)

class SelectionLongest:
    def __init__(self, option1: "GrammarRule|SelectionLongest", *otheroptions: "GrammarRule|SelectionLongest") -> None:
        self.options = (option1.options if isinstance(option1, SelectionLongest) else [option1]) + [
            opt 
            for options in [
                opt.options if isinstance(opt, SelectionLongest) else [opt] for opt in otheroptions
            ]
            for opt in options 
        ]

    def __xor__(self, right: "GrammarRule"):
        if isinstance(right, SelectionLongest):
            return SelectionLongest(self.options + right.options)
        else:
            return SelectionLongest(self.options + [right])

    def __rxor__(self, left: "GrammarRule"):
        if isinstance(left, SelectionLongest):
            return SelectionLongest(left.options + self.options)
        else:
            return SelectionLongest([left] + self.options)


class GrammarClass(type[SyntaxObject]):
    """
    A metaclass for Grammar types
    """

    def __new__(cls, name, bases, attrs):
        if not any(issubclass(base, SyntaxObject) for base in bases):
            raise TypeError(f"Class '{name}' is not a subclass of 'AttributeStorage'")
        return super().__new__(cls, name, bases, attrs)

    def __init__(cls, name, bases, dict):
        super().__init__(name, bases, dict)
        if not hasattr(cls, "grammar"):
            raise NotImplementedError(
                f"Class '{name}' doesn't have a 'grammar' class variable set"
            )
        grammar: "GrammarRule"

    def __truediv__(cls, right: "GrammarRule"):
        if isinstance(right, SelectionFirst):
            return SelectionFirst([cls] + right.options)
        else:
            return SelectionFirst([cls, right])

    def __rtruediv__(cls, left: "GrammarRule"):
        if isinstance(left, SelectionFirst):
            return SelectionFirst(left.options + [cls])
        else:
            return SelectionFirst([left, cls])

    def __or__(cls, right: "GrammarRule"):
        if isinstance(right, SelectionShortest):
            return SelectionShortest([cls] + right.options)
        else:
            return SelectionShortest([cls, right])

    def __ror__(cls, left: "GrammarRule"):
        if isinstance(left, SelectionShortest):
            return SelectionShortest(left.options + [cls])
        else:
            return SelectionShortest([left, cls])

    def __xor__(cls, right: "GrammarRule"):
        if isinstance(right, SelectionLongest):
            return SelectionLongest([cls] + right.options)
        else:
            return SelectionLongest([cls, right])

    def __rxor__(cls, left: "GrammarRule"):
        if isinstance(left, SelectionLongest):
            return SelectionLongest(left.options + [cls])
        else:
            return SelectionLongest([left, cls])


AttributeClass = Union[
    "GrammarClass", list["GrammarClass"], Union["GrammarClass", "GrammarClass"]
]

GrammarRule = Union[
    None,
    NatT,
    PatternT,
    tuple["GrammarRule"],  # For concatenation
    SelectionFirst,  # For multiple options (Union of grammars)
    SelectionShortest,  # For multiple options (Union of grammars)
    SelectionLongest,  # For multiple options (Union of grammars)
    Opt,  # ? operator
    list["GrammarRule"],  # Also ? operator
    OneOrMore,  # + operator
    ZeroOrMore,  # * operator
    Attr,  # For named attributes
    GrammarClass,  # Class containing a 'grammar' class variable
    fw.OpaqueFwRef, # A forward reference to a rule
]
