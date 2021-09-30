from palu.typechecker.symbol import PaluSymbol
from typing import Dict, List, Optional
from enum import Enum


class SymbolRedefinedException(Exception):
    def __init__(self, sym: PaluSymbol, previous: PaluSymbol) -> None:
        super().__init__(f'{sym.name} was redefined in this scope')
        self.sym = sym
        self.previous = previous


class ScopedSymbol:
    def __init__(self, scope: 'Scope', sym: PaluSymbol) -> None:
        self.scope = scope
        self.symbol = sym

    @property
    def mangling_name(self):
        return self.scope.name_mangling(self.symbol.name)


class Scope(object):
    class ScopeKind(Enum):
        Mod = 'mod'
        CodeBlock = 'codeblock'

    def __init__(self, name: Optional[str] = None, kind: 'ScopeKind' = ScopeKind.CodeBlock, *,
                 name_mangling: Optional[bool] = None) -> None:
        super().__init__()
        self.name = name
        self.kind = kind
        self._name_mangling = False
        if kind == Scope.ScopeKind.Mod:
            self._name_mangling = True

        if name_mangling is not None:
            self._name_mangling = name_mangling

        self.symbols: Dict[str, PaluSymbol] = {}
        self.parent: Optional[Scope] = None
        self.children: List[Scope] = []

    def name_mangling(self, name: str):
        if self._name_mangling:
            if self.name is None:
                raise Exception('name mangling scope must have a name')
            return self.name+'_'+name
        return name

    def lookup(self, name: str) -> Optional[ScopedSymbol]:
        if name in self.symbols:
            return ScopedSymbol(self, self.symbols[name])
        elif self.parent is not None:
            return self.parent.lookup(name)
        else:
            return None

    def add_symbol(self, *symbols: PaluSymbol):
        for sym in symbols:
            if sym in self.symbols:
                raise SymbolRedefinedException(sym, self.symbols[sym.name])

            self.symbols[sym.name] = sym

    def add_child_scope(self, scope: 'Scope'):
        self.children.append(scope)
