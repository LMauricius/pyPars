'''
A simple recursive-descent parser that is easy to define.
Currently, only string parsing is supported
'''

import re
from dataclasses import dataclass, field
from typing import Union
from abc import ABCMeta, abstractmethod

from . import text

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
    attrClasses: Union["GrammarClass", list["GrammarClass"], Union["GrammarClass","GrammarClass"]]

class Selection:
    def __init__(self, options: list["GrammarRule"] = []) -> None:
        self.options = options

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

'''
A metaclass for Grammar types
'''
class GrammarClass(type[SyntaxObject]):
    def __new__(cls, name, bases, attrs):
        if not any(issubclass(base, SyntaxObject) for base in bases):
            raise TypeError(f"Class '{name}' is not a subclass of 'AttributeStorage'")
        return super().__new__(cls, name, bases, attrs)
    
    def __init__(cls, name, bases, dict):
        r = super().__init__(name, bases, dict)
        if not hasattr(cls, 'grammar'):
            raise NotImplementedError(f"Class '{name}' doesn't have a 'grammar' class variable set")
        grammar: GrammarRule
        return r

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


GrammarRule = Union[
    None,
    text.NatT,
    text.PatternT,
    tuple["GrammarRule"], # For concatenation
    list["GrammarRule"], # For multiple options
    Selection, # Also for multiple options (Union of grammars)
    Opt, # ? operator
    OneOrMore, # + operator
    ZeroOrMore, # * operator
    Attr, # For named attributes
    dict[str, Union["GrammarClass", list["GrammarClass"]]], # Also for named attributes (dict with a single key)
    GrammarClass # Class containing a 'grammar' class variable
]
    

def parse(mytext: text.Text, pos: text.PosT, rule: GrammarRule, attrStore: SyntaxObject | None = None) -> text.PosT | None:
    PosT = mytext.GetPositionType()
    NatT = mytext.GetNativeType()
    PatternT = mytext.GetPatternType()
    MatchT = mytext.GetMatchType()

    '''
    Returns the end position of the successful match or None if it failed
    '''
    if rule is None:
        return pos
    elif isinstance(rule, NatT):
        if mytext.startswith(rule, pos):
            return pos + len(rule)
        else:
            return None
    elif isinstance(rule, PatternT):
        m = mytext.matchedby(rule, pos)
        if m is None:
            return None
        else:
            return m.span[1]
    elif isinstance(rule, tuple):
        for rulepart in rule:
            pos = parse(mytext, pos, rulepart, attrStore)
            if pos is None:
                return None
        return pos
    elif isinstance(rule, list) or isinstance(rule, Selection):
        if isinstance(rule, list):
            optionsrule = Selection(rule)
        elif isinstance(rule, Selection):
            optionsrule = rule

        for ruleoption in optionsrule.options:
            tempAttrStore = SyntaxObject(set())
            newpos = parse(mytext, pos, ruleoption, tempAttrStore)

            if newpos is not None:
                if attrStore is not None:
                    extendAttributeStore(attrStore, tempAttrStore)
                return newpos
        return None
    elif isinstance(rule, Opt):
        tempAttrStore = SyntaxObject(set())
        pos = parse(mytext, pos, rule.rule, tempAttrStore)

        if pos is not None:
            if attrStore is not None: 
                extendAttributeStore(attrStore, tempAttrStore)
            return pos
        else:
            return 0
    elif isinstance(rule, OneOrMore):
        tempAttrStore = SyntaxObject(set())
        pos = parse(mytext, pos, rule.rule, tempAttrStore)

        # first must match
        if pos is None:
            return None
        
        # others are optional
        while pos is not None:
            # store previous attributes
            if attrStore is not None: 
                extendAttributeStore(attrStore, tempAttrStore)

            # try new rule instance
            tempAttrStore = SyntaxObject(set())
            pos = parse(mytext, pos, rule.rule, tempAttrStore)
    elif isinstance(rule, ZeroOrMore):
        tempAttrStore = SyntaxObject(set())
        pos = parse(mytext, pos, rule.rule, tempAttrStore)

        while pos is not None:
            # store previous attributes
            if attrStore is not None: 
                extendAttributeStore(attrStore, tempAttrStore)

            # try new rule instance
            tempAttrStore = SyntaxObject(set())
            pos = parse(mytext, pos, rule.rule, tempAttrStore)
    elif isinstance(rule, Attr) or isinstance(rule, dict):
        if isinstance(rule, Attr):
            grammarAttributeName = rule.name
            attrClasses = rule.attrClasses
        elif isinstance(rule, dict):
            grammarAttributeName: str = list(rule.keys())[0]
            attrClasses = rule[grammarAttributeName]

        if isinstance(attrClasses, list) and all(isinstance(cls, GrammarClass) for cls in attrClasses):
            optionsrule = Selection(attrClasses)
        elif isinstance(attrClasses, Selection) and all(isinstance(cls, GrammarClass) for cls in attrClasses.options):
            optionsrule = attrClasses
        elif isinstance(attrClasses, GrammarClass):
            optionsrule = Selection([attrClasses])
        else:
            raise ValueError(f"An attribute rule's attrClasses must be of GrammarClass, list[GrammarClass], or GrammarRuleSelection[GrammarClass] type.")

        for attrClass in optionsrule.options:
            subAttrStore: SyntaxObject = attrClass()
            subAttrStore.span = (pos, -1)
            
            newpos = parse(mytext, pos, attrClass.grammar, subAttrStore)

            if newpos is not None:
                subAttrStore.span = (subAttrStore.span[0], newpos)

                if grammarAttributeName in attrStore.grammarAttributeNames:
                    grammarAttr: list = getattr(attrStore, grammarAttributeName)
                else:
                    grammarAttr = []
                    attrStore.grammarAttributeNames.add(grammarAttributeName)
                    setattr(attrStore, grammarAttributeName, grammarAttr)
                grammarAttr.append(subAttrStore)

                return newpos
        return None
    elif isinstance(rule, GrammarClass):
        return parse(mytext, pos, rule.grammar, attrStore)
    else:
        raise ValueError(f"The rule argument is not of a GrammarRule type")