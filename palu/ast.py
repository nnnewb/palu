from abc import ABCMeta, abstractproperty
from enum import Enum
from typing import Optional, Sequence, Union

from palu.symbol import Symbol


class FuncDecl(object):
    def __init__(self, func_name: str, params: Sequence['TypedIdent'], returns: 'IdentExpr', sym: Symbol) -> None:
        super().__init__()
        self.func_name = func_name
        self.params = params
        self.returns = returns
        self.sym = sym

    @property
    def s_expr(self) -> str:
        params = []

        for typed_ident in self.params:
            params.append(f'{typed_ident.ident} : {typed_ident.typing.s_expr}')

        return f'(declare {self.func_name} {" ".join(params)} {self.returns.s_expr})'


class ASTNode(metaclass=ABCMeta):
    @abstractproperty
    def s_expr(self) -> str:
        ...


class SourceFile(ASTNode):
    def __init__(self, statements: Sequence[ASTNode]) -> None:
        super().__init__()
        self.mod = ''
        self.statements = statements

        for stmt in self.statements:
            if isinstance(stmt, ModDeclare):
                self.mod = stmt.name

    @property
    def s_expr(self) -> str:
        statements = []
        for stmt in self.statements:
            statements.append(stmt.s_expr)

        return '\n'.join(statements)


class EmptyStatement(ASTNode):
    def __init__(self) -> None:
        super().__init__()

    @property
    def s_expr(self) -> str:
        return '()'


class ModDeclare(ASTNode):
    def __init__(self, name: str, sym: Symbol) -> None:
        super().__init__()
        self.name = name
        self.sym = sym

    @property
    def s_expr(self) -> str:
        return f'; module {self.name}'


class DeclareStatement(ASTNode):
    def __init__(self, typed_ident: 'TypedIdent', initial_value: ASTNode, sym: Symbol) -> None:
        super().__init__()
        self.typed_ident = typed_ident
        self.initial_value = initial_value
        self.sym = sym

    @property
    def s_expr(self) -> str:
        return f'(define {self.typed_ident.s_expr} {self.initial_value.s_expr})'


class ExternalStatement(ASTNode):
    def __init__(self, external_sym: Union['TypedIdent', 'FuncDecl'], sym: Symbol) -> None:
        super().__init__()
        self.external_sym = external_sym
        self.sym = sym

    @property
    def s_expr(self) -> str:
        return f'(external {self.external_sym.s_expr})'


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


class If(ASTNode):
    def __init__(self, condition: ASTNode, consequence: Sequence[ASTNode], alternative: Optional[Sequence[ASTNode]]) -> None:
        super().__init__()
        self.condition = condition
        self.consequence = consequence
        self.alternative = alternative

    @property
    def s_expr(self) -> str:
        consequence = []
        alternative = []

        for stmt in self.consequence:
            consequence.append(stmt.s_expr)

        if self.alternative:
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


class TypeAliasStatement(ASTNode):
    def __init__(self, ident: str, typing: 'IdentExpr', sym: Symbol) -> None:
        super().__init__()
        self.ident = ident
        self.typing = typing
        self.sym = sym

    @property
    def s_expr(self) -> str:
        return f'(define-type-alias {self.ident} ({self.typing.s_expr}))'


class IdentExpr(ASTNode):
    def __init__(self, *ident: str, sym: Symbol) -> None:
        super().__init__()
        self.ident = ident
        self.sym = sym

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
    def __init__(self, ident: IdentExpr, *args: ASTNode, fn_sym: Symbol) -> None:
        super().__init__()
        self.ident = ident
        self.args = args
        self.fn_sym = fn_sym

    @property
    def s_expr(self) -> str:
        args = []
        for arg in self.args:
            args.append(arg.s_expr)

        return f'({self.ident.s_expr} {" ".join(args)})'


class TypedIdent(object):
    def __init__(self, ident: str, typing: IdentExpr, sym: Symbol) -> None:
        super().__init__()
        self.ident = ident
        self.typing = typing
        self.sym = sym

    @property
    def s_expr(self):
        return f'{self.ident} : {self.typing.s_expr}'


class Func(ASTNode):
    def __init__(self, func_name: str, params: Sequence[TypedIdent], returns: IdentExpr, body:  Sequence[ASTNode], sym: Symbol) -> None:
        super().__init__()
        self.func_name = func_name
        self.params = params
        self.returns = returns
        self.body = body
        self.sym = sym

    @property
    def s_expr(self) -> str:
        params = []
        body = []

        for typed_ident in self.params:
            params.append(f'{typed_ident.ident} : {typed_ident.typing.s_expr}')

        for stmt in self.body:
            body.append(f'{stmt.s_expr}')

        return f'(define {self.func_name} {" ".join(params)} {self.returns.s_expr} ({" ".join(body)}))'


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
    def __init__(self, text: str) -> None:
        super().__init__()
        self.value = True if text == 'true' else False

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
