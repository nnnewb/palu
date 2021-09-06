from typing import List, Sequence

from palu import stubs
from palu.symbol import Symbol, SymbolKind, Typing, predefined
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
    SourceFile,
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
        self.stack: List[Symbol] = []
        self.stack.append(Symbol('', SymbolKind.Global))

    def transform(self, tree: stubs.Tree, source: bytes) -> SourceFile:
        self.stack = []
        statements: List[ASTNode] = []
        root = tree.root_node
        for stmt in root.children:
            statements.append(self.transform_statement(stmt, source))

        return SourceFile(statements)

    def transform_statement(self, node: stubs.Node, source: bytes) -> ASTNode:
        real_stmt = node.children[0]
        if real_stmt.type == 'empty':
            return EmptyStatement()
        elif real_stmt.type == 'declare':
            return self.transform_declare_stmt(real_stmt, source)
        elif real_stmt.type == 'external':
            return self.transform_external_stmt(real_stmt, source)
        elif real_stmt.type == 'while':
            return self.transform_while_stmt(real_stmt, source)
        elif real_stmt.type == 'if':
            return self.transform_if_stmt(real_stmt, source)
        elif real_stmt.type == 'return':
            return self.transform_return_stmt(real_stmt, source)
        elif real_stmt.type == 'type_alias':
            return self.transform_type_alias(real_stmt, source)
        elif real_stmt.type == 'func':
            return self.transform_func_stmt(real_stmt, source)
        elif real_stmt.type == 'expr':
            return self.transform_expr(real_stmt, source)
        elif real_stmt.type == 'mod':
            return self.transform_mod(real_stmt, source)
        else:
            raise Exception(f'unexpected node type {real_stmt.type}')

    def transform_mod(self, node: stubs.Node, source: bytes):
        ident_node = node.child_by_field_name('name')
        assert ident_node
        name = self.get_text(ident_node, source)
        sym = Symbol(name, SymbolKind.Module)
        self.stack.append(sym)
        return ModDeclare(name, sym)

    def transform_declare_stmt(self, node: stubs.Node, source: bytes):
        typed_ident = node.child_by_field_name('typed_ident')
        initial_node = node.child_by_field_name('initial')

        assert typed_ident
        assert initial_node

        ident = self._transform_typed_ident(typed_ident, source)
        initial_value = self.transform_expr(initial_node, source)

        assert len(self.stack) > 0
        parent = self.stack[len(self.stack)-1]

        sym = Symbol(ident.ident, SymbolKind.Var, Typing.from_type_ident(parent, '.'.join(ident.typing.ident)), parent)
        return DeclareStatement(ident, initial_value, sym)

    def transform_external_stmt(self, node: stubs.Node, source: bytes):
        assert len(self.stack) > 0, 'stack size should always greater than 0'
        parent: Symbol = self.stack[len(self.stack)-1]
        real_stmt = node.children[0]
        if real_stmt.type == 'external_variable':
            typed_ident_node = real_stmt.child_by_field_name('typed_ident')
            assert typed_ident_node
            typed_ident = self._transform_typed_ident(typed_ident_node, source)

            typing_str = '.'.join(typed_ident.typing.ident)
            sym = Symbol(typed_ident.ident, SymbolKind.Var, Typing.from_type_ident(parent, typing_str), parent)
            return ExternalStatement(typed_ident, sym)
        elif real_stmt.type == 'external_function':
            func_name_node = real_stmt.child_by_field_name('func_name')
            assert func_name_node
            func_name = self.get_text(func_name_node, source)

            params_node = real_stmt.child_by_field_name('params')
            assert params_node
            params = self._transform_params(params_node, source)

            returns_node = real_stmt.child_by_field_name('returns')
            assert returns_node
            returns = self.transform_ident_expr(returns_node, source)

            t = Typing.from_func_signature(parent, [*map(lambda i: '.'.join(i.typing.ident), params)], '.'.join(returns.ident))
            sym = Symbol(func_name, SymbolKind.Func, t, parent)

            return ExternalStatement(FuncDecl(func_name, params, returns), sym)

    def transform_while_stmt(self, node: stubs.Node, source: bytes):
        condition = node.child_by_field_name('condition')
        body = node.child_by_field_name('body')

        assert condition
        assert body

        assert len(self.stack) > 0
        parent = self.stack[len(self.stack)-1]
        self.stack.append(Symbol('while', SymbolKind.CodeBlock, parent=parent))
        cb = self._transform_codeblock(body, source)
        self.stack.pop()

        return WhileLoop(self.transform_expr(condition, source), cb)

    def transform_if_stmt(self, node: stubs.Node, source: bytes):
        condition = node.child_by_field_name('condition')
        consequence = node.child_by_field_name('consequence')
        alternative = node.child_by_field_name('alternative')

        assert condition
        assert consequence
        if alternative:
            return If(self.transform_expr(condition, source), self._transform_codeblock(consequence, source), self._transform_codeblock(alternative, source))
        else:
            return If(self.transform_expr(condition, source), self._transform_codeblock(consequence, source), None)

    def transform_return_stmt(self, node: stubs.Node, source: bytes):
        returns = node.child_by_field_name('returns')

        assert returns

        return ReturnStatement(self.transform_expr(returns, source))

    def transform_type_alias(self, node: stubs.Node, source: bytes):
        ident = node.child_by_field_name('ident')
        typing = node.child_by_field_name('typing')

        assert ident
        assert typing

        return TypeAliasStatement(self.get_text(ident, source), self.transform_ident_expr(typing, source))

    def transform_expr(self, node: stubs.Node, source: bytes) -> ASTNode:
        real_expr = node.children[0]

        if real_expr.type == 'ident_expr':
            return self.transform_ident_expr(real_expr, source)
        elif real_expr.type == 'binary_expr':
            return self.transform_binary_expr(real_expr, source)
        elif real_expr.type == 'unary_expr':
            return self.transform_unary_expr(real_expr, source)
        elif real_expr.type == 'cond_expr':
            return self.transform_condition_expr(real_expr, source)
        elif real_expr.type == 'call_expr':
            return self.transform_call_expr(real_expr, source)
        elif real_expr.type == 'parenthesized_expr':
            return self.transform_parenthesized_expr(real_expr, source)
        elif real_expr.type == 'number_literal':
            return self.transform_number_literal(real_expr, source)
        elif real_expr.type == 'string_literal':
            return self.transform_string_literal(real_expr, source)
        elif real_expr.type == 'true_lit':
            return self.transform_true_lit(real_expr, source)
        elif real_expr.type == 'false_lit':
            return self.transform_false_lit(real_expr, source)
        elif real_expr.type == 'null_lit':
            return self.transform_null_lit(real_expr)
        else:
            raise Exception(f'unexpected expr type {real_expr.type}')

    def transform_ident_expr(self, node: stubs.Node, source: bytes):
        return IdentExpr(*map(lambda n: str(source[n.start_byte:n.end_byte], 'utf-8'), node.children))

    def transform_binary_expr(self, node: stubs.Node, source: bytes):
        operator = node.child_by_field_name('operator')
        left = node.child_by_field_name('left')
        right = node.child_by_field_name('right')

        assert operator
        assert left
        assert right

        return BinaryExpr(BinaryOp(operator.type), self.transform_expr(left, source), self.transform_expr(right, source))

    def transform_unary_expr(self, node: stubs.Node, source: bytes):
        operator = node.child_by_field_name('operator')
        argument = node.child_by_field_name('argument')

        assert operator
        assert argument

        return UnaryExpr(UnaryOp(operator.type), self.transform_expr(argument, source))

    def transform_condition_expr(self, node: stubs.Node, source: bytes):
        condition = node.child_by_field_name('condition')
        consequence = node.child_by_field_name('consequence')
        alternative = node.child_by_field_name('alternative')

        assert condition
        assert consequence
        assert alternative

        return ConditionExpr(self.transform_expr(condition, source), self.transform_expr(consequence, source), self.transform_expr(alternative, source))

    def transform_call_expr(self, node: stubs.Node, source: bytes):
        func_name = node.child_by_field_name('func_name')
        args = node.child_by_field_name('args')

        assert func_name
        assert args

        return CallExpr(self.transform_ident_expr(func_name, source), *self._transform_argument_list(args, source))

    def transform_func_stmt(self, node: stubs.Node, source: bytes):
        func_name = node.child_by_field_name('func_name')
        params = node.child_by_field_name('params')
        returns = node.child_by_field_name('returns')
        body = node.child_by_field_name('body')

        assert func_name
        assert body
        assert params
        assert returns

        return Func(
            self.get_text(func_name, source),
            self._transform_params(params, source),
            self.transform_ident_expr(returns, source),
            self._transform_codeblock(body, source)
        )

    def transform_parenthesized_expr(self, node: stubs.Node, source: bytes):
        expr = node.child_by_field_name('expr')

        assert expr

        return ParenthesizedExpr(self.transform_expr(expr, source))

    def transform_number_literal(self, node: stubs.Node, source: bytes):
        return NumberLiteral(str(source[node.start_byte:node.end_byte], 'utf-8'))

    def transform_string_literal(self, node: stubs.Node, source: bytes):
        return StringLiteral(str(source[node.start_byte:node.end_byte], 'utf-8'))

    def transform_true_lit(self, node: stubs.Node, source: bytes) -> BooleanLiteral:
        return BooleanLiteral(str(source[node.start_byte:node.end_byte], 'utf-8'))

    def transform_false_lit(self, node: stubs.Node, source: bytes) -> BooleanLiteral:
        return BooleanLiteral(str(source[node.start_byte:node.end_byte], 'utf-8'))

    def transform_null_lit(self, _: stubs.Node) -> NullLiteral:
        return NullLiteral()

    def _transform_typed_ident(self, node: stubs.Node, source: bytes) -> TypedIdent:
        ident = node.child_by_field_name('ident')
        typing = node.child_by_field_name('typing')

        assert ident
        assert typing

        return TypedIdent(self.get_text(ident, source), self.transform_ident_expr(typing, source))

    def _transform_codeblock(self, node: stubs.Node, source: bytes) -> Sequence[ASTNode]:
        return [*map(lambda n: self.transform_statement(n, source), filter(lambda n: n.is_named, node.children))]

    def _transform_argument_list(self, node: stubs.Node, source: bytes) -> Sequence[ASTNode]:
        return [*map(lambda n: self.transform_expr(n, source), filter(lambda n: n.is_named, node.children))]

    def _transform_params(self, node: stubs.Node, source: bytes) -> Sequence[TypedIdent]:
        return [*map(lambda n: self._transform_typed_ident(n, source), filter(lambda n: n.is_named, node.children))]

    def get_text(self, node: stubs.Node, source: bytes) -> str:
        return str(source[node.start_byte:node.end_byte], 'utf-8')
