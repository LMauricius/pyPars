from typing import Callable

class ModularDictMethodObject:

    def __init__(
        self
    ) -> None:
        super().__init__()
        self._dict_extractor_modules: list[Callable[[__class__], dict[str, any]]] = []

    def __dict__(self) -> dict[str, "any"]:
        d = {}
        for extractor in self._dict_extractor_modules:
            d |= extractor(self)

        return d