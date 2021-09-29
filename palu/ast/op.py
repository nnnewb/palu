from enum import Enum


class BinaryOp(Enum):
    ADD = '+'
    SUB = '-'
    MUL = '*'
    DIV = '/'
    PERC = '%'
    OR = '||'
    AND = '&&'
    BIT_OR = '|'
    BIT_AND = '&'
    BIT_XOR = '^'
    EQ = '=='
    NE = '!='
    GT = '>'
    LT = '<'
    GTE = '>='
    LTE = '<='
    LSHIFT = '<<'
    RSHIFT = '>>'


class UnaryOp(Enum):
    ADD = '+'
    SUB = '-'
    NOT = '!'


class AsssignmentOp(Enum):
    Direct = '='
    MulAssign = '*='
    DivAssign = '/='
    AddAssign = '+='
    SubAssign = '-='
    LSAssign = '<<='
    RSAssign = '>>='
    BAAssign = '&='
    BOAssign = '|='
    BXAssign = '^='
