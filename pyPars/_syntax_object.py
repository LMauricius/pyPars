from dataclasses import dataclass, field
    
@dataclass
class SyntaxObject:
    so_grammarAttributeNames: set[str] = field(default_factory=set) 
    so_span: tuple[int, int] = (0,0)
    so_options: list["SyntaxObject"] = field(default_factory=list)

    def extend(self, source: "SyntaxObject")->None:
        '''
        Appends all attribute values from source to target's attributes
        '''
        for grammarAttrName in source.so_grammarAttributeNames:
            newGrammarAttr: list = getattr(source, grammarAttrName)
            if grammarAttrName in self.so_grammarAttributeNames:
                grammarAttr: list = getattr(self, grammarAttrName)
            else:
                grammarAttr = []
                self.so_grammarAttributeNames.add(grammarAttrName)
                setattr(self, grammarAttrName, grammarAttr)
            grammarAttr.extend(newGrammarAttr)

        if len(source.so_options) > 0:
            self.extendOptions(source.so_options)

    def extendOptions(self, sources: "list[SyntaxObject]")->None:
        '''
        Each entry is treated as an option in an ambiguity
        '''
        if len(sources) == 1:
            self.extend(sources[0])
        elif len(self.so_options) == 0:
            self.so_options = sources
        else:
            newoptions = []
            for option in self.so_options:
                for source in sources:
                    newopt = SyntaxObject(set())
                    newopt.extend(option)
                    newopt.extend(source)
                    newoptions.append(newopt)
            self.so_options = newoptions


    def __dict__(self) -> dict[str, 'any']:
        return {
            "__class__.__name__": self.__class__.__name__,
            "span": self.so_span
        } | {
            grammarAttrName: [
                subobj.__dict__()
                for subobj in getattr(self, grammarAttrName)
            ]
            for grammarAttrName in self.so_grammarAttributeNames
        }