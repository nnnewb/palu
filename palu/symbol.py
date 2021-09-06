from typing import Dict, Optional, Sequence, TypedDict
from enum import Enum


class SymbolKind(Enum):
    Var = 'var'
    Type = 'type'
    Func = 'func'
    Module = 'module'
    # pesudo symbol for scope book keeping, not actual symbol
    Global = 'global' 
    CodeBlock = 'codeblock'


class Typing(object):
    def __init__(self, ref: Optional['Symbol'] = None, params: Optional[Sequence['Typing']] = None, returns: Optional['Typing'] = None) -> None:
        super().__init__()
        self.ref = ref
        self.params = params
        self.returns = returns

    @staticmethod
    def from_type_ident(env: 'Symbol', name: str) -> Optional['Typing']:
        sym = env.resolve_full_name(name)
        if sym:
            return Typing(sym)
        return None

    @staticmethod
    def from_func_signature(env: 'Symbol', params: Sequence[str], returns: str) -> Optional['Typing']:
        resolved_params = []
        for p in params:
            resolved_p = env.resolve_full_name(p)
            if not resolved_p:
                raise Exception(f'unresolved symbol {p}')

            resolved_params.append(Typing(resolved_p))

        resolved_returns = env.resolve_full_name(returns)
        if not resolved_returns:
            raise Exception(f'unresolved symbol {returns}')
        return Typing(None, resolved_params, Typing(resolved_returns))


class Symbol(object):
    def __init__(self, name: str, kind: SymbolKind, typing: 'Typing' = None, parent: 'Symbol' = None) -> None:
        """ symbol

        Args:
            name (str): symbol name
            kind (SymbolKind): symbol kind
            typing (Typing, optional): symbol type. None if symbol present a type name. Defaults to None.
            parent (Symbol, optional): symbol parent. None if symbol present a root namespace. Defaults to None.
        """
        super().__init__()
        self.name = name
        self.kind = kind
        self.parent = parent
        self.typing = typing
        self.children: Dict[str, 'Symbol'] = {}

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
        if self.parent:
            return self.parent.full_name + '.' + self.name
        else:
            return self.name

    def set_child(self, child: 'Symbol'):
        """add or update child in this scope.

        Args:
            child (Symbol): new child
        """
        self.children[child.name] = child

    def resolve_name(self, name: str) -> Optional['Symbol']:
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

        return None

    def resolve_full_name(self, name: str) -> Optional['Symbol']:
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

        return sym

    @staticmethod
    def resolve_predefined(name: str) -> Optional['Symbol']:
        for predefined_sym in predefined:
            if predefined_sym.name == name:
                return predefined_sym
        return None


predefined = [
    Symbol('i8', SymbolKind.Type),
    Symbol('u8', SymbolKind.Type),
    Symbol('i16', SymbolKind.Type),
    Symbol('u16', SymbolKind.Type),
    Symbol('i32', SymbolKind.Type),
    Symbol('u32', SymbolKind.Type),
    Symbol('i64', SymbolKind.Type),
    Symbol('u64', SymbolKind.Type),
    Symbol('string', SymbolKind.Type),
]
