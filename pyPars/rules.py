from dataclasses import dataclass, field
from typing import Union, Callable
from .text import Text, NatT, PosT, PatternT, MatchT
from .syntax_object import SyntaxObject


@dataclass
class Opt:
    rule: "GrammarRule"


@dataclass
class OneOrMore:
    rule: "GrammarRule"


@dataclass
class ZeroOrMore:
    rule: "GrammarRule"


@dataclass
class Attr:
    name: str
    attrClasses: "GrammarClass|SelectionFirst"

def atr(name: str) -> Callable[["GrammarClass|SelectionFirst"], Attr]:
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

    def __or__(self, right: "GrammarRule"):
        if isinstance(right, SelectionFirst):
            return SelectionFirst(self.options + right.options)
        else:
            return SelectionFirst(self.options + [right])

    def __ror__(self, left: "GrammarRule"):
        if isinstance(left, SelectionFirst):
            return SelectionFirst(left.options + self.options)
        else:
            return SelectionFirst([left] + self.options)


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

    def __or__(cls, right: "GrammarRule"):
        if isinstance(right, SelectionFirst):
            return SelectionFirst([cls] + right.options)
        else:
            return SelectionFirst([cls, right])

    def __ror__(cls, left: "GrammarRule"):
        if isinstance(left, SelectionFirst):
            return SelectionFirst(left.options + [cls])
        else:
            return SelectionFirst([left, cls])


AttributeClass = Union[
    "GrammarClass", list["GrammarClass"], Union["GrammarClass", "GrammarClass"]
]

GrammarRule = Union[
    None,
    NatT,
    PatternT,
    tuple["GrammarRule"],  # For concatenation
    SelectionFirst,  # For multiple options (Union of grammars)
    Opt,  # ? operator
    list["GrammarRule"],  # Also ? operator
    OneOrMore,  # + operator
    ZeroOrMore,  # * operator
    Attr,  # For named attributes
    GrammarClass,  # Class containing a 'grammar' class variable
]
