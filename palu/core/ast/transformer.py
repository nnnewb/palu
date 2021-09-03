from typing import Sequence

from palu import stubs
from palu.core.ast.node import (
    ASTNode,
    BinaryExpr,
    BinaryOp,
    BooleanLiteral,
    CallExpr,
    ConditionExpr,
    DeclareStatement,
    EmptyStatement,
    ExternalStatement,
    FunctionSignature,
    IdentExpr,
    IfBranch,
    LambdaExpr,
    NullLiteral,
    NumberLiteral,
    ParenthesizedExpr,
    ReturnStatement,
    StringLiteral,
    TypedIdent,
    UnaryExpr,
    UnaryOp,
    WhileLoop
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
        elif real_stmt.type == 'expr':
            return self.transform_expr(real_stmt)
        else:
            raise Exception(f'unexpected node type {node.type}')

    def transform_declare_stmt(self, node: stubs.Node):
        ident = self._transform_typed_ident(node.child_by_field_name('typed_ident'))
        initial = self.transform_expr(node.child_by_field_name('initial'))

        return DeclareStatement(ident, initial)

    def transform_external_stmt(self, node: stubs.Node):
        return ExternalStatement(self._transform_typed_ident(node.child_by_field_name('typed_ident')))

    def transform_while_stmt(self, node: stubs.Node):
        return WhileLoop(
            self.transform_expr(node.child_by_field_name('condition')),
            self._transform_codeblock(node.child_by_field_name('body')),
        )

    def transform_if_stmt(self, node: stubs.Node):
        return IfBranch(
            self.transform_expr(node.child_by_field_name('condition')),
            self._transform_codeblock(node.child_by_field_name('consequence')),
            self._transform_codeblock(node.child_by_field_name('alternative'))
        )

    def transform_return_stmt(self, node: stubs.Node):
        return ReturnStatement(self.transform_expr(node.child_by_field_name('returns')))

    def transform_expr(self, node: stubs.Node) -> ASTNode:
        real_expr = node.children[0]

        if real_expr.type == 'ident_expr':
            return self.transform_ident_expr(real_expr)
        elif real_expr.type == 'binary_expr':
            return self.transform_binary_expr(real_expr)
        elif real_expr.type == 'unary_expr':
            return self.transform_unary_expr(real_expr)
        elif real_expr.type == 'cond_expr':
            return self.transform_cond_expr(real_expr)
        elif real_expr.type == 'call_expr':
            return self.transform_call_expr(real_expr)
        elif real_expr.type == 'lambda':
            return self.transform_lambda_expr(real_expr)
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
        return BinaryExpr(
            BinaryOp(node.child_by_field_name('operator').type),
            self.transform_expr(node.child_by_field_name('left')),
            self.transform_expr(node.child_by_field_name('right')),
        )

    def transform_unary_expr(self, node: stubs.Node):
        return UnaryExpr(
            UnaryOp(node.child_by_field_name('operator').type),
            self.transform_expr(node.child_by_field_name('argument')),
        )

    def transform_cond_expr(self, node: stubs.Node):
        return ConditionExpr(
            self.transform_expr(node.child_by_field_name('condition')),
            self.transform_expr(node.child_by_field_name('consequence')),
            self.transform_expr(node.child_by_field_name('alternative')),
        )

    def transform_call_expr(self, node: stubs.Node):
        return CallExpr(
            self.transform_ident_expr(node.children[0]),
            *self._transform_argument_list(node.children[1]),
        )

    def transform_lambda_expr(self, node: stubs.Node):
        signature = node.child_by_field_name('signature')
        body = node.child_by_field_name('body')
        if body.type == 'expr':
            return LambdaExpr(self._transform_function_signature(signature), self.transform_expr(body))
        elif body.type == 'codeblock':
            return LambdaExpr(self._transform_function_signature(signature), *self._transform_codeblock(body))
        else:
            raise Exception(f'unexpected body type {body.type}')

    def transform_parenthesized_expr(self, node: stubs.Node):
        return ParenthesizedExpr(self.transform_expr(node.children[0]))

    def transform_number_literal(self, node: stubs.Node):
        return NumberLiteral(str(self.source[node.start_byte:node.end_byte], 'utf-8'))

    def transform_string_literal(self, node: stubs.Node):
        return StringLiteral(str(self.source[node.start_byte:node.end_byte], 'utf-8'))

    def transform_true_lit(self, node: stubs.Node) -> BooleanLiteral:
        return BooleanLiteral(node)

    def transform_false_lit(self, node: stubs.Node) -> BooleanLiteral:
        return BooleanLiteral(node)

    def transform_null_lit(self, _: stubs.Node) -> NullLiteral:
        return NullLiteral()

    def _transform_typed_ident(self, node: stubs.Node) -> TypedIdent:
        ident_node = node.child_by_field_name('ident')
        typing = node.child_by_field_name('typing')

        ident = str(self.source[ident_node.start_byte:ident_node.end_byte], 'utf-8')

        if typing.type == 'ident_expr':
            return TypedIdent(ident, self.transform_ident_expr(typing))
        elif typing.type == 'func_signature':
            return TypedIdent(ident, self._transform_function_signature(typing))
        else:
            raise Exception(f'unexpected typing type {typing.type}')

    def _transform_codeblock(self, node: stubs.Node) -> Sequence[ASTNode]:
        return [*map(lambda n: self.transform_statement(n), filter(lambda n: n.is_named, node.children))]

    def _transform_function_signature(self, node: stubs.Node) -> FunctionSignature:
        params = node.child_by_field_name('params')
        returns = node.child_by_field_name('returns')
        p = self._transform_params(params)

        if returns.type == 'ident_expr':
            return FunctionSignature(self.transform_ident_expr(returns), *p)
        elif returns.type == 'func_signature':
            return FunctionSignature(self._transform_function_signature(returns), *p)
        else:
            raise Exception(f'unexpected function returns type {returns.type}')

    def _transform_argument_list(self, node: stubs.Node) -> Sequence[ASTNode]:
        return [*map(lambda n: self.transform_expr(n), filter(lambda n: n.is_named, node.children))]

    def _transform_params(self, node: stubs.Node) -> Sequence[TypedIdent]:
        return [*map(lambda n: self._transform_typed_ident(n), filter(lambda n: n.is_named, node.children))]
