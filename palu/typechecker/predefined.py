from palu.typechecker.symbol import PaluSymbol
from palu.typechecker.scope import Scope

global_scope = Scope()
global_scope.add_symbol(
    PaluSymbol('bool', None, [], is_builtin_type=True),
    PaluSymbol('i8', None, [], is_builtin_type=True),
    PaluSymbol('u8', None, [], is_builtin_type=True),
    PaluSymbol('i16', None, [], is_builtin_type=True),
    PaluSymbol('u16', None, [], is_builtin_type=True),
    PaluSymbol('i32', None, [], is_builtin_type=True),
    PaluSymbol('u32', None, [], is_builtin_type=True),
    PaluSymbol('i64', None, [], is_builtin_type=True),
    PaluSymbol('u64', None, [], is_builtin_type=True),
    PaluSymbol('f32', None, [], is_builtin_type=True),
    PaluSymbol('f64', None, [], is_builtin_type=True),
)
