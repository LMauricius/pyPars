
from typing import Union, TypeVar

# Generic type placeholder
PosT = TypeVar('PosT')
NatT = TypeVar('NatT')
PatternT = TypeVar('PatternT')
MatchT = TypeVar('MatchT')

class Text:
    
    def GetPositionType(self) -> type[PosT]:
        '''
        Returns the type for positions used to match in the instances of this class
        '''
        raise NotImplementedError()
    
    def GetNativeType(self) -> type[NatT]:
        '''
        Returns the type that is returned when sliced
        '''
        raise NotImplementedError()
    
    def GetPatternType(self) -> type[PatternT]:
        '''
        Returns the type that can be used as a matchedby() argument
        '''
        raise NotImplementedError()
    
    def GetMatchType(self) -> type[MatchT]:
        '''
        Returns the type that is returned by the matchedby() method
        It must have a span attribute that is a tuple of (PosT, PosT)
        '''
        raise NotImplementedError()
    
    def getStartPos(self) -> PosT:
        '''
        Returns the first pos
        '''
        raise NotImplementedError()
    
    def __getitem__(self, pos: PosT | slice) -> NatT:
        '''
        Returns the native type between two positions
        '''
        raise NotImplementedError()

    def startswith(self, prefix: NatT, pos: PosT) -> MatchT | None:
        raise NotImplementedError()

    def matchedby(self, pattern: PatternT, pos: PosT) -> MatchT | None:
        raise NotImplementedError()