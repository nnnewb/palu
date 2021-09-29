from typing import Callable, Dict, List
from typing_extensions import TypeAlias
from palu.typechecker.predefined import global_scope
from io import StringIO
from palu.typechecker.scope import Scope, ScopedSymbol
from palu.typechecker.symbol import PaluSymbol
from palu.ast.expr import (AssignmentExpr, BinaryExpr, CallExpr, ConditionExpr,
                           IdentExpr, ParenthesizedExpr, TypedIdent, UnaryExpr)
from palu.ast.func import Func
from palu.ast.literals import (BooleanLiteral, NullLiteral, NumberLiteral,
                               StringLiteral)
from palu.ast.node import Node
from palu.ast.op import AsssignmentOp, BinaryOp, UnaryOp
from palu.ast.source import ModDeclare, SourceFile
from palu.ast.statements import (DeclareStatement, EmptyStatement,
                                 ExternalFunctionSpec, ExternalStatement,
                                 ExternalVariableSpec, If, ReturnStatement,
                                 TypeAliasStatement, WhileLoop)


class _Dispatcher:
    def __init__(self) -> None:
        self.dispatch_dict: Dict[type, Callable] = {}

    def dispatch(self, this, data):
        self.dispatch_dict[data.__class__](this, data)

    def subscribe(self, _type):
        def wrapper(func):
            self.dispatch_dict[_type] = func
            return func
        return wrapper


class Transpiler:
    _dispatcher = _Dispatcher()

    def __init__(self) -> None:
        self.current_scope = global_scope
        self.scope_stack: List[Scope] = []
        self._buffer = StringIO()

    def enter(self, scope):
        self.scope_stack.append(self.current_scope)
        self.current_scope = scope

    def leave(self):
        self.current_scope = self.scope_stack.pop()

    @_dispatcher.subscribe(SourceFile)
    def _transpile_source_file(self, node: SourceFile):
        self.enter(Scope())
        for n in node.statements:
            self._dispatcher.dispatch(self, n)
        self.leave()

    @_dispatcher.subscribe(IdentExpr)
    def _transpile_ident_expr(self, ident_expr: IdentExpr):
        # TODO: 应该考虑 name mangling，对于 mod 级别非导出的 palu 函数用 mod 名称做前缀
        self._buffer.write('.'.join(ident_expr.ident))

    @_dispatcher.subscribe(NumberLiteral)
    def _transpile_number_literal(self, literal: NumberLiteral):
        self._buffer.write(literal.value.__str__())

    @_dispatcher.subscribe(BooleanLiteral)
    def _transpile_boolean_literal(self, literal: BooleanLiteral):
        self._buffer.write('TRUE' if literal.value else 'FALSE')

    @_dispatcher.subscribe(DeclareStatement)
    def _transpile_declare_stmt(self, decl: DeclareStatement):
        self._dispatcher.dispatch(self, decl.typed_ident)

        if decl.initial_value is not None:
            self._buffer.write(' = ')
            self._dispatcher.dispatch(self, decl.initial_value)

        self._buffer.write(';')

    @_dispatcher.subscribe(ExternalStatement)
    def _transpile_external_stmt(self, external_stmt: ExternalStatement):
        self._buffer.write('extern ')
        self._dispatcher.dispatch(self, external_stmt.spec)
        self._buffer.write(';')

    @_dispatcher.subscribe(ExternalVariableSpec)
    def _transpile_external_var(self, external_var_spec: ExternalVariableSpec):
        self._dispatcher.dispatch(self, external_var_spec.typed_ident)

    @_dispatcher.subscribe(ExternalFunctionSpec)
    def _transpile_external_fn(self, external_fn_spec: ExternalFunctionSpec):
        self._dispatcher.dispatch(self, external_fn_spec.returns)
        self._buffer.write(' '+external_fn_spec.ident+'(')
        for idx, param in enumerate(external_fn_spec.params):
            if isinstance(param, str):
                self._buffer.write(param)
            else:
                self._dispatcher.dispatch(self, param)

            if idx < len(external_fn_spec.params)-1:
                self._buffer.write(',')
        self._buffer.write(')')

    @_dispatcher.subscribe(WhileLoop)
    def _transpile_while_loop(self, while_loop: WhileLoop):
        self._buffer.write('while(')
        self._dispatcher.dispatch(self, while_loop.condition)
        self._buffer.write(') {')
        for n in while_loop.body:
            self._dispatcher.dispatch(self, n)
        self._buffer.write('}')

    @_dispatcher.subscribe(If)
    def _transpile_if_stmt(self, if_stmt: If):
        self._buffer.write('if(')
        self._dispatcher.dispatch(self, if_stmt.condition)
        self._buffer.write(') {')
        for n in if_stmt.consequence:
            self._dispatcher.dispatch(self, n)

        if if_stmt.alternative:
            self._buffer.write('} else {')
            for n in if_stmt.alternative:
                self._dispatcher.dispatch(self, n)

        self._buffer.write('}')

    @_dispatcher.subscribe(ReturnStatement)
    def _transpile_return_stmt(self, ret: ReturnStatement):
        self._buffer.write('return ')
        self._dispatcher.dispatch(self, ret.expr)
        self._buffer.write(';')

    @_dispatcher.subscribe(Func)
    def _transpile_func(self, fn: Func):
        self._dispatcher.dispatch(self, fn.returns)
        self._buffer.write(' '+fn.func_name+'(')
        for idx, param in enumerate(fn.params):
            if isinstance(param, str):
                self._buffer.write(param)
            else:
                self._dispatcher.dispatch(self, param)

            if idx < len(fn.params)-1:
                self._buffer.write(',')
        self._buffer.write(') {')
        for n in fn.body:
            self._dispatcher.dispatch(self, n)
        self._buffer.write('}')

    @_dispatcher.subscribe(CallExpr)
    def _transpile_call_expr(self, call_expr: CallExpr):
        self._dispatcher.dispatch(self, call_expr.ident)
        self._buffer.write('(')
        for idx, arg in enumerate(call_expr.args):
            self._dispatcher.dispatch(self, arg)
            if idx < len(call_expr.args)-1:
                self._buffer.write(',')
        self._buffer.write(')')

    @_dispatcher.subscribe(TypedIdent)
    def _transpile_typed_ident(self, typed_ident: TypedIdent):
        self._dispatcher.dispatch(self, typed_ident.typing)
        if typed_ident.is_pointer:
            self._buffer.write('*')
        self._buffer.write(' ' + typed_ident.ident)

    @_dispatcher.subscribe(TypeAliasStatement)
    def _transpile_type_alias_stmt(self, stmt: TypeAliasStatement):
        self._buffer.write('typedef ')
        self._dispatcher.dispatch(self, stmt.typing)
        if stmt.is_pointer:
            self._buffer.write('*')

        self._buffer.write(f' {stmt.ident};')

    @_dispatcher.subscribe(ParenthesizedExpr)
    def _transpile_parenthesized_expr(self, expr: ParenthesizedExpr):
        self._buffer.write('(')
        self._dispatcher.dispatch(self, expr.expr)
        self._buffer.write(')')

    @_dispatcher.subscribe(BinaryExpr)
    def _transpile_binary_expr(self, bin_expr: BinaryExpr):
        self._buffer.write('(')
        self._dispatcher.dispatch(self, bin_expr.left)
        self._buffer.write(') '+bin_expr.op.value+' (')
        self._dispatcher.dispatch(self, bin_expr.right)
        self._buffer.write(')')

    @_dispatcher.subscribe(UnaryExpr)
    def _transpile_unary_expr(self, unary: UnaryExpr):
        self._buffer.write(unary.op.value)
        self._dispatcher.dispatch(self, unary.expr)

    @_dispatcher.subscribe(ConditionExpr)
    def _transpile_condition_expr(self, expr: ConditionExpr):
        self._buffer.write('(')
        self._dispatcher.dispatch(self, expr.condition)
        self._buffer.write(') ? (')
        self._dispatcher.dispatch(self, expr.consequence)
        self._buffer.write(') : (')
        self._dispatcher.dispatch(self, expr.alternative)
        self._buffer.write(')')

    @_dispatcher.subscribe(AssignmentExpr)
    def _transpile_assignment_expr(self, expr: AssignmentExpr):
        self._dispatcher.dispatch(self, expr.left)
        self._buffer.write(expr.op.value)
        self._dispatcher.dispatch(self, expr.right)
        self._buffer.write(';')

    def transpile(self, node: Node):
        self._buffer.truncate(0)
        self._dispatcher.dispatch(self, node)
        return self._buffer.getvalue()
