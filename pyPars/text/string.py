import re
from dataclasses import dataclass
from ._abstract import Text

@dataclass
class StringMatch:
    span: tuple[int,int]

class StringText(Text[int, str, re.Pattern, re.Match]):

    def __init__(self, text: str) -> None:
        self.text = text
    
    def getStartPos(self) -> int:
        return 0
    
    def __getitem__(self, pos: int|slice) -> str:
        return self.text[pos]
    
    def startswith(self, prefix: str, pos: int) -> StringMatch | None:
        if self.text.startswith(prefix, pos):
            return StringMatch((pos, pos+len(prefix)))
        else:
            return None

    def matchedby(self, pattern: re.Pattern, pos: int) -> StringMatch | None:
        m = pattern.match(self.text, pos)
        if m is not None:
            return StringMatch(m.span())
        else:
            return None