from .text import Text, NatT, PosT, PatternT, MatchT
from ._syntax_object import SyntaxObject
from ._rules import (
    Concat,
    Opt,
    OneOrMore,
    ZeroOrMore,
    Attr,
    SelectionFirst,
    Selection,
    SelectionLongest,
    GrammarClass,
    GrammarRule,
    CanonGrammarRule,
)
from ._rule_canonize import tryCanonize
from . import so_modifiers as mod
from dataclasses import dataclass
import forward_decl as fw


@dataclass
class LeftRecursiveIterationContext:
    position: PosT
    attrStore: SyntaxObject | None


class LeftRecursionException(Exception):
    def __init__(self, grammar_cls: GrammarClass) -> None:
        super().__init__()
        self.grammar_cls = grammar_cls


@dataclass
class ParseState:
    position: PosT
    currentObject: SyntaxObject


def parseLeftRecursive(
    mytext: Text[NatT, PosT, PatternT, MatchT],
    startPos: PosT,
    currentRule: GrammarRule,
    ruleId2recursionContext: dict[int, LeftRecursiveIterationContext],
) -> list[ParseState]:
    """
    Returns the end position of the successful match or None if it failed
    """
    PosT = mytext.GetPositionType()
    NatT = mytext.GetNativeType()
    PatternT = mytext.GetPatternType()
    MatchT = mytext.GetMatchType()

    currentObject = SyntaxObject()

    currentRule = tryCanonize(currentRule)

    if isinstance(currentRule, NatT):
        if mytext.startswith(currentRule, startPos):
            return [ParseState(startPos + len(currentRule), currentObject)]
        else:
            return []
    elif isinstance(currentRule, PatternT):
        m = mytext.matchedby(currentRule, startPos)
        if m is None:
            return []
        else:
            return [(m.span[1], currentObject)]
    elif isinstance(currentRule, Concat):
        if len(currentRule) >= 1:
            newPos, newObject = parseLeftRecursive(
                mytext, startPos, currentRule[0], ruleId2recursionContext
            )
            if newPos is not None:
                currentObject.extend(newObject)
            else:
                return None
            for rulepart in currentRule[1:]:
                newPos = parseLeftRecursive(mytext, newPos, rulepart, {}, currentObject)
                if newPos is not None:
                    currentObject.extend(newObject)
                else:
                    return None
            return [(newPos, currentObject)]
        else:
            return [(startPos, currentObject)]
    elif isinstance(currentRule, Selection):
        minPos = None
        validOptions: list[SyntaxObject] = []

        for option in currentRule.options:
            tempObject = SyntaxObject(set())
            newPos = parseLeftRecursive(
                mytext, startPos, option, ruleId2recursionContext, tempObject
            )
            if newPos is not None:
                if minPos is None or newPos < minPos:
                    minPos = newPos
                    multiAttrStores = [tempObject]
                elif newPos == minPos:
                    multiAttrStores.append(tempObject)

        if len(validOptions) > 0:
            currentObject.extendOptions(validOptions)
            return minPos
    elif isinstance(currentRule, SelectionFirst) or isinstance(
        currentRule, SelectionLongest
    ):
        # ensure we first check if non-left-recursive options can be accepted

        # check if we already visited this rule at this position in text
        if id(currentRule) in ruleId2recursionContext:
            if ruleId2recursionContext[id(currentRule)] is None:
                raise LeftRecursionException(currentRule)
            else:
                if currentObject is not None:
                    currentObject.extend(
                        ruleId2recursionContext[id(currentRule)].attrStore
                    )
                return ruleId2recursionContext[id(currentRule)].position
        else:
            # Prepare for possible recursion later
            ruleId2recursionContext[id(currentRule)] = None

        if isinstance(currentRule, SelectionFirst):
            # holds rules that have higher priority than the currently accepted one,
            # but could not be accepted yet as they might rely on lower priority selections
            # to be accepted further down the recursion
            higherPriorityRecursions = []

            tryRecursions = False

            # first check non-left-recursive options
            for ruleoption in currentRule.options:
                tempObject = SyntaxObject(set())
                newPos = None
                try:
                    newPos = parseLeftRecursive(
                        mytext,
                        startPos,
                        ruleoption,
                        ruleId2recursionContext,
                        tempObject,
                    )
                except LeftRecursionException as e:
                    if e.grammar_cls is currentRule:
                        higherPriorityRecursions.append(ruleoption)
                        tryRecursions = True
                    else:
                        raise

                if newPos is not None:
                    ruleId2recursionContext[
                        id(currentRule)
                    ] = LeftRecursiveIterationContext(newPos, tempObject)
                    break

            if newPos is None:
                return None

            # now keep checking while we can extend current node by deepening the recursion
            oldpos = newPos
            while tryRecursions:
                tryRecursions = False
                indexReached = 0
                for indexReached, ruleoption in enumerate(higherPriorityRecursions):
                    tempObject = SyntaxObject(set())
                    newPos = parseLeftRecursive(
                        mytext,
                        startPos,
                        ruleoption,
                        ruleId2recursionContext,
                        tempObject,
                    )

                    if newPos is not None and newPos > oldpos:
                        tryRecursions = True
                        ruleId2recursionContext[
                            id(currentRule)
                        ] = LeftRecursiveIterationContext(newPos, tempObject)
                        oldpos = newPos
                        break
                higherPriorityRecursions = higherPriorityRecursions[
                    0 : indexReached + 1
                ]

            if currentObject is not None:
                currentObject.extend(ruleId2recursionContext[id(currentRule)].attrStore)
            return ruleId2recursionContext[id(currentRule)].position
        elif isinstance(currentRule, SelectionLongest):
            maxpos = None
            multiAttrStores: list[SyntaxObject] = []

            for ruleoption in currentRule.options:
                tempObject = SyntaxObject(set())
                newPos = parseLeftRecursive(
                    mytext, startPos, ruleoption, ruleId2recursionContext, tempObject
                )
                if newPos is not None and (maxpos is None or newPos >= maxpos):
                    if maxpos is None or newPos > maxpos:
                        maxpos = newPos
                        multiAttrStores = []
                    multiAttrStores.append(tempObject)

            if currentObject is not None and len(multiAttrStores) > 0:
                currentObject.extendOptions(multiAttrStores)
            return maxpos
    elif isinstance(currentRule, Opt) or isinstance(currentRule, list):
        if isinstance(currentRule, Opt):
            nonOptRule = currentRule.rule
        else:
            nonOptRule = tuple(currentRule)
        tempObject = SyntaxObject(set())
        newPos = parseLeftRecursive(
            mytext, startPos, nonOptRule, ruleId2recursionContext, tempObject
        )

        if newPos is not None:
            if currentObject is not None:
                currentObject.extend(tempObject)
            return newPos
        else:
            return startPos
    elif isinstance(currentRule, OneOrMore):
        tempObject = SyntaxObject(set())
        newPos = parseLeftRecursive(
            mytext, startPos, currentRule.rule, ruleId2recursionContext, tempObject
        )

        # first must match
        if newPos is None:
            return None

        # others are optional
        while newPos is not None:
            # store previous attributes
            if currentObject is not None:
                currentObject.extend(tempObject)
            startPos = newPos

            # try new rule instance
            tempObject = SyntaxObject(set())
            newPos = parseLeftRecursive(
                mytext, startPos, currentRule.rule, set(), tempObject
            )

        return startPos
    elif isinstance(currentRule, ZeroOrMore):
        tempObject = SyntaxObject(set())
        newPos = parseLeftRecursive(
            mytext, startPos, currentRule.rule, ruleId2recursionContext, tempObject
        )

        while newPos is not None:
            # store previous attributes
            if currentObject is not None:
                currentObject.extend(tempObject)
            startPos = newPos

            # try new rule instance
            tempObject = SyntaxObject(set())
            newPos = parseLeftRecursive(
                mytext, startPos, currentRule.rule, {}, tempObject
            )

        return startPos
    elif isinstance(currentRule, Attr):
        if isinstance(currentRule.attrClasses, SelectionFirst) and all(
            isinstance(cls, GrammarClass)
            or (
                isinstance(cls, fw.OpaqueFwRef)
                and isinstance(cls.get_ref(), GrammarClass)
            )
            for cls in currentRule.attrClasses.options
        ):
            optionsrule = currentRule.attrClasses
        elif isinstance(currentRule.attrClasses, GrammarClass) or (
            isinstance(currentRule.attrClasses, fw.OpaqueFwRef)
            and isinstance(currentRule.attrClasses.get_ref(), GrammarClass)
        ):
            optionsrule = SelectionFirst(currentRule.attrClasses)
        else:
            raise ValueError(
                f"An attribute rule's attrClasses must be of GrammarClass or SelectionFirst[GrammarClass] type."
            )

        for attrClass in optionsrule.options:
            if isinstance(attrClass, fw.OpaqueFwRef):
                attrClass = attrClass.get_ref()

            newSyntaxObject: SyntaxObject = attrClass()
            newSyntaxObjectSpan = (startPos, -1)

            newPos = parseLeftRecursive(
                mytext,
                startPos,
                attrClass.grammar,
                ruleId2recursionContext,
                newSyntaxObject,
            )

            if newPos is not None:
                newSyntaxObjectSpan = (newSyntaxObjectSpan[0], newPos)

                # Satisfy the TextSaver modifier
                if isinstance(newSyntaxObject, mod.TextSaver):
                    newSyntaxObject.so_savedText = mytext[
                        newSyntaxObjectSpan[0] : newSyntaxObjectSpan[1]
                    ]
                # Satisfy the SpanSaver modifier
                if isinstance(newSyntaxObject, mod.SpanSaver):
                    newSyntaxObject.so_span = newSyntaxObjectSpan
                # Satisfy the SelfReplacable modifier
                trySelfReplace = True
                newSyntaxObjectOptions = [newSyntaxObject]
                while trySelfReplace:
                    trySelfReplace = False
                    nextSyntaxObjectOptions = []
                    for opt in newSyntaxObjectOptions:
                        if (
                            isinstance(opt, mod.SelfReplacable)
                            and "self" in opt.so_grammarAttributeNames
                        ):
                            trySelfReplace = True
                            nextSyntaxObjectOptions.extend(opt.self)
                        else:
                            nextSyntaxObjectOptions.append(opt)
                    newSyntaxObjectOptions = nextSyntaxObjectOptions

                if currentRule.name in currentObject.so_grammarAttributeNames:
                    grammarAttrOptions: list = getattr(currentObject, currentRule.name)
                else:
                    grammarAttrOptions = []
                    currentObject.so_grammarAttributeNames.add(currentRule.name)
                    setattr(currentObject, currentRule.name, grammarAttrOptions)
                grammarAttrOptions.extend(newSyntaxObjectOptions)

                return newPos
        return None
    elif isinstance(currentRule, GrammarClass):
        return parseLeftRecursive(
            mytext,
            startPos,
            currentRule.grammar,
            ruleId2recursionContext,
            currentObject,
        )
    else:
        raise ValueError(f"The rule argument is not of a GrammarRule type")


def parse(
    mytext: Text[NatT, PosT, PatternT, MatchT],
    pos: PosT,
    rule: GrammarRule,
    attrStore: SyntaxObject | None = None,
) -> PosT | None:
    return parseLeftRecursive(mytext, pos, rule, {}, attrStore)
