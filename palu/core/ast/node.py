from abc import ABCMeta, abstractproperty
from enum import Enum
from typing import Sequence, Union, Optional

from palu import stubs


class ASTNode(metaclass=ABCMeta):
    @abstractproperty
    def s_expr(self) -> str:
        ...


class EmptyStatement(ASTNode):
    def __init__(self) -> None:
        super().__init__()

    @property
    def s_expr(self) -> str:
        return '()'


class DeclareStatement(ASTNode):
    def __init__(self, typed_ident: 'TypedIdent', initial_value: ASTNode) -> None:
        super().__init__()
        self.typed_ident = typed_ident
        self.initial_value = initial_value

    @property
    def s_expr(self) -> str:
        return f'(define {self.typed_ident.s_expr} {self.initial_value.s_expr})'


class ExternalStatement(ASTNode):
    def __init__(self, typed_ident: 'TypedIdent') -> None:
        super().__init__()
        self.typed_ident = typed_ident

    @property
    def s_expr(self) -> str:
        return f'(external {self.typed_ident.s_expr})'


class WhileLoop(ASTNode):
    def __init__(self, condition: ASTNode, statements: Sequence[ASTNode]) -> None:
        super().__init__()
        self.condition = condition
        self.body: Sequence[ASTNode] = statements

    @property
    def s_expr(self) -> str:
        statements = []
        for stmt in self.body:
            statements.append(stmt.s_expr)
        return f'(while {self.condition.s_expr} {" ".join(statements)})'


class IfBranch(ASTNode):
    def __init__(self, condition: ASTNode, consequence: Sequence[ASTNode], alternative: Sequence[ASTNode]) -> None:
        super().__init__()
        self.condition = condition
        self.consequence: Sequence[ASTNode] = consequence
        self.alternative: Sequence[ASTNode] = alternative

    @property
    def s_expr(self) -> str:
        consequence = []
        alternative = []

        for stmt in self.consequence:
            consequence.append(stmt.s_expr)

        for stmt in self.alternative:
            alternative.append(stmt.s_expr)

        return f'(if {self.condition.s_expr} ({" ".join(consequence)}) ({" ".join(alternative)}))'


class ReturnStatement(ASTNode):
    def __init__(self, expr: ASTNode) -> None:
        super().__init__()
        self.expr = expr

    @property
    def s_expr(self) -> str:
        return f'(return {self.expr.s_expr})'


class IdentExpr(ASTNode):
    def __init__(self, *ident: str) -> None:
        super().__init__()
        self.ident = ident

    @property
    def s_expr(self) -> str:
        return f'{".".join(self.ident)}'


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


class BinaryExpr(ASTNode):
    def __init__(self, op: BinaryOp, left: ASTNode, right: ASTNode) -> None:
        super().__init__()
        self.left = left
        self.right = right
        self.op = op

    @property
    def s_expr(self) -> str:
        return f'({self.op} {self.left.s_expr} {self.right.s_expr})'


class UnaryOp(Enum):
    ADD = '+'
    SUB = '-'
    NOT = '!'


class UnaryExpr(ASTNode):
    def __init__(self, op: UnaryOp, expr: ASTNode) -> None:
        super().__init__()
        self.op = op
        self.expr = expr

    @property
    def s_expr(self) -> str:
        return f'({self.op} {self.expr.s_expr})'


class ConditionExpr(ASTNode):
    def __init__(self, condition: ASTNode, consequence: ASTNode, alternative: ASTNode) -> None:
        super().__init__()
        self.condition = condition
        self.consequence = consequence
        self.alternative = alternative

    @property
    def s_expr(self) -> str:
        return f'(if {self.condition.s_expr} {self.consequence.s_expr} {self.alternative.s_expr})'


class CallExpr(ASTNode):
    def __init__(self, ident: IdentExpr, *args: ASTNode) -> None:
        super().__init__()
        self.ident = ident
        self.args = args

    @property
    def s_expr(self) -> str:
        args = []
        for arg in self.args:
            args.append(arg.s_expr)

        return f'({self.ident.s_expr} {" ".join(args)})'


class TypedIdent(object):
    def __init__(self, ident: str, typing: Union[IdentExpr, 'FunctionSignature']) -> None:
        super().__init__()
        self.ident = ident
        self.typing = typing

    @property
    def s_expr(self):
        return f'{self.ident} : {self.typing.s_expr}'


class LambdaExpr(ASTNode):
    def __init__(self, signature: 'FunctionSignature', *statements:  Union['ASTNode', ASTNode]) -> None:
        super().__init__()
        self.signature = signature
        self.statements = statements

    @property
    def s_expr(self) -> str:
        if len(self.statements) == 1 and isinstance(self.statements[0], ASTNode):
            returns = ReturnStatement(self.statements[0])
            return f'(lambda {self.signature.s_expr} {returns.s_expr})'
        else:
            statements = []
            for stmt in self.statements:
                statements.append(stmt.s_expr)
            return f'(lambda {self.signature.s_expr} ({" ".join(statements)}))'


class ParenthesizedExpr(ASTNode):
    def __init__(self, expr: ASTNode) -> None:
        super().__init__()
        self.expr = expr

    @property
    def s_expr(self) -> str:
        return f'({self.expr.s_expr})'


class NumberLiteral(ASTNode):
    def __init__(self, text: str) -> None:
        super().__init__()
        self.value = int(text)

    @property
    def s_expr(self) -> str:
        return f'{self.value}'


class StringLiteral(ASTNode):
    def __init__(self, text) -> None:
        super().__init__()
        self.value = text

    @property
    def s_expr(self) -> str:
        return f'"{self.value}"'


class BooleanLiteral(ASTNode):
    def __init__(self, node: stubs.Node) -> None:
        super().__init__()
        self.value = True if node.type == 'true' else False

    @property
    def s_expr(self) -> str:
        return f'{self.value}'


class NullLiteral(ASTNode):
    def __init__(self) -> None:
        super().__init__()
        self.value = None

    @property
    def s_expr(self) -> str:
        return 'null'


class FunctionSignature(object):
    def __init__(self, returns: Union[IdentExpr, 'FunctionSignature'], *params: TypedIdent) -> None:
        super().__init__()
        self.params = params
        self.returns = returns

    @property
    def s_expr(self) -> str:
        params = []
        for p in self.params:
            params.append(p.s_expr)
        return f'([{" ".join(params)}]) : {self.returns.s_expr}'
