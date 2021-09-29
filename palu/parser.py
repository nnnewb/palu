from typing import List, Sequence, Union

from tree_sitter import Language
from tree_sitter import Node
from tree_sitter import Node as TSNode
from tree_sitter import Parser as TSParser
from tree_sitter import Tree

from palu.ast.expr import (AssignmentExpr, BinaryExpr, CallExpr, ConditionExpr,
                           IdentExpr, ParenthesizedExpr, TypedIdent, UnaryExpr)
from palu.ast.func import Func
from palu.ast.literals import (BooleanLiteral, NullLiteral, NumberLiteral,
                               StringLiteral)
from palu.ast.node import Node as PaluNode
from palu.ast.op import AsssignmentOp, BinaryOp, UnaryOp
from palu.ast.source import ModDeclare, SourceFile
from palu.ast.statements import (DeclareStatement, EmptyStatement,
                                 ExternalFunctionSpec, ExternalStatement,
                                 ExternalVariableSpec, If, ReturnStatement,
                                 TypeAliasStatement, WhileLoop)

lang_lib = 'build/palu.dll'

Language.build_library(lang_lib, ['tree-sitter-palu'])
palu = Language(lang_lib, 'palu')


class PaluSyntaxError(Exception):
    def __init__(self, tree, line, column) -> None:
        super().__init__((line, column))
        self.tree = tree
        self.line = line
        self.column = column


_parser = TSParser()
_parser.set_language(palu)


def _validate_recursive(tree: Tree, node: Node):
    if node.has_error or node.is_missing:
        raise PaluSyntaxError(tree, *node.start_point)

    for child in node.children:
        _validate_recursive(tree, child)


def parse(source: bytes) -> SourceFile:
    transformer = Transformer()
    tree = _parser.parse(source)
    _validate_recursive(tree, tree.root_node)
    return transformer.transform(tree, source)


class Transformer(object):
    def __init__(self) -> None:
        super().__init__()

    def transform(self, tree: Tree, source: bytes) -> SourceFile:
        statements: List[PaluNode] = []
        root = tree.root_node
        for stmt in root.children:
            statements.append(self.transform_statement(stmt, source))

        return SourceFile(root.start_point, root.end_point, statements)

    def transform_statement(self, node: TSNode, source: bytes) -> PaluNode:
        real_stmt = node.children[0]
        if real_stmt.type == 'empty':
            return EmptyStatement(real_stmt.start_point, real_stmt.end_point)
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
        elif real_stmt.type == 'mod':
            return self.transform_mod(real_stmt, source)
        elif real_stmt.type == 'call_expr':
            return self.transform_call_expr(real_stmt, source)
        else:
            raise Exception(f'unexpected node type {real_stmt.type}')

    def transform_mod(self, node: TSNode, source: bytes):
        ident_node = node.child_by_field_name('name')
        assert ident_node
        name = self.get_text(ident_node, source)
        return ModDeclare(node.start_point, node.end_point, name)

    def transform_declare_stmt(self, node: TSNode, source: bytes):
        typed_ident = node.child_by_field_name('typed_ident')
        initial_node = node.child_by_field_name('initial')

        assert typed_ident
        assert initial_node

        ident = self._transform_typed_ident(typed_ident, source)
        initial_value = self.transform_expr(initial_node, source)

        return DeclareStatement(node.start_point, node.end_point, ident, initial_value)

    def transform_external_stmt(self, node: TSNode, source: bytes):
        real_stmt = node.children[0]
        if real_stmt.type == 'external_variable':
            typed_ident_node = real_stmt.child_by_field_name('typed_ident')
            assert typed_ident_node
            typed_ident = self._transform_typed_ident(typed_ident_node, source)
            return ExternalStatement(
                node.start_point,
                node.end_point,
                ExternalVariableSpec(
                    real_stmt.start_point,
                    real_stmt.end_point,
                    typed_ident))
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

            return ExternalStatement(
                node.start_point,
                node.end_point,
                ExternalFunctionSpec(
                    node.start_point,
                    node.end_point,
                    func_name,
                    params,
                    returns))
        else:
            raise Exception(f'unexpected external statement type {real_stmt.type}')

    def transform_while_stmt(self, node: TSNode, source: bytes):
        condition = node.child_by_field_name('condition')
        body = node.child_by_field_name('body')

        assert condition
        assert body

        cb = self._transform_codeblock(body, source)

        return WhileLoop(node.start_point, node.end_point, self.transform_expr(condition, source), cb)

    def transform_if_stmt(self, node: TSNode, source: bytes):
        condition = node.child_by_field_name('condition')
        consequence_node = node.child_by_field_name('consequence')
        alternative_node = node.child_by_field_name('alternative')

        assert condition
        assert consequence_node

        if alternative_node:
            consequence = self._transform_codeblock(consequence_node, source)
            alternative = self._transform_codeblock(alternative_node, source)

            return If(node.start_point, node.end_point, self.transform_expr(condition, source), consequence, alternative)
        else:
            consequence = self._transform_codeblock(consequence_node, source)

            return If(node.start_point, node.end_point, self.transform_expr(condition, source), consequence, None)

    def transform_return_stmt(self, node: TSNode, source: bytes):
        returns = node.child_by_field_name('returns')

        assert returns

        return ReturnStatement(node.start_point, node.end_point, self.transform_expr(returns, source))

    def transform_type_alias(self, node: TSNode, source: bytes):
        ident_node = node.child_by_field_name('ident')
        typing_node = node.child_by_field_name('typing')

        assert ident_node
        assert typing_node

        ident = self.get_text(ident_node, source)
        if typing_node.type == 'ident_expr':
            typing = self.transform_ident_expr(typing_node, source)
        elif typing_node.type == 'pointer':
            underlying_node = typing_node.child_by_field_name('underlying')
            assert underlying_node
            typing = self.transform_ident_expr(underlying_node, source)
        else:
            raise Exception(f'unexpected typing node type {typing_node.type}')

        return TypeAliasStatement(node.start_point, node.end_point, ident, typing, typing_node.type == 'pointer')

    def transform_expr(self, node: TSNode, source: bytes) -> PaluNode:
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
        elif real_expr.type == 'assignment_expr':
            return self.transform_assignment_expr(real_expr, source)
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

    def transform_ident_expr(self, node: TSNode, source: bytes):
        ident = [*map(lambda n: self.get_text(n, source), node.children)]
        return IdentExpr(node.start_point, node.end_point, *ident)

    def transform_binary_expr(self, node: TSNode, source: bytes):
        operator = node.child_by_field_name('operator')
        left = node.child_by_field_name('left')
        right = node.child_by_field_name('right')

        assert operator
        assert left
        assert right

        return BinaryExpr(
            node.start_point, node.end_point,
            BinaryOp(operator.type),
            self.transform_expr(left, source),
            self.transform_expr(right, source))

    def transform_unary_expr(self, node: TSNode, source: bytes):
        operator = node.child_by_field_name('operator')
        argument = node.child_by_field_name('argument')

        assert operator
        assert argument

        return UnaryExpr(node.start_point, node.end_point, UnaryOp(operator.type), self.transform_expr(argument, source))

    def transform_condition_expr(self, node: TSNode, source: bytes):
        condition = node.child_by_field_name('condition')
        consequence = node.child_by_field_name('consequence')
        alternative = node.child_by_field_name('alternative')

        assert condition
        assert consequence
        assert alternative

        return ConditionExpr(
            node.start_point, node.end_point,
            self.transform_expr(condition, source),
            self.transform_expr(consequence, source),
            self.transform_expr(alternative, source),
        )

    def transform_call_expr(self, node: TSNode, source: bytes):
        func_name_node = node.child_by_field_name('func_name')
        args_node = node.child_by_field_name('args')

        assert func_name_node
        assert args_node

        func_name = self.transform_ident_expr(func_name_node, source)
        args = self._transform_argument_list(args_node, source)

        return CallExpr(node.start_point, node.end_point, func_name, *args)

    def transform_func_stmt(self, node: TSNode, source: bytes):
        func_name_node = node.child_by_field_name('func_name')
        params_node = node.child_by_field_name('params')
        returns_node = node.child_by_field_name('returns')
        body_node = node.child_by_field_name('body')

        assert func_name_node
        assert body_node
        assert params_node
        assert returns_node

        func_name = self.get_text(func_name_node, source)

        # 解析函数签名
        params = self._transform_params(params_node, source)
        returns = self.transform_ident_expr(returns_node, source)

        # 解析函数体内容
        body = self._transform_codeblock(body_node, source)

        return Func(node.start_point, node.end_point, func_name, params, returns, body)

    def transform_parenthesized_expr(self, node: TSNode, source: bytes):
        expr = node.child_by_field_name('expr')

        assert expr

        return ParenthesizedExpr(node.start_point, node.end_point, self.transform_expr(expr, source))

    def transform_assignment_expr(self, node: TSNode, source: bytes):
        left_node = node.child_by_field_name('left')
        op_node = node.child_by_field_name('operator')
        right_node = node.child_by_field_name('right')

        assert left_node
        assert op_node
        assert right_node

        op = AsssignmentOp(self.get_text(op_node, source))
        left = self.transform_ident_expr(left_node, source)
        right = self.transform_expr(right_node, source)

        return AssignmentExpr(node.start_point, node.end_point, left, op, right)

    def transform_number_literal(self, node: TSNode, source: bytes):
        return NumberLiteral(node.start_point, node.end_point, str(source[node.start_byte:node.end_byte], 'utf-8'))

    def transform_string_literal(self, node: TSNode, source: bytes):
        return StringLiteral(node.start_point, node.end_point, str(source[node.start_byte:node.end_byte], 'utf-8'))

    def transform_true_lit(self, node: TSNode, source: bytes) -> BooleanLiteral:
        return BooleanLiteral(node.start_point, node.end_point, str(source[node.start_byte:node.end_byte], 'utf-8'))

    def transform_false_lit(self, node: TSNode, source: bytes) -> BooleanLiteral:
        return BooleanLiteral(node.start_point, node.end_point, str(source[node.start_byte:node.end_byte], 'utf-8'))

    def transform_null_lit(self, node: TSNode) -> NullLiteral:
        return NullLiteral(node.start_point, node.end_point)

    def _transform_typed_ident(self, node: TSNode, source: bytes) -> TypedIdent:
        ident_node = node.child_by_field_name('ident')
        typing_node = node.child_by_field_name('typing')

        assert ident_node
        assert typing_node

        ident = self.get_text(ident_node, source)
        if typing_node.type == 'ident_expr':
            typing = self.transform_ident_expr(typing_node, source)
        elif typing_node.type == 'pointer':
            underlying_node = typing_node.child_by_field_name('underlying')
            assert underlying_node
            typing = self.transform_ident_expr(underlying_node, source)
        else:
            raise Exception(f'unexpected typing node type {typing_node.type}')

        return TypedIdent(ident, typing, typing_node.type == 'pointer')

    def _transform_codeblock(self, node: TSNode, source: bytes) -> Sequence[PaluNode]:
        return [*map(lambda n: self.transform_statement(n, source), filter(lambda n: n.is_named, node.children))]

    def _transform_argument_list(self, node: TSNode, source: bytes) -> Sequence[PaluNode]:
        return [*map(lambda n: self.transform_expr(n, source), filter(lambda n: n.is_named, node.children))]

    def _transform_params(self, node: TSNode, source: bytes) -> Sequence[Union[TypedIdent, str]]:
        result: List[Union[TypedIdent, str]] = []
        for child in node.children:
            if child.type in '(,)':
                continue
            elif child.type == 'typed_ident':
                result.append(self._transform_typed_ident(child, source))
            else:
                result.append(self.get_text(child, source))

        return result

    def get_text(self, node: TSNode, source: bytes) -> str:
        return str(source[node.start_byte:node.end_byte], 'utf-8')
