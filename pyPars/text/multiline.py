import re
from dataclasses import dataclass

@dataclass
class MultilinePos:
    line: int
    char: int
    abspos: int

@dataclass
class MultilineMatch:
    span: tuple[MultilinePos,MultilinePos]

class MultilineText:

    def __init__(self, text: str) -> None:
        self.text = text

    def shiftedMultilinePos(self, start: MultilinePos, shift: int) -> MultilinePos:
        numNL = self.text.count('\n', start.abspos, start.abspos+shift)

        if numNL == 0:
            return MultilinePos(start.line, start.char+shift, start.abspos+shift)
        else:
            lastNL = self.text.rfind('\n', start.abspos, start.abspos+shift)
            return MultilinePos(start.line + numNL, start.abspos+shift - lastNL, start.abspos+shift)
    
    def GetPositionType(self) -> type[MultilinePos]:
        return MultilinePos
    
    def GetNativeType(self) -> type[str]:
        return str
    
    def GetPatternType(self) -> type[re.Pattern]:
        return re.Pattern
    
    def GetMatchType(self) -> type[re.Match]:
        return re.Match
    
    def getStartPos(self) -> MultilinePos:
        return MultilinePos(0,0,0)
    
    def __getitem__(self, pos: MultilinePos|slice) -> str:
        if isinstance(pos, slice):
            return self.text[pos.start.abspos:pos.stop.abspos:pos.step]
        else:
            return self.text[pos.abspos]
    
    def startswith(self, prefix: str, pos: MultilinePos) -> MultilineMatch | None:
        if self.text.startswith(prefix, pos.abspos):
            return MultilineMatch((pos, self.shiftedMultilinePos(pos, len(prefix))))
        else:
            return None

    def matchedby(self, pattern: re.Pattern, pos: MultilinePos) -> MultilineMatch | None:
        m = pattern.match(self.text, pos.abspos)
        if m is not None:
            return MultilineMatch(
                pos,
                self.shiftedMultilinePos(pos, m.span()[1] - m.span()[0])
            )
        else:
            return None