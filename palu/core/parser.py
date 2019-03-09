from ply.lex import lex
from ply.yacc import yacc

tokens = (
    'identifier',
)

t_ignore=' \t\n\r\f\v'
t_identifier = '[a-zA-Z]+'
literals = ';'


def p_stmt(p):
    """ stmt : identifier identifier ';' """
    p[0] = (p[1], p[2])


lexer = lex()
parser = yacc()
result = parser.parse('name name;', lexer=lexer)
print(result)
