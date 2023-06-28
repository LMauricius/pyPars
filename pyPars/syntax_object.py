from dataclasses import dataclass, field
    
@dataclass
class SyntaxObject:
    grammarAttributeNames: set[str] = field(default_factory=set) 
    span: tuple[int, int] = (0,0)

    def extend(self, source: "SyntaxObject")->None:
        '''
        Appends all attribute values from source to target's attributes
        '''
        for grammarAttrName in source.grammarAttributeNames:
            newGrammarAttr: list = getattr(source, grammarAttrName)
            if grammarAttrName in self.grammarAttributeNames:
                grammarAttr: list = getattr(self, grammarAttrName)
            else:
                grammarAttr = []
                self.grammarAttributeNames.add(grammarAttrName)
                setattr(self, grammarAttrName, grammarAttr)
            grammarAttr.extend(newGrammarAttr)

    def __dict__(self) -> dict[str, 'any']:
        return {
            "__class__.__name__": self.__class__.__name__,
            "span": self.span
        } | {
            grammarAttrName: [
                subobj.__dict__()
                for subobj in getattr(self, grammarAttrName)
            ]
            for grammarAttrName in self.grammarAttributeNames
        }