from abc import ABCMeta
from typing import Optional, Sequence


class Statement(metaclass=ABCMeta):
    def __init__(self) -> None:
        super().__init__()


class EmptyStatement(Statement):
    def __init__(self) -> None:
        super().__init__()


class DeclareStatement(Statement):
    def __init__(self, typed_ident) -> None:
        super().__init__()
        self.typed_ident = typed_ident


class ExternalStatement(Statement):
    def __init__(self, typed_ident) -> None:
        super().__init__()
        self.typed_ident = typed_ident


class WhileLoop(Statement):
    def __init__(self, condition) -> None:
        super().__init__()
        self.condition = condition
        self.body: Sequence[Statement] = []


class IfBranch(Statement):
    def __init__(self, condition, else_branch) -> None:
        super().__init__()
        self.condition = condition
        self.body: Sequence[Statement] = []
        self.else_branch: Optional[ElseBranch] = else_branch


class ElseBranch(Statement):
    def __init__(self) -> None:
        super().__init__()
        self.body: Sequence[Statement] = []


class ReturnStatement(Statement):
    def __init__(self, expr) -> None:
        super().__init__()
        self.expr = expr
