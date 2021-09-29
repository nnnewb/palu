from palu.ast.node import Node
from typing import Optional, Sequence, Tuple


class EmptyStatement(Node):
    def __init__(self, start: Tuple[int, int], end: Tuple[int, int]) -> None:
        super().__init__(start, end)


class DeclareStatement(Node):
    def __init__(self, start: Tuple[int, int], end: Tuple[int, int], typed_ident, initial_value: Node) -> None:
        super().__init__(start, end)
        self.typed_ident = typed_ident
        self.initial_value = initial_value


class ExternalStatement(Node):
    def __init__(self, start: Tuple[int, int], end: Tuple[int, int], spec) -> None:
        super().__init__(start, end)
        self.spec = spec


class ExternalFunctionSpec(Node):
    def __init__(self, start: Tuple[int, int], end: Tuple[int, int], ident, params, returns) -> None:
        super().__init__(start, end)
        self.ident = ident
        self.params = params
        self.returns = returns


class ExternalVariableSpec(Node):
    def __init__(self, start: Tuple[int, int], end: Tuple[int, int], typed_ident) -> None:
        super().__init__(start, end)
        self.typed_ident = typed_ident


class WhileLoop(Node):
    def __init__(self, start: Tuple[int, int], end: Tuple[int, int], condition: Node, statements: Sequence[Node]) -> None:
        super().__init__(start, end)
        self.condition = condition
        self.body: Sequence[Node] = statements


class If(Node):
    def __init__(self, start: Tuple[int, int], end: Tuple[int, int], condition: Node, consequence: Sequence[Node], alternative: Optional[Sequence[Node]]) -> None:
        super().__init__(start, end)
        self.condition = condition
        self.consequence = consequence
        self.alternative = alternative


class ReturnStatement(Node):
    def __init__(self, start: Tuple[int, int], end: Tuple[int, int], expr: Node) -> None:
        super().__init__(start, end)
        self.expr = expr


class TypeAliasStatement(Node):
    def __init__(self, start: Tuple[int, int], end: Tuple[int, int], ident: str, typing, is_pointer=False) -> None:
        super().__init__(start, end)
        self.ident = ident
        self.typing = typing
        self.is_pointer = is_pointer
