from io import StringIO
from typing import Callable, Dict, List


from palu.ast.expr import (AssignmentExpr, BinaryExpr, CallExpr, ConditionExpr,
                           IdentExpr, ParenthesizedExpr, TypedIdent, UnaryExpr)
from palu.ast.func import Func
from palu.ast.literals import (BooleanLiteral, NullLiteral, NumberLiteral,
                               StringLiteral)
from palu.ast.node import Node
from palu.ast.source import ModDeclare, SourceFile
from palu.ast.statements import (DeclareStatement, EmptyStatement,
                                 ExternalFunctionSpec, ExternalStatement,
                                 ExternalVariableSpec, If, ReturnStatement,
                                 TypeAliasStatement, WhileLoop)
from palu.typechecker.predefined import global_scope
from palu.typechecker.scope import Scope, ScopedSymbol
from palu.typechecker.symbol import PaluSymbol


class _Emitter:
    def __init__(self) -> None:
        self.dispatch_dict: Dict[type, Callable] = {}

    def emit(self, this, data):
        self.dispatch_dict[data.__class__](this, data)

    def on(self, _type):
        def wrapper(func):
            self.dispatch_dict[_type] = func
            return func
        return wrapper


class Transpiler:
    _emitter = _Emitter()
    _on = _emitter.on

    def __init__(self) -> None:
        self.current_scope = global_scope
        self.scope_stack: List[Scope] = []
        self._buffer = StringIO()

    def enter(self, scope):
        self.scope_stack.append(self.current_scope)
        self.current_scope = scope

    def leave(self):
        self.current_scope = self.scope_stack.pop()

    def _emit(self, node: Node):
        self._emitter.emit(self, node)

    def _write(self, *text: str):
        for t in text:
            self._buffer.write(t)

    @_on(SourceFile)
    def _transpile_source_file(self, node: SourceFile):
        self.enter(Scope())
        for n in node.statements:
            self._emit(n)
        self.leave()

    @_on(ModDeclare)
    def _transpile_mod_declare(self, mod: ModDeclare):
        self.enter(Scope(mod.name, Scope.ScopeKind.Mod))

    @_on(IdentExpr)
    def _transpile_ident_expr(self, ident_expr: IdentExpr):
        # TODO: 应该考虑 name mangling，对于 mod 级别非导出的 palu 函数用 mod 名称做前缀
        self._write('.'.join(ident_expr.ident))

    @_on(NumberLiteral)
    def _transpile_number_literal(self, literal: NumberLiteral):
        self._write(literal.value.__str__())

    @_on(BooleanLiteral)
    def _transpile_boolean_literal(self, literal: BooleanLiteral):
        self._write('TRUE' if literal.value else 'FALSE')

    @_on(NullLiteral)
    def _transpile_null_literal(self, _: NullLiteral):
        self._write('NULL')

    @_on(StringLiteral)
    def _transpile_string_literal(self, literal: StringLiteral):
        self._write(literal.value)

    @_on(DeclareStatement)
    def _transpile_declare_stmt(self, decl: DeclareStatement):
        self._emit(decl.typed_ident)

        if decl.initial_value is not None:
            self._write(' = ')
            self._emit(decl.initial_value)

        self._write(';')

    @_on(ExternalStatement)
    def _transpile_external_stmt(self, external_stmt: ExternalStatement):
        self._write('extern ')
        self._emit(external_stmt.spec)
        self._write(';')

    @_on(ExternalVariableSpec)
    def _transpile_external_var(self, external_var_spec: ExternalVariableSpec):
        self._emit(external_var_spec.typed_ident)

    @_on(ExternalFunctionSpec)
    def _transpile_external_fn(self, external_fn_spec: ExternalFunctionSpec):
        self._emit(external_fn_spec.returns)
        self._write(' ', external_fn_spec.ident, '(')
        for idx, param in enumerate(external_fn_spec.params):
            if isinstance(param, str):
                self._write(param)
            else:
                self._emit(param)

            if idx < len(external_fn_spec.params)-1:
                self._write(',')
        self._write(')')

    @_on(WhileLoop)
    def _transpile_while_loop(self, while_loop: WhileLoop):
        self._write('while(')
        self._emit(while_loop.condition)
        self._write(') {')
        for n in while_loop.body:
            self._emit(n)
        self._write('}')

    @_on(EmptyStatement)
    def _transpile_empty_stmt(self, _: EmptyStatement):
        self._write(';')

    @_on(If)
    def _transpile_if_stmt(self, if_stmt: If):
        self._write('if(')
        self._emit(if_stmt.condition)
        self._write(') {')
        for n in if_stmt.consequence:
            self._emit(n)

        if if_stmt.alternative:
            self._write('} else {')
            for n in if_stmt.alternative:
                self._emit(n)

        self._write('}')

    @_on(ReturnStatement)
    def _transpile_return_stmt(self, ret: ReturnStatement):
        self._write('return ')
        self._emit(ret.expr)
        self._write(';')

    @_on(Func)
    def _transpile_func(self, fn: Func):
        self._emit(fn.returns)
        self._write(f' {self.current_scope.name_mangling(fn.func_name)}(')
        for idx, param in enumerate(fn.params):
            if isinstance(param, str):
                self._write(param)
            else:
                self._emit(param)

            if idx < len(fn.params)-1:
                self._write(',')
        self._write(') {')
        for n in fn.body:
            self._emit(n)
        self._write('}')

    @_on(CallExpr)
    def _transpile_call_expr(self, call_expr: CallExpr):
        self._emit(call_expr.ident)
        self._write('(')
        for idx, arg in enumerate(call_expr.args):
            self._emit(arg)
            if idx < len(call_expr.args)-1:
                self._write(',')
        self._write(')')

    @_on(TypedIdent)
    def _transpile_typed_ident(self, typed_ident: TypedIdent):
        self._emit(typed_ident.typing)
        if typed_ident.is_pointer:
            self._write('*')
        self._write(' ', typed_ident.ident)

    @_on(TypeAliasStatement)
    def _transpile_type_alias_stmt(self, stmt: TypeAliasStatement):
        self._write('typedef ')
        self._emit(stmt.typing)
        if stmt.is_pointer:
            self._write('*')

        self._write(f' {stmt.ident};')

    @_on(ParenthesizedExpr)
    def _transpile_parenthesized_expr(self, expr: ParenthesizedExpr):
        self._write('(')
        self._emit(expr.expr)
        self._write(')')

    @_on(BinaryExpr)
    def _transpile_binary_expr(self, bin_expr: BinaryExpr):
        self._write('(')
        self._emit(bin_expr.left)
        self._write(') ', bin_expr.op.value, ' (')
        self._emit(bin_expr.right)
        self._write(')')

    @_on(UnaryExpr)
    def _transpile_unary_expr(self, unary: UnaryExpr):
        self._write(unary.op.value)
        self._emit(unary.expr)

    @_on(ConditionExpr)
    def _transpile_condition_expr(self, expr: ConditionExpr):
        self._write('(')
        self._emit(expr.condition)
        self._write(') ? (')
        self._emit(expr.consequence)
        self._write(') : (')
        self._emit(expr.alternative)
        self._write(')')

    @_on(AssignmentExpr)
    def _transpile_assignment_expr(self, expr: AssignmentExpr):
        self._emit(expr.left)
        self._write(expr.op.value)
        self._emit(expr.right)
        self._write(';')

    def transpile(self, node: Node):
        self._buffer.truncate(0)
        self._emit(node)
        return self._buffer.getvalue()
