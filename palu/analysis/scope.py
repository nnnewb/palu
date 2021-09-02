from enum import Enum


class ScopeType(Enum):
    PACKAGE = 'package'
    MODULE = 'module'
    BLOCK = 'block'


class Scope(object):
    def __init__(self, name: str, scope_type: ScopeType) -> None:
        super().__init__()
        self.name = name
        self.scope_type = scope_type
        self.symbols = []
