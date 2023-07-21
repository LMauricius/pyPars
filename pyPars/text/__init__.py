
from typing import TypeVar, Generic, Type, get_args, get_origin

# Generic type placeholder
#: The position type for parsing
PosT = TypeVar('PosT')
#: The native type for grammar
NatT = TypeVar('NatT')
#: The pattern type for grammar
PatternT = TypeVar('PatternT')
#: The match result type for parsing
MatchT = TypeVar('MatchT')

class Text(Generic[PosT, NatT, PatternT, MatchT]):
    @classmethod
    def GetTextSpecialization(cls) -> "Text[Type[PosT], Type[NatT], Type[PatternT], Type[MatchT]]":
        for base in cls.__orig_bases__:
            origin = get_origin(base)
            if origin is not None and issubclass(origin, Text):
                return base

    @classmethod
    def GetPositionType(cls) -> Type[PosT]:
        '''
        Returns the type for positions used to match in the instances of this class
        '''
        return get_args(cls.GetTextSpecialization())[0]
    
    @classmethod
    def GetNativeType(cls) -> Type[NatT]:
        '''
        Returns the type that is returned when sliced
        '''
        return get_args(cls.GetTextSpecialization())[1]
    
    @classmethod
    def GetPatternType(cls) -> Type[PatternT]:
        '''
        Returns the type that can be used as a matchedby() argument
        '''
        return get_args(cls.GetTextSpecialization())[2]
    
    @classmethod
    def GetMatchType(cls) -> Type[MatchT]:
        '''
        Returns the type that is returned by the matchedby() method
        It must have a span attribute that is a tuple of (PosT, PosT)
        '''
        return get_args(cls.GetTextSpecialization())[3]
    
    
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