from typing import Dict, Optional
from enum import Enum


class SymbolKind(Enum):
    Var = 'var'
    Type = 'type'
    Func = 'func'
    Module = 'module'


class Typing(object):
    def __init__(self, is_readonly=True, is_pointer=False, underlying: 'Symbol' = None) -> None:
        super().__init__()
        self.is_readonly = is_readonly
        self.is_pointer = is_pointer
        self.underlying = underlying

    def assignable(self, operand: 'Typing') -> bool:
        if self.is_readonly:
            return False
        elif self.is_pointer != operand.is_pointer:
            return False
        elif self.underlying != operand.underlying:
            return False
        return True


class Symbol(object):
    def __init__(self, name: str, kind: SymbolKind, typing: Typing = None, parent: 'Symbol' = None) -> None:
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
