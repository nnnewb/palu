from palu.ast.node import Node
from typing import Sequence, Tuple


class Func(Node):
    def __init__(self, start: Tuple[int, int], end: Tuple[int, int], name: str, params: Sequence, ret, body:  Sequence[Node]):
        super().__init__(start, end)
        self.func_name = name
        self.params = params
        self.returns = ret
        self.body = body
