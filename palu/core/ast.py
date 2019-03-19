from typing import Union
from collections.abc import Sequence
from enum import Enum


class ASTType(Enum):
    WHILE = 'while'
    IF = 'if'
    THEN = 'then'
    DO = 'do'
    END = 'end'


class ASTNode(Sequence[Union['ASTNode', ASTType]]):
    def __init__(self, *args):
        self._items = [*args]

    def __getitem__(self, idx):
        return self._items[idx]

    def __len__(self):
        return len(self._items)


class Stmt:
    pass


class SimpleStmt(Stmt):

    def __init__(self, expr):
        self.expr = expr

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f'<SIMPLE_STMT expr = {self.expr} >'


class Expr:
    pass


class BinExpr(Expr):
    def __init__(self, operator, loperand, roperand):
        self.operator = operator
        self.loperand = loperand
        self.roperand = roperand

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f'<BINARY_EXPR {self.loperand} {self.operator} {self.roperand}>'


class Literal(Expr):
    def __init__(self, literal):
        self.literal = literal


class FnCall(Expr):
    def __init__(self, fn, args):
        self.fn = fn
        self.args = args


class Variable(Expr):
    def __init__(self, name):
        self.name = name


class Branches:

    def __init__(self, condition, codeblock):
        self.condition = condition
        self.codeblock = codeblock


class WhileLoop:

    def __init__(self, condition, codeblock):
        self.condition = condition
        self.codeblock = codeblock
