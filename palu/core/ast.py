from collections.abc import Sequence
from enum import Enum


class ASTType(Enum):
    WHILE = 'while'
    IF = 'if'
    THEN = 'then'
    ELSE = 'else'
    DO = 'do'
    END = 'end'
    ADD = '+'
    MINUS = '-'
    MUL = '*'
    DIVIDE = '/'
    ASSIGN = '='
    EQUALS = '=='
    LESS_THAN = '<'
    LESS_OR_EQUALS = '<='
    GREATER_THAN = '>'
    GREATER_THAN_OR_EQUALS = '>='
    OR = 'or'
    AND = 'and'
    RETURN = 'return'
    IDENTIFIER = 'identifier'
    FNDEF = 'define'
    EXECSEQ = 'begin'
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
        if len(self):
            return f'({self[0].value if isinstance(self[0], ASTType) else self[0]} {" ".join([repr(child) for child in self[1:]])})'
        else:
            return '( )'


class Identifier:
    def __init__(self, identifier):
        self.identifier = identifier

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return self.identifier
