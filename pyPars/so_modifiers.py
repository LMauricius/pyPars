from dataclasses import dataclass
from .text import Text, NatT, PosT, PatternT, MatchT
from ._modular_dict_method import ModularDictMethodObject


class TextSaver(ModularDictMethodObject):
    """
    Adds the `so_savedText` attribute to SyntaxObjects inheriting this class.
    `so_savedText` holds the slice of the parsed text spanned by the object.
    """

    def __init__(self) -> None:
        super().__init__()
        self.so_savedText: NatT = None

        self._dict_extractor_modules.append(lambda self: {"<text>": self.so_savedText})


class SpanSaver(ModularDictMethodObject):
    """
    Adds the `so_span` attribute to SyntaxObjects inheriting this class.
    `so_span` is a tuple of the start and end position in the text spanned by the object.
    """

    def __init__(self) -> None:
        super().__init__()
        self.so_span: tuple[PosT, PosT] = None

        self._dict_extractor_modules.append(lambda self: {"<span>": self.so_span})


class SelfReplacable(ModularDictMethodObject):
    """
    Allows replacing the SyntaxObject with its `self` attribute when assigned
    """

    def __init__(self) -> None:
        super().__init__()