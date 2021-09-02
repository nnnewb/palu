from abc import ABCMeta
from enum import Enum
from palu import stubs
from typing import Sequence


class Expr(object, metaclass=ABCMeta):
    def __init__(self) -> None:
        super().__init__()


class IdentExpr(Expr):
    def __init__(self, *ident: str) -> None:
        super().__init__()
        self.ident = ident


class BinaryOp(Enum):
    ADD = '+'
    SUB = '-'
    MUL = '*'
    DIV = '/'
    PERC = '%'
    OR = '||'
    AND = '&&'
    BIT_OR = '|'
    BIT_AND = '&'
    BIT_XOR = '^'
    EQ = '=='
    NE = '!='
    GT = '>'
    LT = '<'
    GTE = '>='
    LTE = '<='
    LSHIFT = '<<'
    RSHIFT = '>>'


class BinaryExpr(Expr):
    def __init__(self, op: BinaryOp, left: Expr, right: Expr) -> None:
        super().__init__()
        self.left = left
        self.right = right
        self.op = op


class UnaryOp(Enum):
    ADD = '+'
    SUB = '-'
    NOT = '!'


class UnaryExpr(Expr):
    def __init__(self, op: UnaryOp, expr: Expr) -> None:
        super().__init__()
        self.op = op
        self.expr = expr


class ConditionExpr(Expr):
    def __init__(self, condition: Expr, if_expr: Expr, else_expr: Expr) -> None:
        super().__init__()
        self.condition = condition
        self.if_expr = if_expr
        self.else_expr = else_expr


class CallExpr(Expr):
    def __init__(self, ident: IdentExpr, *args: Expr) -> None:
        super().__init__()
        self.ident = ident
        self.args = args


class TypedIdent(object):
    def __init__(self, ident, typing) -> None:
        super().__init__()
        self.ident = ident
        self.typing = typing


class LambdaExpr(Expr):
    def __init__(self, params: Sequence[TypedIdent], *statements: 'Statement') -> None:
        super().__init__()
        self.params = params
        self.statements = statements


class ParenthesizedExpr(Expr):
    def __init__(self, expr: Expr) -> None:
        super().__init__()
        self.expr = expr


class NumberLiteral(Expr):
    def __init__(self, text: str) -> None:
        super().__init__()
        self.value = int(text)


class StringLiteral(Expr):
    def __init__(self, text) -> None:
        super().__init__()
        self.value = text


class BooleanLiteral(Expr):
    def __init__(self, node: stubs.Node) -> None:
        super().__init__()
        self.value = True if node.type == 'true' else False


class NullLiteral(Expr):
    def __init__(self) -> None:
        super().__init__()
        self.value = None
