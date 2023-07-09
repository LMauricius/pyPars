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
    attrClasses: "GrammarClass|Selection"

def atr(name: str) -> Callable[["GrammarClass|Selection"], Attr]:
    return lambda attrClasses: Attr(name, attrClasses)


class Selection:
    def __init__(self, option1: "GrammarRule|Selection", *otheroptions: "GrammarRule|Selection") -> None:
        self.options = (option1.options if isinstance(option1, Selection) else [option1]) + [
            opt 
            for options in [
                opt.options if isinstance(opt, Selection) else [opt] for opt in otheroptions
            ]
            for opt in options 
        ]

    def __or__(self, right: "GrammarRule"):
        if isinstance(right, Selection):
            return Selection(self.options + right.options)
        else:
            return Selection(self.options + [right])

    def __ror__(self, left: "GrammarRule"):
        if isinstance(left, Selection):
            return Selection(left.options + self.options)
        else:
            return Selection([left] + self.options)


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
        if isinstance(right, Selection):
            return Selection([cls] + right.options)
        else:
            return Selection([cls, right])

    def __ror__(cls, left: "GrammarRule"):
        if isinstance(left, Selection):
            return Selection(left.options + [cls])
        else:
            return Selection([left, cls])


AttributeClass = Union[
    "GrammarClass", list["GrammarClass"], Union["GrammarClass", "GrammarClass"]
]

GrammarRule = Union[
    None,
    NatT,
    PatternT,
    tuple["GrammarRule"],  # For concatenation
    Selection,  # For multiple options (Union of grammars)
    Opt,  # ? operator
    list["GrammarRule"],  # Also ? operator
    OneOrMore,  # + operator
    ZeroOrMore,  # * operator
    Attr,  # For named attributes
    GrammarClass,  # Class containing a 'grammar' class variable
]
