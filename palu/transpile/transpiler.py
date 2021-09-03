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
    Func,
    IdentExpr,
    IfBranch,
    NullLiteral,
    NumberLiteral,
    ParenthesizedExpr,
    ReturnStatement,
    StringLiteral,
    TypeAliasStatement,
    TypedIdent,
    UnaryExpr,
    WhileLoop
)


class Transpiler(metaclass=ABCMeta):
    def __init__(self) -> None:
        super().__init__()

    def transpile(self, node: ASTNode):
        if isinstance(node, DeclareStatement):
            return self.transpile_declare_stmt(node)
        elif isinstance(node, ExternalStatement):
            return self.transpile_external_stmt(node)
        elif isinstance(node, WhileLoop):
            return self.transpile_while_stmt(node)
        elif isinstance(node, IfBranch):
            return self.transpile_if_stmt(node)
        elif isinstance(node, ReturnStatement):
            return self.transpile_return_stmt(node)
        elif isinstance(node, Func):
            return self.transpile_func_stmt(node)
        elif isinstance(node, TypeAliasStatement):
            return self.transpile_type_alias_stmt(node)
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

    def transpile_declare_stmt(self, node: DeclareStatement):
        return f'{self.transpile_ident_expr(node.typed_ident.typing)} {node.typed_ident.ident};'

    def transpile_external_stmt(self, node):
        raise NotImplementedError()

    def transpile_while_stmt(self, node: WhileLoop):
        statements = []
        for stmt in node.body:
            statements.append(self.transpile(stmt))

        body = '\n'.join(statements)

        return f'''\
            while({self.transpile(node.condition)}) {{
                {body}
            }}
        '''

    def transpile_if_stmt(self, node: IfBranch):
        condition = self.transpile(node.condition)

        consequence = []
        for stmt in node.consequence:
            consequence.append(self.transpile(stmt))

        alternative = []
        if node.alternative:
            for stmt in node.alternative:
                alternative.append(self.transpile(stmt))

        alternative_body = '\n'.join(alternative)
        consequence_body = '\n'.join(consequence)

        return f'''\
            if({condition}) {{
                {consequence_body}
            }} else {{
                {alternative_body}
            }}
        '''

    def transpile_return_stmt(self, node: ReturnStatement):
        returns = self.transpile(node.expr)
        return f'return {returns};'

    def transpile_func_stmt(self, node: Func):
        params = []
        statements = []

        for param in node.params:
            params.append(f'{".".join(param.typing.ident)} {param.ident}')

        for stmt in node.body:
            statements.append(self.transpile(stmt))

        func_body = '\n'.join(statements)

        return f'''\
            {self.transpile(node.returns)} {node.func_name}({",".join(params)}) {{
                {func_body}
            }}
        '''

    def transpile_type_alias_stmt(self, node: TypeAliasStatement):
        ident = node.ident
        typing = node.typing
        alias_to = self.transpile_ident_expr(typing)

        return f'typedef {ident} {alias_to}'

    def transpile_ident_expr(self, node: IdentExpr):
        return '.'.join(node.ident)

    def transpile_binary_expr(self, node: BinaryExpr):
        return f'({self.transpile(node.left)} {node.op.value} {self.transpile(node.right)})'

    def transpile_unary_expr(self, node: UnaryExpr):
        return f'{node.op.value}{self.transpile(node.expr)}'

    def transpile_condition_expr(self, node: ConditionExpr):
        return f'({self.transpile(node.condition)}) ? ({self.transpile(node.consequence)}) : ({self.transpile(node.alternative)})'

    def transpile_call_expr(self, node: CallExpr):
        args = []
        for arg in node.args:
            args.append(self.transpile(arg))

        return f'{self.transpile(node.ident)}({",".join(args)})'

    def transpile_parenthesized_expr(self, node: ParenthesizedExpr):
        return f'({self.transpile(node.expr)})'

    def transpile_number_literal(self, node: NumberLiteral):
        return f'{node.value}'

    def transpile_string_literal(self, node: StringLiteral):
        return f'"{node.value}"'

    def transpile_boolean_literal(self, node: BooleanLiteral):
        return f'{node.value}'.upper()

    def transpile_null_literal(self, node):
        return 'null'
