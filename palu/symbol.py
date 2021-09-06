from typing import Dict, Optional, Sequence
from enum import Enum


class SymbolKind(Enum):
    Var = 'var'
    Type = 'type'
    Func = 'func'
    Module = 'module'
    # pesudo symbol for scope book keeping, not actual symbol
    Global = 'global'
    CodeBlock = 'codeblock'
    Params = 'params'


class Typing(object):
    def __init__(self, ref: Optional['Symbol'] = None, params: Optional[Sequence['Typing']] = None, returns: Optional['Typing'] = None) -> None:
        super().__init__()
        self.ref = ref
        self.params = params
        self.returns = returns

    @staticmethod
    def from_type_ident(env: 'Symbol', name: str) -> 'Typing':
        sym = env.resolve_full_name(name)
        if not sym:
            raise Exception(f'unresolved symbol `{name}`')
        return Typing(sym)

    @staticmethod
    def from_func_signature(env: 'Symbol', params: Sequence[str], returns: str) -> 'Typing':
        resolved_params = []
        for p in params:
            resolved_p = env.resolve_full_name(p)
            if not resolved_p:
                raise Exception(f'unresolved symbol `{p}`')

            resolved_params.append(Typing(resolved_p))

        resolved_returns = env.resolve_full_name(returns)
        if not resolved_returns:
            raise Exception(f'unresolved symbol `{returns}`')
        return Typing(None, resolved_params, Typing(resolved_returns))


class Symbol(object):
    def __init__(self, name: str, kind: SymbolKind, typing: 'Typing' = None, parent: 'Symbol' = None, c_type: Optional[str] = None) -> None:
        """ symbol

        Args:
            name (str): symbol name
            kind (SymbolKind): symbol kind
            typing (Typing, optional): symbol type. None if symbol present a type name. Defaults to None.
            parent (Symbol, optional): symbol parent. None if symbol present a root namespace. Defaults to None.
            c_type (str, optional): c_type of this symbol. symbol.name as c_type by default. Defaults to None.
        """
        super().__init__()
        self.name = name
        self.kind = kind
        self.parent = parent
        self.typing = typing
        self.children: Dict[str, 'Symbol'] = {}
        self._c_type = c_type

    @property
    def root(self) -> 'Symbol':
        if self.parent:
            return self.parent.root
        return self

    @property
    def full_name(self) -> str:
        """full identifier str of this symbol

        Returns:
            str: full identifier
        """
        if self.parent and self.parent.full_name:
            return self.parent.full_name + '.' + self.name
        else:
            return self.name

    def add_child(self, child: 'Symbol'):
        """add or update child in this scope.

        Args:
            child (Symbol): new child
        """
        if child.name in self.children:
            raise Exception(f'{child.name} has already declared in this scope')
        self.children[child.name] = child

    def resolve_name(self, name: str) -> 'Symbol':
        """resolve symbol in this scope.

        Returns:
            Optional[Symbol]: resolved symbol
        """
        for predefined_sym in predefined:
            if predefined_sym.name == name:
                return predefined_sym

        sym_in_current_scope = self.children.get(name)
        if sym_in_current_scope:
            return sym_in_current_scope

        if self.parent:
            sym_in_parent_scope = self.parent.resolve_name(name)
            if sym_in_parent_scope:
                return sym_in_parent_scope

        raise Exception(f'unresolved symbol {name}')

    def resolve_full_name(self, name: str) -> 'Symbol':
        """resolve full name of symbol in this scope.

        Returns:
            Optional[Symbol]: resolved symbol
        """
        parts = name.split('.')
        if len(parts) == 1:
            return self.resolve_name(parts[0])

        if self.root != self:
            return self.root.resolve_full_name(name)

        sym: Optional['Symbol'] = self
        for p in parts:
            if sym:
                sym = self.resolve_name(p)

        if sym is None:
            raise Exception(f'unresolved symbol {name}')

        return sym

    @property
    def c_type(self) -> str:
        if self.kind == SymbolKind.Type:
            return self.name if self._c_type is None else self._c_type

        raise Exception('only symbol of type has c_type')


predefined = [
    Symbol('void', SymbolKind.Type, c_type='void'),
    # 应该用 stdint.h 定义的类型，避免标准对 char/short/int 这些类型长度定义不准确的问题
    Symbol('i8', SymbolKind.Type, c_type='signed char'),
    Symbol('u8', SymbolKind.Type, c_type='unsigned char'),
    Symbol('i16', SymbolKind.Type, c_type='short'),
    Symbol('u16', SymbolKind.Type, c_type='unsigned short'),
    Symbol('i32', SymbolKind.Type, c_type='int'),
    Symbol('u32', SymbolKind.Type, c_type='unsigned int'),
    Symbol('i64', SymbolKind.Type, c_type='long int'),
    Symbol('u64', SymbolKind.Type, c_type='unsigned long int'),
    Symbol('string', SymbolKind.Type, c_type='const char*'),
]
