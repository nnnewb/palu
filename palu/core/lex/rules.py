from logging import getLogger

from palu.core.annotations.ply.lex import LexToken

tokens = (
    'BRACE_OPEN',
    'BRACE_CLOSE',
    'KW_IF',
    'KW_THEN',
    'KW_ELSE',
    'KW_ELIF',
    'KW_WHILE',
    'KW_DO',
    'KW_FOR',
    'KW_IN',
    'KW_END',
    'KW_DEF',
    'OP_PLUS',
    'OP_MINUS',
    'OP_TIMES',
    'OP_DIVIDE',
    'OP_ARROW',
    'LITERAL_NUMBER',
    'LITERAL_STRING',
    'LITERAL_STRING_TEMPLATE',
    'IDENTIFIER',
    'COMMA',
    'LParen',
    'RParen',

    # counting
    'NEWLINE',
)

t_BRACE_OPEN = r'{'
t_BRACE_CLOSE = r'}'
t_OP_PLUS = r'\+'
t_OP_MINUS = r'-'
t_OP_TIMES = r'\*'
t_OP_DIVIDE = r'/'
t_OP_ARROW = r'=>'
t_LITERAL_NUMBER = r'(0x\d+|b[01]+|\-?\d+)'
t_LITERAL_STRING = r'(\'.*\'|".*")'
t_LITERAL_STRING_TEMPLATE = r'`.*`'
t_COMMA = r','
t_LParen = r'\('
t_RParen = r'\)'
t_ignore = ' \t\r\f\v'

literals = ';'


def t_NEWLINE(t: LexToken):
    r'\n+'
    t.lexer.lineno += len(t.value)


def t_IDENTIFIER(t: LexToken):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    t.type = "KW_{}".format(t.value.upper()) if t.value in ('if', 'then', 'else', 'elif',
                                                            'while', 'do', 'for', 'in', 'end',
                                                            'def') else 'IDENTIFIER'
    return t


def t_error(t: LexToken):
    print("Illegal character '{}' found.".format(t.value[0]))
    t.lexer.skip(1)


logger = getLogger('palu.core.lexer.rules')
