from typing import Tuple
from palu.ast.node import Node
from palu.ast.op import BinaryOp, UnaryOp, AsssignmentOp


class TypedIdent(object):
    def __init__(self, ident: str, typing, is_pointer=False) -> None:
        super().__init__()
        self.ident = ident
        self.typing = typing
        self.is_pointer = is_pointer


class IdentExpr(Node):
    def __init__(self, start: Tuple[int, int], end: Tuple[int, int], *ident: str) -> None:
        super().__init__(start, end)
        self.ident = ident


class BinaryExpr(Node):
    def __init__(self, start: Tuple[int, int], end: Tuple[int, int], op: BinaryOp, left: Node, right: Node) -> None:
        super().__init__(start, end)
        self.left = left
        self.right = right
        self.op = op


class UnaryExpr(Node):
    def __init__(self, start: Tuple[int, int], end: Tuple[int, int], op: UnaryOp, expr: Node) -> None:
        super().__init__(start, end)
        self.op = op
        self.expr = expr


class ConditionExpr(Node):
    def __init__(self, start: Tuple[int, int], end: Tuple[int, int], condition: Node, consequence: Node, alternative: Node) -> None:
        super().__init__(start, end)
        self.condition = condition
        self.consequence = consequence
        self.alternative = alternative


class CallExpr(Node):
    def __init__(self, start: Tuple[int, int], end: Tuple[int, int], ident: IdentExpr, *args: Node) -> None:
        super().__init__(start, end)
        self.ident = ident
        self.args = args


class ParenthesizedExpr(Node):
    def __init__(self, start: Tuple[int, int], end: Tuple[int, int], expr: Node) -> None:
        super().__init__(start, end)
        self.expr = expr


class AssignmentExpr(Node):
    def __init__(self, start: Tuple[int, int], end: Tuple[int, int], left: IdentExpr, op: AsssignmentOp, right: Node):
        super().__init__(start, end)
        self.left = left
        self.right = right
        self.op = op
