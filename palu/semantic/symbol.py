from palu.semantic.namespace import Namespace


class Symbol(Namespace):
    def __init__(self, name: str) -> None:
        super().__init__()
        self.name = name
