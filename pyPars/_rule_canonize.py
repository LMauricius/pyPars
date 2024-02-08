from ._rules import *
from typing import Callable


def tryCanonizeConcat(rule: GrammarRule) -> Concat | None:
    if isinstance(rule, Concat):
        return rule
    elif isinstance(rule, tuple):
        return Concat(rule)
    else:
        return None


def tryCanonizeOpt(rule: GrammarRule) -> Opt | None:
    if isinstance(rule, Opt):
        return rule
    elif isinstance(rule, list):
        if len(rule) == 1:
            return Opt(rule[0])
        else:
            return Opt(Concat(rule))
    else:
        return None


def tryCanonizeOneOrMore(rule: GrammarRule) -> OneOrMore | None:
    if isinstance(rule, OneOrMore):
        return rule
    else:
        return None


def tryCanonizeZeroOrMore(rule: GrammarRule) -> ZeroOrMore | None:
    if isinstance(rule, ZeroOrMore):
        return rule
    else:
        return None


def tryCanonizeAttr(rule: GrammarRule) -> Attr | None:
    if isinstance(rule, Attr):
        return rule
    elif isinstance(rule, dict):
        assert (
            len(rule.items()) == 1
        ), "When represented as a dict, Attr must have a single key-value pair"
        return Attr(rule.keys()[0], rule.values()[0])
    else:
        return None


def tryCanonizeSelectionFirst(rule: GrammarRule) -> SelectionFirst | None:
    if isinstance(rule, SelectionFirst):
        return rule
    else:
        return None


def tryCanonizeSelection(rule: GrammarRule) -> Selection | None:
    if isinstance(rule, Selection):
        return rule
    else:
        return None


def tryCanonizeGrammarClass(rule: GrammarRule) -> GrammarClass | None:
    if isinstance(rule, GrammarClass):
        return rule
    else:
        return None


def tryCanonize(rule: GrammarRule) -> CanonGrammarRule:
    r = tryCanonizeConcat(rule)
    if r is not None:
        return r
    r = tryCanonizeOpt(rule)
    if r is not None:
        return r
    r = tryCanonizeOneOrMore(rule)
    if r is not None:
        return r
    r = tryCanonizeZeroOrMore(rule)
    if r is not None:
        return r
    r = tryCanonizeAttr(rule)
    if r is not None:
        return r
    r = tryCanonizeSelectionFirst(rule)
    if r is not None:
        return r
    r = tryCanonizeSelection(rule)
    if r is not None:
        return r
    r = tryCanonizeGrammarClass(rule)
    if r is not None:
        return r

    return rule  # native type or pattern
