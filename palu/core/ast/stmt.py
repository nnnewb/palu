from abc import ABCMeta
from palu.core.ast.expr import Expr, TypedIdent
from typing import Optional, Sequence


class Statement(metaclass=ABCMeta):
    def __init__(self) -> None:
        super().__init__()


class EmptyStatement(Statement):
    def __init__(self) -> None:
        super().__init__()


class DeclareStatement(Statement):
    def __init__(self, typed_ident: TypedIdent, initial_value: Expr) -> None:
        super().__init__()
        self.typed_ident = typed_ident
        self.initial_value = initial_value


class ExternalStatement(Statement):
    def __init__(self, typed_ident: TypedIdent) -> None:
        super().__init__()
        self.typed_ident = typed_ident


class WhileLoop(Statement):
    def __init__(self, condition: Expr, statements: Sequence[Statement]) -> None:
        super().__init__()
        self.condition = condition
        self.body: Sequence[Statement] = statements


class IfBranch(Statement):
    def __init__(self, condition: Expr, statements: Sequence[Statement]) -> None:
        super().__init__()
        self.condition = condition
        self.body: Sequence[Statement] = statements


class ElseBranch(Statement):
    def __init__(self, statements: Sequence[Statement]) -> None:
        super().__init__()
        self.body: Sequence[Statement] = statements


class ReturnStatement(Statement):
    def __init__(self, expr: Expr) -> None:
        super().__init__()
        self.expr = expr
