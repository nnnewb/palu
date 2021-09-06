from typing import List, Sequence

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
    SourceFile,
    StringLiteral,
    TypeAliasStatement,
    TypedIdent,
    UnaryExpr,
    UnaryOp,
    WhileLoop,
    FuncDecl
)


def transform(tree: stubs.Tree, source: bytes) -> SourceFile:
    source = source
    statements: List[ASTNode] = []
    root = tree.root_node
    for stmt in root.children:
        statements.append(transform_statement(stmt, source))

    return SourceFile(statements)


def transform_statement(node: stubs.Node, source: bytes) -> ASTNode:
    real_stmt = node.children[0]
    if real_stmt.type == 'empty':
        return EmptyStatement()
    elif real_stmt.type == 'declare':
        return transform_declare_stmt(real_stmt, source)
    elif real_stmt.type == 'external':
        return transform_external_stmt(real_stmt, source)
    elif real_stmt.type == 'while':
        return transform_while_stmt(real_stmt, source)
    elif real_stmt.type == 'if':
        return transform_if_stmt(real_stmt, source)
    elif real_stmt.type == 'return':
        return transform_return_stmt(real_stmt, source)
    elif real_stmt.type == 'type_alias':
        return transform_type_alias(real_stmt, source)
    elif real_stmt.type == 'func':
        return transform_func_stmt(real_stmt, source)
    elif real_stmt.type == 'expr':
        return transform_expr(real_stmt, source)
    elif real_stmt.type == 'mod':
        return transform_mod(real_stmt, source)
    else:
        raise Exception(f'unexpected node type {real_stmt.type}')


def transform_mod(node: stubs.Node, source: bytes):
    ident_node = node.child_by_field_name('name')
    assert ident_node
    return ModDeclare(get_text(ident_node, source))


def transform_declare_stmt(node: stubs.Node, source: bytes):
    typed_ident = node.child_by_field_name('typed_ident')
    initial_node = node.child_by_field_name('initial')

    assert typed_ident
    assert initial_node

    ident = _transform_typed_ident(typed_ident, source)
    initial_value = transform_expr(initial_node, source)

    return DeclareStatement(ident, initial_value)


def transform_external_stmt(node: stubs.Node, source: bytes):
    real_stmt = node.children[0]
    if real_stmt.type == 'external_variable':
        typed_ident = real_stmt.child_by_field_name('typed_ident')
        assert typed_ident
        return ExternalStatement(_transform_typed_ident(typed_ident, source))
    elif real_stmt.type == 'external_function':
        func_name_node = real_stmt.child_by_field_name('func_name')
        assert func_name_node
        func_name = get_text(func_name_node, source)

        params_node = real_stmt.child_by_field_name('params')
        assert params_node
        params = _transform_params(params_node, source)

        returns_node = real_stmt.child_by_field_name('returns')
        assert returns_node
        returns = transform_ident_expr(returns_node, source)

        return ExternalStatement(FuncDecl(func_name, params, returns))


def transform_while_stmt(node: stubs.Node, source: bytes):
    condition = node.child_by_field_name('condition')
    body = node.child_by_field_name('body')

    assert condition
    assert body

    return WhileLoop(transform_expr(condition, source), _transform_codeblock(body, source))


def transform_if_stmt(node: stubs.Node, source: bytes):
    condition = node.child_by_field_name('condition')
    consequence = node.child_by_field_name('consequence')
    alternative = node.child_by_field_name('alternative')

    assert condition
    assert consequence
    if alternative:
        return If(transform_expr(condition, source), _transform_codeblock(consequence, source), _transform_codeblock(alternative, source))
    else:
        return If(transform_expr(condition, source), _transform_codeblock(consequence, source), None)


def transform_return_stmt(node: stubs.Node, source: bytes):
    returns = node.child_by_field_name('returns')

    assert returns

    return ReturnStatement(transform_expr(returns, source))


def transform_type_alias(node: stubs.Node, source: bytes):
    ident = node.child_by_field_name('ident')
    typing = node.child_by_field_name('typing')

    assert ident
    assert typing

    return TypeAliasStatement(get_text(ident, source), transform_ident_expr(typing, source))


def transform_expr(node: stubs.Node, source: bytes) -> ASTNode:
    real_expr = node.children[0]

    if real_expr.type == 'ident_expr':
        return transform_ident_expr(real_expr, source)
    elif real_expr.type == 'binary_expr':
        return transform_binary_expr(real_expr, source)
    elif real_expr.type == 'unary_expr':
        return transform_unary_expr(real_expr, source)
    elif real_expr.type == 'cond_expr':
        return transform_condition_expr(real_expr, source)
    elif real_expr.type == 'call_expr':
        return transform_call_expr(real_expr, source)
    elif real_expr.type == 'parenthesized_expr':
        return transform_parenthesized_expr(real_expr, source)
    elif real_expr.type == 'number_literal':
        return transform_number_literal(real_expr, source)
    elif real_expr.type == 'string_literal':
        return transform_string_literal(real_expr, source)
    elif real_expr.type == 'true_lit':
        return transform_true_lit(real_expr, source)
    elif real_expr.type == 'false_lit':
        return transform_false_lit(real_expr, source)
    elif real_expr.type == 'null_lit':
        return transform_null_lit(real_expr)
    else:
        raise Exception(f'unexpected expr type {real_expr.type}')


def transform_ident_expr(node: stubs.Node, source: bytes):
    return IdentExpr(*map(lambda n: str(source[n.start_byte:n.end_byte], 'utf-8'), node.children))


def transform_binary_expr(node: stubs.Node, source: bytes):
    operator = node.child_by_field_name('operator')
    left = node.child_by_field_name('left')
    right = node.child_by_field_name('right')

    assert operator
    assert left
    assert right

    return BinaryExpr(BinaryOp(operator.type), transform_expr(left, source), transform_expr(right, source))


def transform_unary_expr(node: stubs.Node, source: bytes):
    operator = node.child_by_field_name('operator')
    argument = node.child_by_field_name('argument')

    assert operator
    assert argument

    return UnaryExpr(UnaryOp(operator.type), transform_expr(argument, source))


def transform_condition_expr(node: stubs.Node, source: bytes):
    condition = node.child_by_field_name('condition')
    consequence = node.child_by_field_name('consequence')
    alternative = node.child_by_field_name('alternative')

    assert condition
    assert consequence
    assert alternative

    return ConditionExpr(transform_expr(condition, source), transform_expr(consequence, source), transform_expr(alternative, source))


def transform_call_expr(node: stubs.Node, source: bytes):
    func_name = node.child_by_field_name('func_name')
    args = node.child_by_field_name('args')

    assert func_name
    assert args

    return CallExpr(transform_ident_expr(func_name, source), *_transform_argument_list(args, source))


def transform_func_stmt(node: stubs.Node, source: bytes):
    func_name = node.child_by_field_name('func_name')
    params = node.child_by_field_name('params')
    returns = node.child_by_field_name('returns')
    body = node.child_by_field_name('body')

    assert func_name
    assert body
    assert params
    assert returns

    return Func(
        get_text(func_name, source),
        _transform_params(params, source),
        transform_ident_expr(returns, source),
        _transform_codeblock(body, source)
    )


def transform_parenthesized_expr(node: stubs.Node, source: bytes):
    expr = node.child_by_field_name('expr')

    assert expr

    return ParenthesizedExpr(transform_expr(expr, source))


def transform_number_literal(node: stubs.Node, source: bytes):
    return NumberLiteral(str(source[node.start_byte:node.end_byte], 'utf-8'))


def transform_string_literal(node: stubs.Node, source: bytes):
    return StringLiteral(str(source[node.start_byte:node.end_byte], 'utf-8'))


def transform_true_lit(node: stubs.Node, source: bytes) -> BooleanLiteral:
    return BooleanLiteral(str(source[node.start_byte:node.end_byte], 'utf-8'))


def transform_false_lit(node: stubs.Node, source: bytes) -> BooleanLiteral:
    return BooleanLiteral(str(source[node.start_byte:node.end_byte], 'utf-8'))


def transform_null_lit(_: stubs.Node) -> NullLiteral:
    return NullLiteral()


def _transform_typed_ident(node: stubs.Node, source: bytes) -> TypedIdent:
    ident = node.child_by_field_name('ident')
    typing = node.child_by_field_name('typing')

    assert ident
    assert typing

    return TypedIdent(get_text(ident, source), transform_ident_expr(typing, source))


def _transform_codeblock(node: stubs.Node, source: bytes) -> Sequence[ASTNode]:
    return [*map(lambda n: transform_statement(n, source), filter(lambda n: n.is_named, node.children))]


def _transform_argument_list(node: stubs.Node, source: bytes) -> Sequence[ASTNode]:
    return [*map(lambda n: transform_expr(n, source), filter(lambda n: n.is_named, node.children))]


def _transform_params(node: stubs.Node, source: bytes) -> Sequence[TypedIdent]:
    return [*map(lambda n: _transform_typed_ident(n, source), filter(lambda n: n.is_named, node.children))]


def get_text(node: stubs.Node, source: bytes) -> str:
    return str(source[node.start_byte:node.end_byte], 'utf-8')
