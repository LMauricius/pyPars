from dataclasses import dataclass, field
from ._modular_dict_method import ModularDictMethodObject


class SyntaxObject(ModularDictMethodObject):
    def __init__(
        self,
        grammarAttributeNames: set[str] = None,
        options: list["SyntaxObject"] = None,
    ) -> None:
        super().__init__()

        self.so_grammarAttributeNames = (
            set() if grammarAttributeNames is None else grammarAttributeNames
        )

        self.so_options = [] if options is None else options

        self._dict_extractor_modules.append(
            lambda self: (
                {"<class>": self.__class__.__name__}
                | {
                    grammarAttrName: [
                        subobj for subobj in getattr(self, grammarAttrName)
                    ]
                    for grammarAttrName in self.so_grammarAttributeNames
                }
            )
        )

    def extend(self, source: "SyntaxObject") -> None:
        """
        Appends all attribute values from source to target's attributes
        """
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

    def extendOptions(self, sources: "list[SyntaxObject]") -> None:
        """
        Each entry is treated as an option in an ambiguity
        """
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
