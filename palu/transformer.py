from typing import Sequence

from palu import stubs
from palu.ast import (
    ASTNode,
    BinaryExpr,
    BinaryOp,
    BooleanLiteral,
    CallExpr,
    ConditionExpr,
    DeclareStatement,
    EmptyStatement,
    ExternalStatement,
    Func,
    IdentExpr,
    If,
    ModDeclare,
    NullLiteral,
    NumberLiteral,
    ParenthesizedExpr,
    ReturnStatement,
    StringLiteral,
    TypeAliasStatement,
    TypedIdent,
    UnaryExpr,
    UnaryOp,
    WhileLoop,
    FuncDecl
)


class Transformer(object):
    def __init__(self) -> None:
        super().__init__()
        self.source = b''

    def transform(self, source: bytes, tree: stubs.Tree) -> Sequence[ASTNode]:
        self.source = source
        result = []
        root = tree.root_node
        for stmt in root.children:
            result.append(self.transform_statement(stmt))

        return result

    def transform_statement(self, node: stubs.Node) -> ASTNode:
        real_stmt = node.children[0]
        if real_stmt.type == 'empty':
            return EmptyStatement()
        elif real_stmt.type == 'declare':
            return self.transform_declare_stmt(real_stmt)
        elif real_stmt.type == 'external':
            return self.transform_external_stmt(real_stmt)
        elif real_stmt.type == 'while':
            return self.transform_while_stmt(real_stmt)
        elif real_stmt.type == 'if':
            return self.transform_if_stmt(real_stmt)
        elif real_stmt.type == 'return':
            return self.transform_return_stmt(real_stmt)
        elif real_stmt.type == 'type_alias':
            return self.transform_type_alias(real_stmt)
        elif real_stmt.type == 'func':
            return self.transform_func_stmt(real_stmt)
        elif real_stmt.type == 'expr':
            return self.transform_expr(real_stmt)
        elif real_stmt.type == 'mod':
            return self.transform_mod(real_stmt)
        else:
            raise Exception(f'unexpected node type {real_stmt.type}')

    def transform_mod(self, node: stubs.Node):
        ident_node = node.child_by_field_name('name')
        assert ident_node
        return ModDeclare(self._extract_text(ident_node))

    def transform_declare_stmt(self, node: stubs.Node):
        typed_ident = node.child_by_field_name('typed_ident')
        initial_node = node.child_by_field_name('initial')

        assert typed_ident
        assert initial_node

        ident = self._transform_typed_ident(typed_ident)
        initial_value = self.transform_expr(initial_node)

        return DeclareStatement(ident, initial_value)

    def transform_external_stmt(self, node: stubs.Node):
        real_stmt = node.children[0]
        if real_stmt.type == 'external_variable':
            typed_ident = real_stmt.child_by_field_name('typed_ident')
            assert typed_ident
            return ExternalStatement(self._transform_typed_ident(typed_ident))
        elif real_stmt.type == 'external_function':
            func_name_node = real_stmt.child_by_field_name('func_name')
            assert func_name_node
            func_name = self._extract_text(func_name_node)

            params_node = real_stmt.child_by_field_name('params')
            assert params_node
            params = self._transform_params(params_node)

            returns_node = real_stmt.child_by_field_name('returns')
            assert returns_node
            returns = self.transform_ident_expr(returns_node)

            return ExternalStatement(FuncDecl(func_name, params, returns))

    def transform_while_stmt(self, node: stubs.Node):
        condition = node.child_by_field_name('condition')
        body = node.child_by_field_name('body')

        assert condition
        assert body

        return WhileLoop(self.transform_expr(condition), self._transform_codeblock(body))

    def transform_if_stmt(self, node: stubs.Node):
        condition = node.child_by_field_name('condition')
        consequence = node.child_by_field_name('consequence')
        alternative = node.child_by_field_name('alternative')

        assert condition
        assert consequence
        if alternative:
            return If(self.transform_expr(condition), self._transform_codeblock(consequence), self._transform_codeblock(alternative))
        else:
            return If(self.transform_expr(condition), self._transform_codeblock(consequence), None)

    def transform_return_stmt(self, node: stubs.Node):
        returns = node.child_by_field_name('returns')

        assert returns

        return ReturnStatement(self.transform_expr(returns))

    def transform_type_alias(self, node: stubs.Node):
        ident = node.child_by_field_name('ident')
        typing = node.child_by_field_name('typing')

        assert ident
        assert typing

        return TypeAliasStatement(self._extract_text(ident), self.transform_ident_expr(typing))

    def transform_expr(self, node: stubs.Node) -> ASTNode:
        real_expr = node.children[0]

        if real_expr.type == 'ident_expr':
            return self.transform_ident_expr(real_expr)
        elif real_expr.type == 'binary_expr':
            return self.transform_binary_expr(real_expr)
        elif real_expr.type == 'unary_expr':
            return self.transform_unary_expr(real_expr)
        elif real_expr.type == 'cond_expr':
            return self.transform_condition_expr(real_expr)
        elif real_expr.type == 'call_expr':
            return self.transform_call_expr(real_expr)
        elif real_expr.type == 'parenthesized_expr':
            return self.transform_parenthesized_expr(real_expr)
        elif real_expr.type == 'number_literal':
            return self.transform_number_literal(real_expr)
        elif real_expr.type == 'string_literal':
            return self.transform_string_literal(real_expr)
        elif real_expr.type == 'true_lit':
            return self.transform_true_lit(real_expr)
        elif real_expr.type == 'false_lit':
            return self.transform_false_lit(real_expr)
        elif real_expr.type == 'null_lit':
            return self.transform_null_lit(real_expr)
        else:
            raise Exception(f'unexpected expr type {real_expr.type}')

    def transform_ident_expr(self, node: stubs.Node):
        return IdentExpr(*map(lambda n: str(self.source[n.start_byte:n.end_byte], 'utf-8'), node.children))

    def transform_binary_expr(self, node: stubs.Node):
        operator = node.child_by_field_name('operator')
        left = node.child_by_field_name('left')
        right = node.child_by_field_name('right')

        assert operator
        assert left
        assert right

        return BinaryExpr(BinaryOp(operator.type), self.transform_expr(left), self.transform_expr(right))

    def transform_unary_expr(self, node: stubs.Node):
        operator = node.child_by_field_name('operator')
        argument = node.child_by_field_name('argument')

        assert operator
        assert argument

        return UnaryExpr(UnaryOp(operator.type), self.transform_expr(argument))

    def transform_condition_expr(self, node: stubs.Node):
        condition = node.child_by_field_name('condition')
        consequence = node.child_by_field_name('consequence')
        alternative = node.child_by_field_name('alternative')

        assert condition
        assert consequence
        assert alternative

        return ConditionExpr(self.transform_expr(condition), self.transform_expr(consequence), self.transform_expr(alternative))

    def transform_call_expr(self, node: stubs.Node):
        func_name = node.child_by_field_name('func_name')
        args = node.child_by_field_name('args')

        assert func_name
        assert args

        return CallExpr(self.transform_ident_expr(func_name), *self._transform_argument_list(args))

    def transform_func_stmt(self, node: stubs.Node):
        func_name = node.child_by_field_name('func_name')
        params = node.child_by_field_name('params')
        returns = node.child_by_field_name('returns')
        body = node.child_by_field_name('body')

        assert func_name
        assert body
        assert params
        assert returns

        return Func(
            self._extract_text(func_name),
            self._transform_params(params),
            self.transform_ident_expr(returns),
            self._transform_codeblock(body)
        )

    def transform_parenthesized_expr(self, node: stubs.Node):
        expr = node.child_by_field_name('expr')

        assert expr

        return ParenthesizedExpr(self.transform_expr(expr))

    def transform_number_literal(self, node: stubs.Node):
        return NumberLiteral(str(self.source[node.start_byte:node.end_byte], 'utf-8'))

    def transform_string_literal(self, node: stubs.Node):
        return StringLiteral(str(self.source[node.start_byte:node.end_byte], 'utf-8'))

    def transform_true_lit(self, node: stubs.Node) -> BooleanLiteral:
        return BooleanLiteral(str(self.source[node.start_byte:node.end_byte], 'utf-8'))

    def transform_false_lit(self, node: stubs.Node) -> BooleanLiteral:
        return BooleanLiteral(str(self.source[node.start_byte:node.end_byte], 'utf-8'))

    def transform_null_lit(self, _: stubs.Node) -> NullLiteral:
        return NullLiteral()

    def _transform_typed_ident(self, node: stubs.Node) -> TypedIdent:
        ident_node = node.child_by_field_name('ident')
        typing = node.child_by_field_name('typing')

        assert ident_node
        assert typing

        ident = str(self.source[ident_node.start_byte:ident_node.end_byte], 'utf-8')

        return TypedIdent(ident, self.transform_ident_expr(typing))

    def _transform_codeblock(self, node: stubs.Node) -> Sequence[ASTNode]:
        return [*map(lambda n: self.transform_statement(n), filter(lambda n: n.is_named, node.children))]

    def _transform_argument_list(self, node: stubs.Node) -> Sequence[ASTNode]:
        return [*map(lambda n: self.transform_expr(n), filter(lambda n: n.is_named, node.children))]

    def _transform_params(self, node: stubs.Node) -> Sequence[TypedIdent]:
        return [*map(lambda n: self._transform_typed_ident(n), filter(lambda n: n.is_named, node.children))]

    def _extract_text(self, node: stubs.Node) -> str:
        return str(self.source[node.start_byte:node.end_byte], 'utf-8')
