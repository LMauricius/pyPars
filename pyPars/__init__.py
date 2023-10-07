"""
A simple recursive-descent parser that is easy to define.
Currently, only string parsing is supported
"""
from .text import Text, NatT, PosT, PatternT, MatchT
from .syntax_object import SyntaxObject
from .rules import (
    Opt,
    OneOrMore,
    ZeroOrMore,
    Attr,
    atr,
    SelectionFirst,
    SelectionShortest,
    SelectionLongest,
    GrammarClass,
    GrammarRule,
)
from dataclasses import dataclass
import forward_decl as fw

@dataclass
class LeftRecursiveIterationContext:
    position: PosT

class LeftRecursionException(Exception):
    def __init__(self) -> None:
        super().__init__()

def parseLeftRecursive(
    mytext: Text[NatT, PosT, PatternT, MatchT],
    pos: PosT,
    rule: GrammarRule,
    ruleId2recursionContext: dict[int, LeftRecursiveIterationContext],
    attrStore: SyntaxObject | None = None
) -> PosT | None:
    PosT = mytext.GetPositionType()
    NatT = mytext.GetNativeType()
    PatternT = mytext.GetPatternType()
    MatchT = mytext.GetMatchType()

    """
    Returns the end position of the successful match or None if it failed
    """
    if rule is None:
        return pos
    elif isinstance(rule, fw.OpaqueFwRef):
        return parseLeftRecursive(mytext, pos, rule.get_ref(), ruleId2recursionContext, attrStore)
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
        if len(rule) > 1:
            pos = parseLeftRecursive(mytext, pos, rule[0], ruleId2recursionContext, attrStore)
            if pos is None:
                return None
        for rulepart in rule[1:]:
            pos = parseLeftRecursive(mytext, pos, rulepart, {}, attrStore)
            if pos is None:
                return None
        return pos
    elif isinstance(rule, SelectionShortest):
        minpos = None
        multiAttrStores: list[SyntaxObject] = []

        for ruleoption in rule.options:
            tempAttrStore = SyntaxObject(set())
            newpos = parseLeftRecursive(mytext, pos, ruleoption, tempAttrStore)
            if newpos is not None and (minpos is None or newpos <= minpos):
                if minpos is None or newpos < minpos:
                    minpos = newpos
                    multiAttrStores = []
                multiAttrStores.append(tempAttrStore)

        if attrStore is not None and len(multiAttrStores) > 0:
            attrStore.extendOptions(multiAttrStores)
        return minpos
    elif isinstance(rule, SelectionFirst) or isinstance(rule, SelectionLongest):
        # ensure we first check if non-left-recursive options can be accepted

        # check if we already visited this rule at this position in text
        if id(rule) in ruleId2recursionContext:
            if ruleId2recursionContext[id(rule)] is None:
                raise LeftRecursionException()
            else:
                return ruleId2recursionContext[id(rule)].position
        else:
            # Infinitely recursively generated syntax trees are impossible,
            # so assume parsing will fail on such an option
            ruleId2recursionContext[id(rule)] = None

        if isinstance(rule, SelectionFirst):

            # holds rules that have higher priority than the currently accepted one,
            # but could not be accepted yet as they might rely on lower priority selections
            # to be accepted further down the recursion
            higherPriorityRecursions = []

            tryRecursions = False

            # first check non-left-recursive options
            for ruleoption in rule.options:
                tempAttrStore = SyntaxObject(set())
                try:
                    newpos = parseLeftRecursive(mytext, pos, ruleoption, tempAttrStore)
                except LeftRecursionException as e:
                    higherPriorityRecursions.append(ruleoption)
                    tryRecursions = True

                if newpos is not None:
                    ruleId2recursionContext[id(rule)] = LeftRecursiveIterationContext(newpos)
                    if attrStore is not None:
                        attrStore.extend(tempAttrStore)
                    break

            # now keep checking while we can extend current node by deepening the recursion
            while tryRecursions:
                tryRecursions = False
                maxIndexReached = 0
                for ruleoption in higherPriorityRecursions:
                    tempAttrStore = SyntaxObject(set())
                    newpos = parseLeftRecursive(mytext, pos, ruleoption, tempAttrStore)

                    if newpos is not None:
                        tryRecursions = True
                        ruleId2recursionContext[id(rule)] = LeftRecursiveIterationContext(newpos)
                        if attrStore is not None:
                            attrStore.extend(tempAttrStore)
                        break
                    maxIndexReached += 1
                higherPriorityRecursions = higherPriorityRecursions[0:maxIndexReached+1]
            
            return ruleId2recursionContext[id(rule)].position
        elif isinstance(rule, SelectionLongest):
            maxpos = None
            multiAttrStores: list[SyntaxObject] = []

            for ruleoption in rule.options:
                tempAttrStore = SyntaxObject(set())
                newpos = parseLeftRecursive(mytext, pos, ruleoption, tempAttrStore)
                if newpos is not None and (maxpos is None or newpos >= maxpos):
                    if maxpos is None or newpos > maxpos:
                        maxpos = newpos
                        multiAttrStores = []
                    multiAttrStores.append(tempAttrStore)

            if attrStore is not None and len(multiAttrStores) > 0:
                attrStore.extendOptions(multiAttrStores)
            return maxpos
    elif isinstance(rule, Opt) or isinstance(rule, list):
        if isinstance(rule, Opt):
            nonOptRule = rule.rule
        else:
            nonOptRule = tuple(rule)
        tempAttrStore = SyntaxObject(set())
        pos = parseLeftRecursive(mytext, pos, nonOptRule, ruleId2recursionContext, tempAttrStore)

        if pos is not None:
            if attrStore is not None:
                attrStore.extend(tempAttrStore)
            return pos
        else:
            return 0
    elif isinstance(rule, OneOrMore):
        tempAttrStore = SyntaxObject(set())
        pos = parseLeftRecursive(mytext, pos, rule.rule, ruleId2recursionContext, tempAttrStore)

        # first must match
        if pos is None:
            return None

        # others are optional
        while pos is not None:
            # store previous attributes
            if attrStore is not None:
                attrStore.extend(tempAttrStore)

            # try new rule instance
            tempAttrStore = SyntaxObject(set())
            pos = parseLeftRecursive(mytext, pos, rule.rule, set(), tempAttrStore)
    elif isinstance(rule, ZeroOrMore):
        tempAttrStore = SyntaxObject(set())
        pos = parseLeftRecursive(mytext, pos, rule.rule, ruleId2recursionContext, tempAttrStore)

        while pos is not None:
            # store previous attributes
            if attrStore is not None:
                attrStore.extend(tempAttrStore)

            # try new rule instance
            tempAttrStore = SyntaxObject(set())
            pos = parseLeftRecursive(mytext, pos, rule.rule, set(), tempAttrStore)
    elif isinstance(rule, Attr):

        if isinstance(rule.attrClasses, SelectionFirst) and all(
            isinstance(cls, GrammarClass) for cls in rule.attrClasses.options
        ):
            optionsrule = rule.attrClasses
        elif isinstance(rule.attrClasses, GrammarClass):
            optionsrule = SelectionFirst([rule.attrClasses])
        else:
            raise ValueError(
                f"An attribute rule's attrClasses must be of GrammarClass or SelectionFirst[GrammarClass] type."
            )

        for attrClass in optionsrule.options:
            subAttrStore: SyntaxObject = attrClass()
            subAttrStore.span = (pos, -1)

            newpos = parseLeftRecursive(mytext, pos, attrClass.grammar, ruleId2recursionContext, subAttrStore)

            if newpos is not None:
                subAttrStore.span = (subAttrStore.span[0], newpos)

                if rule.name in attrStore.grammarAttributeNames:
                    grammarAttr: list = getattr(attrStore, rule.name)
                else:
                    grammarAttr = []
                    attrStore.grammarAttributeNames.add(rule.name)
                    setattr(attrStore, rule.name, grammarAttr)
                grammarAttr.append(subAttrStore)

                return newpos
        return None
    elif isinstance(rule, GrammarClass):
        return parseLeftRecursive(mytext, pos, rule.grammar, ruleId2recursionContext, attrStore)
    else:
        raise ValueError(f"The rule argument is not of a GrammarRule type")



def parse(
    mytext: Text[NatT, PosT, PatternT, MatchT],
    pos: PosT,
    rule: GrammarRule,
    attrStore: SyntaxObject | None = None
) -> PosT | None:
    return parseLeftRecursive(
        mytext,
        pos,
        rule,
        {},
        attrStore
    )