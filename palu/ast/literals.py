from palu.ast.node import Node
from typing import Tuple

class NumberLiteral(Node):
    def __init__(self, start: Tuple[int, int], end: Tuple[int, int], text: str) -> None:
        super().__init__(start, end)
        self.value = int(text)


class StringLiteral(Node):
    def __init__(self, start: Tuple[int, int], end: Tuple[int, int], text) -> None:
        super().__init__(start, end)
        self.value = text


class BooleanLiteral(Node):
    def __init__(self, start: Tuple[int, int], end: Tuple[int, int], text: str) -> None:
        super().__init__(start, end)
        self.value = True if text == 'true' else False


class NullLiteral(Node):
    def __init__(self, start: Tuple[int, int], end: Tuple[int, int],) -> None:
        super().__init__(start, end)
        self.value = None