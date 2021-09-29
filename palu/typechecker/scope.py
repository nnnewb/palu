from palu.typechecker.symbol import PaluSymbol
from typing import Dict, List, Optional


class SymbolRedefinedException(Exception):
    def __init__(self, sym: PaluSymbol, previous: PaluSymbol) -> None:
        super().__init__(f'{sym.name} was redefined in this scope')
        self.sym = sym
        self.previous = previous


class ScopedSymbol:
    def __init__(self, scope: 'Scope', sym: PaluSymbol) -> None:
        self.scope = scope
        self.symbol = sym


class Scope(object):
    def __init__(self) -> None:
        super().__init__()
        self.symbols: Dict[str, PaluSymbol] = {}
        self.parent: Optional[Scope] = None
        self.children: List[Scope] = []

    def lookup(self, name: str) -> Optional[ScopedSymbol]:
        if name in self.symbols:
            return ScopedSymbol(self, self.symbols[name])
        elif self.parent is not None:
            return self.parent.lookup(name)
        else:
            return None

    def add_symbol(self, sym: PaluSymbol):
        if sym in self.symbols:
            raise SymbolRedefinedException(sym, self.symbols[sym.name])

        self.symbols[sym.name] = sym

    def add_child_scope(self, scope: 'Scope'):
        self.children.append(scope)
