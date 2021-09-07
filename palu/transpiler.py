from abc import ABCMeta
from textwrap import dedent, indent
from typing import List

from palu.ast import (
    ASTNode,
    AssignmentExpr,
    BinaryExpr,
    BooleanLiteral,
    CallExpr,
    ConditionExpr,
    DeclareStatement,
    ExternalStatement,
    Func,
    IdentExpr,
    If,
    ModDeclare,
    NullLiteral,
    NumberLiteral,
    ParenthesizedExpr,
    ReturnStatement,
    SourceFile,
    StringLiteral,
    TypeAliasStatement,
    UnaryExpr,
    WhileLoop
)


class Transpiler(metaclass=ABCMeta):
    def __init__(self) -> None:
        super().__init__()

    def transpile(self, node: ASTNode, semi=True):
        semi_sym = ';' if semi else ''
        if isinstance(node, SourceFile):
            return self.transpile_source_file(node)
        if isinstance(node, DeclareStatement):
            return self.transpile_declare_stmt(node) + semi_sym
        elif isinstance(node, WhileLoop):
            return self.transpile_while_stmt(node)
        elif isinstance(node, If):
            return self.transpile_if_stmt(node)
        elif isinstance(node, ReturnStatement):
            return self.transpile_return_stmt(node) + semi_sym
        elif isinstance(node, Func):
            return self.transpile_func_stmt(node)
        elif isinstance(node, TypeAliasStatement):
            return self.transpile_type_alias_stmt(node) + semi_sym
        elif isinstance(node, IdentExpr):
            return self.transpile_ident_expr(node) + semi_sym
        elif isinstance(node, BinaryExpr):
            return self.transpile_binary_expr(node) + semi_sym
        elif isinstance(node, UnaryExpr):
            return self.transpile_unary_expr(node) + semi_sym
        elif isinstance(node, ConditionExpr):
            return self.transpile_condition_expr(node) + semi_sym
        elif isinstance(node, CallExpr):
            return self.transpile_call_expr(node) + semi_sym
        elif isinstance(node, ParenthesizedExpr):
            return self.transpile_parenthesized_expr(node) + semi_sym
        elif isinstance(node, AssignmentExpr):
            return self.transpile_assignment_expr(node) + semi_sym
        elif isinstance(node, NumberLiteral):
            return self.transpile_number_literal(node) + semi_sym
        elif isinstance(node, StringLiteral):
            return self.transpile_string_literal(node) + semi_sym
        elif isinstance(node, BooleanLiteral):
            return self.transpile_boolean_literal(node) + semi_sym
        elif isinstance(node, NullLiteral):
            return self.transpile_null_literal(node) + semi_sym
        elif isinstance(node, ExternalStatement):
            return self.transpile_external_stmt(node)
        elif isinstance(node, ModDeclare):
            return self.transpile_mod_declare(node)
        else:
            raise Exception(f'unexpected ast node {node}')

    def transpile_source_file(self, node: SourceFile):
        result: List[str] = []

        for stmt in node.statements:
            result.append(self.transpile(stmt))

        return '\n'.join(result)

    def transpile_mod_declare(self, node: ModDeclare):
        return f'// mod {node.name}'

    def transpile_declare_stmt(self, node: DeclareStatement):
        result = f'{node.typed_ident.typing.sym.c_type} {node.typed_ident.ident}'
        if node.initial_value is not None:
            result += f' = {self.transpile(node.initial_value,semi=False)}'
        return result

    def transpile_external_stmt(self, node: ExternalStatement):
        return f'// {node.s_expr}'

    def transpile_while_stmt(self, node: WhileLoop):
        statements = []
        for stmt in node.body:
            statements.append(self.transpile(stmt))

        body = '\n'.join(statements)

        return dedent(f'''\
        while({self.transpile(node.condition, False)}) {{
        {indent(body, "    ")}
        }}''')

    def transpile_if_stmt(self, node: If):
        condition = self.transpile(node.condition, False)

        consequence = []
        for stmt in node.consequence:
            consequence.append(self.transpile(stmt))

        alternative = []
        if node.alternative:
            for stmt in node.alternative:
                alternative.append(self.transpile(stmt))

        alternative_body = '\n'.join(alternative)
        consequence_body = '\n'.join(consequence)
        if alternative:
            alternative_body = f'''\
            else {{
            {indent(alternative_body,"    ")}
            }}'''

        return dedent(f'''\
        if({condition}) {{
        {indent(consequence_body,"    ")}
        }} ''' + alternative_body)

    def transpile_return_stmt(self, node: ReturnStatement):
        returns = self.transpile(node.expr, False)
        return f'return {returns}'

    def transpile_func_stmt(self, node: Func):
        params = []
        statements = []

        assert node.sym.typing is not None
        assert node.sym.typing.returns is not None
        assert node.sym.typing.returns.ref is not None

        for param in node.params:
            assert param.sym.typing is not None
            assert param.sym.typing.ref is not None
            params.append(f'{param.sym.typing.ref.c_type} {param.ident}')

        for stmt in node.body:
            statements.append(self.transpile(stmt))

        func_body = '\n'.join(statements)

        return dedent(f'''\
        {node.sym.typing.returns.ref.c_type} {node.func_name}({",".join(params)}) {{
        {indent(func_body, "    ")}
        }}''')

    def transpile_type_alias_stmt(self, node: TypeAliasStatement):
        ident = node.ident
        typing = node.typing
        alias_to = self.transpile_ident_expr(typing)

        return f'typedef {ident} {alias_to}'

    def transpile_ident_expr(self, node: IdentExpr):
        return '.'.join(node.ident)

    def transpile_binary_expr(self, node: BinaryExpr):
        return f'({self.transpile(node.left, False)} {node.op.value} {self.transpile(node.right, False)})'

    def transpile_unary_expr(self, node: UnaryExpr):
        return f'{node.op.value}{self.transpile(node.expr, False)}'

    def transpile_condition_expr(self, node: ConditionExpr):
        return f'({self.transpile(node.condition, False)}) ?' + \
            ' ({self.transpile(node.consequence, False)}) :' + \
            ' ({self.transpile(node.alternative, False)})'

    def transpile_call_expr(self, node: CallExpr):
        args = []
        for arg in node.args:
            args.append(self.transpile(arg, False))

        return f'{self.transpile(node.ident, False)}({",".join(args)})'

    def transpile_parenthesized_expr(self, node: ParenthesizedExpr):
        return f'({self.transpile(node.expr, False)})'

    def transpile_assignment_expr(self, node: AssignmentExpr):
        return f'{self.transpile_ident_expr(node.left)} {node.op.value} {self.transpile(node.right, semi=False)}'

    def transpile_number_literal(self, node: NumberLiteral):
        return f'{node.value}'

    def transpile_string_literal(self, node: StringLiteral):
        return f'{node.value}'

    def transpile_boolean_literal(self, node: BooleanLiteral):
        return f'{node.value}'.upper()

    def transpile_null_literal(self, node):
        return 'null'
