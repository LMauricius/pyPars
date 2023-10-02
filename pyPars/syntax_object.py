from dataclasses import dataclass, field
    
@dataclass
class SyntaxObject:
    grammarAttributeNames: set[str] = field(default_factory=set) 
    span: tuple[int, int] = (0,0)
    options: list["SyntaxObject"] = []

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

        if len(source.options) > 0:
            self.extendOptions(source.options)

    def extendOptions(self, sources: "list[SyntaxObject]")->None:
        '''
        Each entry is treated as an option in an ambiguity
        '''
        if len(sources) == 1:
            self.extend(sources[0])
        elif len(self.options) == 0:
            self.options = sources
        else:
            newoptions = []
            for option in self.options:
                for source in sources:
                    newopt = SyntaxObject(set())
                    newopt.extend(option)
                    newopt.extend(source)
                    newoptions.append(newopt)
            self.options = newoptions


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