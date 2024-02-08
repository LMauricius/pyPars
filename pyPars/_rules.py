from dataclasses import dataclass, field
from typing import Union, Callable, Iterable
from .text import Text, NatT, PosT, PatternT, MatchT
from ._syntax_object import SyntaxObject


@dataclass
class Concat:
    items: Iterable["GrammarRule"]


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
    def __init__(self, name: str, attrClasses: "GrammarClass|SelectionFirst") -> None:
        self.name = name
        if isinstance(attrClasses, SelectionFirst):
            self.attrClasses = attrClasses
        else:
            self.attrClasses = SelectionFirst(attrClasses)

    def __repr__(self) -> str:
        classNames = "/".join(
            [repr(attrClass) for attrClass in self.attrClasses.options]
        )
        return f"'{{{self.name}':{classNames}}}"


class SelectionFirst:
    def __init__(self, *options: "GrammarRule|SelectionFirst") -> None:
        self.options = [
            opt
            for options in [
                opt.options if isinstance(opt, SelectionFirst) else [opt]
                for opt in options
            ]
            for opt in options
        ]

    def __truediv__(self, right: "GrammarRule"):
        if isinstance(right, SelectionFirst):
            return SelectionFirst(*(self.options + right.options))
        else:
            return SelectionFirst(*(self.options + [right]))

    def __rtruediv__(self, left: "GrammarRule"):
        if isinstance(left, SelectionFirst):
            return SelectionFirst(*(left.options + self.options))
        else:
            return SelectionFirst(*([left] + self.options))

    def __repr__(self) -> str:
        return "/".join([repr(opt) for opt in self.options])


class Selection:
    def __init__(self, *options: "GrammarRule|Selection") -> None:
        self.options = [
            opt
            for options in [
                opt.options if isinstance(opt, Selection) else [opt]
                for opt in options
            ]
            for opt in options
        ]

    def __or__(self, right: "GrammarRule"):
        if isinstance(right, Selection):
            return Selection(*(self.options + right.options))
        else:
            return Selection(*(self.options + [right]))

    def __ror__(self, left: "GrammarRule"):
        if isinstance(left, Selection):
            return Selection(*(left.options + self.options))
        else:
            return Selection(*([left] + self.options))

    def __repr__(self) -> str:
        return "|".join([repr(opt) for opt in self.options])


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
            return SelectionFirst(*([cls] + right.options))
        else:
            return SelectionFirst(*[cls, right])

    def __rtruediv__(cls, left: "GrammarRule"):
        if isinstance(left, SelectionFirst):
            return SelectionFirst(*(left.options + [cls]))
        else:
            return SelectionFirst(*[left, cls])

    def __or__(cls, right: "GrammarRule"):
        if isinstance(right, Selection):
            return Selection(*([cls] + right.options))
        else:
            return Selection(*[cls, right])

    def __ror__(cls, left: "GrammarRule"):
        if isinstance(left, Selection):
            return Selection(*(left.options + [cls]))
        else:
            return Selection(*[left, cls])

    def __repr__(self) -> str:
        return self.__name__


CanonGrammarRule = Union[
    NatT,
    PatternT,
    Concat,  # For concatenation
    Opt,  # ? operator
    OneOrMore,  # + operator
    ZeroOrMore,  # * operator
    Attr,  # For named attributes
    SelectionFirst,  # For multiple options (Union of grammars)
    Selection,  # For multiple options (Union of grammars)
    GrammarClass,  # Class containing a 'grammar' class variable
]


GrammarRule = (
    CanonGrammarRule
    | tuple["GrammarRule"]
    | list["GrammarRule"]
    | dict[str, "GrammarClass|SelectionFirst"]
)
