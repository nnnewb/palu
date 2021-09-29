from abc import ABCMeta
from enum import Enum
from typing import Optional, Sequence, Tuple, Union


class Node(metaclass=ABCMeta):
    def __init__(self, start: Tuple[int, int], end: Tuple[int, int]) -> None:
        self.start_pos = start
        self.end_pos = end

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} {self.start_pos[0]}:{self.start_pos[1]}>'

class FuncDecl(object):
    def __init__(self, func_name: str, params: Sequence['TypedIdent'], returns: 'IdentExpr') -> None:
        super().__init__()
        self.func_name = func_name
        self.params = params
        self.returns = returns


class SourceFile(Node):
    def __init__(self, start: Tuple[int, int], end: Tuple[int, int], statements: Sequence[Node]) -> None:
        super().__init__(start, end)
        self.mod = ''
        self.statements = statements

        for stmt in self.statements:
            if isinstance(stmt, ModDeclare):
                self.mod = stmt.name


class EmptyStatement(Node):
    def __init__(self, start: Tuple[int, int], end: Tuple[int, int]) -> None:
        super().__init__(start, end)


class ModDeclare(Node):
    def __init__(self, start: Tuple[int, int], end: Tuple[int, int], name: str) -> None:
        super().__init__(start, end)
        self.name = name


class DeclareStatement(Node):
    def __init__(self, start: Tuple[int, int], end: Tuple[int, int], typed_ident: 'TypedIdent', initial_value: Node) -> None:
        super().__init__(start, end)
        self.typed_ident = typed_ident
        self.initial_value = initial_value


class ExternalStatement(Node):
    def __init__(self, start: Tuple[int, int], end: Tuple[int, int], external_sym: Union['TypedIdent', 'FuncDecl']) -> None:
        super().__init__(start, end)
        self.external_sym = external_sym


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
    def __init__(self, start: Tuple[int, int], end: Tuple[int, int], ident: str, typing: 'IdentExpr') -> None:
        super().__init__(start, end)
        self.ident = ident
        self.typing = typing


class IdentExpr(Node):
    def __init__(self, start: Tuple[int, int], end: Tuple[int, int], *ident: str) -> None:
        super().__init__(start, end)
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


class BinaryExpr(Node):
    def __init__(self, start: Tuple[int, int], end: Tuple[int, int], op: BinaryOp, left: Node, right: Node) -> None:
        super().__init__(start, end)
        self.left = left
        self.right = right
        self.op = op


class UnaryOp(Enum):
    ADD = '+'
    SUB = '-'
    NOT = '!'


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


class TypedIdent(object):
    def __init__(self, ident: str, typing: IdentExpr, ) -> None:
        super().__init__()
        self.ident = ident
        self.typing = typing


class Func(Node):
    def __init__(self, start: Tuple[int, int], end: Tuple[int, int], name: str, params: Sequence[TypedIdent], ret: IdentExpr, body:  Sequence[Node]):
        super().__init__(start, end)
        self.func_name = name
        self.params = params
        self.returns = ret
        self.body = body


class ParenthesizedExpr(Node):
    def __init__(self, start: Tuple[int, int], end: Tuple[int, int], expr: Node) -> None:
        super().__init__(start, end)
        self.expr = expr


class AsssignmentOp(Enum):
    Direct = '='
    MulAssign = '*='
    DivAssign = '/='
    AddAssign = '+='
    SubAssign = '-='
    LSAssign = '<<='
    RSAssign = '>>='
    BAAssign = '&='
    BOAssign = '|='
    BXAssign = '^='


class AssignmentExpr(Node):
    def __init__(self, start: Tuple[int, int], end: Tuple[int, int], left: IdentExpr, op: AsssignmentOp, right: Node):
        super().__init__(start, end)
        self.left = left
        self.right = right
        self.op = op


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
