from ._rules import *
from typing import Callable

class KleeneRightHandSideObject:
    '''
    Can be used as a right-hand placeholder operand of Kleene unary operations
    Can be used as <rule><operator><placeholder>
    For example, rule+K == OneOrMore(rule) and rule*K == ZeroOrMore(rule)
    '''

    def __radd__(self, rule: GrammarRule) -> GrammarRule:
        return OneOrMore(rule)
    
    def __rmul__(self, rule: GrammarRule) -> GrammarRule:
        return ZeroOrMore(rule)
    
K = KleeneRightHandSideObject()