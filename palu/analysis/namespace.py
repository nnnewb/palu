from abc import ABC


class Namespace(ABC):
    def __init__(self, parent: 'Namespace') -> None:
        super().__init__()
        self.parent = parent
        self.children = []
