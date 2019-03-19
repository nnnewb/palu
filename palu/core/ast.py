from collections.abc import Sequence
from enum import Enum


class ASTType(Enum):
    WHILE = 'while'
    IF = 'if'
    THEN = 'then'
    DO = 'do'
    END = 'end'
    ADD = '+'
    MINUS = '-'
    MUL = '*'
    DIVIDE = '/'
    IDENTIFIER = 'id'
    FNCALL = 'fncall'
    FNDEF = 'fndef'
    BLOCK = 'block'
    PARAMETERS = 'parameters'


class ASTNode(Sequence):
    def __init__(self, *args):
        self._items = [*args]

    def __getitem__(self, idx):
        return self._items[idx]

    def __len__(self):
        return len(self._items)

    def __repr__(self):
        return f'({self[0]} {" ".join([repr(child) for child in self[1:]])})'
