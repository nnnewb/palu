from abc import ABCMeta
from typing import Sequence

from palu.core.ast.node import (
    ASTNode,
    BinaryExpr,
    BooleanLiteral,
    CallExpr,
    ConditionExpr,
    DeclareStatement,
    ExternalStatement,
    IdentExpr,
    IfBranch,
    NullLiteral,
    NumberLiteral,
    ParenthesizedExpr,
    ReturnStatement,
    StringLiteral,
    UnaryExpr,
    WhileLoop
)


class Transpiler(metaclass=ABCMeta):
    def __init__(self) -> None:
        super().__init__()

    def transpile(self, ast: Sequence[ASTNode]):
        for node in ast:
            if isinstance(node, DeclareStatement):
                return self.transpile_declare_stmt(node)
            elif isinstance(node, ExternalStatement):
                return self.transpile_external_stmt(node)
            elif isinstance(node, WhileLoop):
                return self.transpile_while_stmt(node)
            elif isinstance(node, IfBranch):
                return self.transpile_if_stmt(node)
            elif isinstance(node, ReturnStatement):
                return self.transpile_return_stmt()
            elif isinstance(node, IdentExpr):
                return self.transpile_ident_expr(node)
            elif isinstance(node, BinaryExpr):
                return self.transpile_binary_expr(node)
            elif isinstance(node, UnaryExpr):
                return self.transpile_unary_expr(node)
            elif isinstance(node, ConditionExpr):
                return self.transpile_condition_expr(node)
            elif isinstance(node, CallExpr):
                return self.transpile_call_expr(node)
            elif isinstance(node, ParenthesizedExpr):
                return self.transpile_parenthesized_expr(node)
            elif isinstance(node, NumberLiteral):
                return self.transpile_number_literal(node)
            elif isinstance(node, StringLiteral):
                return self.transpile_string_literal(node)
            elif isinstance(node, BooleanLiteral):
                return self.transpile_boolean_literal(node)
            elif isinstance(node, NullLiteral):
                return self.transpile_null_literal(node)
            else:
                raise Exception(f'unexpected ast node {node}')

    def transpile_statement(self):
        raise NotImplemented

    def transpile_declare_stmt(self, node: ASTNode):
        raise NotImplemented

    def transpile_external_stmt(self):
        raise NotImplemented

    def transpile_while_stmt(self):
        raise NotImplemented

    def transpile_if_stmt(self):
        raise NotImplemented

    def transpile_return_stmt(self):
        raise NotImplemented

    def transpile_expr(self):
        raise NotImplemented

    def transpile_ident_expr(self):
        raise NotImplemented

    def transpile_binary_expr(self):
        raise NotImplemented

    def transpile_unary_expr(self):
        raise NotImplemented

    def transpile_condition_expr(self):
        raise NotImplemented

    def transpile_call_expr(self):
        raise NotImplemented

    def transpile_lambda_expr(self):
        raise NotImplemented

    def transpile_parenthesized_expr(self):
        raise NotImplemented

    def transpile_number_literal(self):
        raise NotImplemented

    def transpile_string_literal(self):
        raise NotImplemented

    def transpile_boolean_literal(self):
        raise NotImplemented

    def transpile_null_literal(self):
        raise NotImplemented
