from logging import getLogger

from palu.core.annotations.ply.lex import LexToken

logger = getLogger('palu.core.lexer.rules')

tokens = (
    'BRACE_OPEN',
    'BRACE_CLOSE',
    'KW_IF',
    'KW_THEN',
    'KW_ELSE',
    'KW_ELIF',
    'KW_WHILE',
    'KW_DO',
    'KW_IN',
    'KW_END',
    'KW_DEF',
    'KW_RETURN',
    'KW_OR',
    'KW_AND',
    'OP_ARROW',
    'OP_ASSIGN',
    'OP_EQ',
    'OP_NE',
    'OP_GT',
    'OP_GE',
    'OP_LT',
    'OP_LE',
    'LITERAL_NUMBER',
    'LITERAL_STRING',
    'LITERAL_STRING_TEMPLATE',
    'IDENTIFIER',
    'NEWLINE',
    'COMMENT',
)

t_ignore_COMMENT = r'--.*'
t_OP_ARROW = r'=>'
t_OP_ASSIGN = r'='
t_OP_EQ = r'=='
t_OP_NE = r'!='
t_OP_GT = r'>'
t_OP_GE = r'>='
t_OP_LT = r'<'
t_OP_LE = r'<='
t_LITERAL_STRING_TEMPLATE = r'`.*?`'
t_ignore = ' \t\r\f\v'

literals = r';\+\-\*/\(\),\{\}'


def t_NEWLINE(t: LexToken):
    r"""\n+"""
    t.lexer.lineno += len(t.value)


def t_IDENTIFIER(t: LexToken) -> LexToken:
    r"""[a-zA-Z_][a-zA-Z0-9_-]*"""
    t.type = "KW_{}".format(t.value.upper()) if t.value in ('if', 'then', 'else', 'elif',
                                                            'while', 'do', 'for', 'in', 'end',
                                                            'def', 'return', 'and', 'or') else 'IDENTIFIER'
    return t


def t_LITERAL_NUMBER(t: LexToken) -> LexToken:
    r'''(0x\d+|b[01]+|\-?\d+)'''
    if t.value.startswith('b'):
        t.value = int(t.value[1:], 2)
    elif t.value.startswith('0x'):
        t.value = int(t.value[2:], 16)
    elif t.value.startswith('0'):
        t.value = int(t.value, 8)
    else:
        t.value = int(t.value)
    return t


def t_LITERAL_STRING(t: LexToken) -> LexToken:
    r'''(\'.*?\'|".*?")'''
    t.value = t.value[1:-1]
    return t


def t_error(t: LexToken):
    logger.error("Illegal character '{}' found.".format(t.value[0]))
    t.lexer.skip(1)
