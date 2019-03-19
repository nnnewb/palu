from logging import getLogger

from ply.yacc import YaccProduction

from palu.core.annotations.ply.lex import LexToken
from palu.core.lex.rules import tokens
from palu.core.ast import ASTNode, ASTType

tokens = tokens
start = 'stmt'

logger = getLogger('palu.core.syntax.rules')


def p_empty(p: YaccProduction):
    """ empty : """
    pass


def p_stmt(p: YaccProduction):
    """ stmt : expr ';'
            | if
            | while
    """
    p[0] = p[1]


def p_expr(p: YaccProduction):
    """ expr : term '+' expr
            | term '-' expr
            | term
        term : factor '*' term
            | factor '/' term
            | factor
    """
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = ASTNode(ASTType(p[2]), p[1], p[3])


def p_factor(p: YaccProduction):
    """ factor : '(' expr ')'
            | LITERAL_NUMBER
            | fncall
    """
    if len(p) == 4:
        p[0] = p[2]
    else:
        p[0] = p[1]


def p_fn_call(p: YaccProduction):
    """ fncall : IDENTIFIER '(' args ')'
                | IDENTIFIER
    """
    if len(p) == 2:
        p[0] = ASTNode(ASTType.IDENTIFIER, p[1])
    else:
        p[0] = ASTNode(ASTType.FNCALL, p[1], *p[3])


def p_args(p: YaccProduction):
    """
    arg : LITERAL_NUMBER
        | LITERAL_STRING
        | LITERAL_STRING_TEMPLATE
        | fncall
        | empty
    args : arg
        | arg ',' args
    """
    if len(p) == 4:
        # arg , args
        p[0] = [p[1], *p[3]]
    elif len(p) == 2:
        if p[1] is None:
            # | empty
            p[0] = []
        else:
            # | single argj
            p[0] = p[1]


def p_if(p: YaccProduction):
    """ if : KW_IF expr then_block
    """
    p[0] = ASTNode(ASTType.IF, p[2], p[3])


def p_then_block(p: YaccProduction):
    """ then_block : KW_THEN then_stmt_
        then_stmt_ : stmt then_stmt_
                | KW_END
    """
    if len(p) == 3 and p[1] != 'then':
        p[0] = ASTNode(*[p[1], *p[2]])
    elif len(p) == 3 and p[1] == 'then':
        p[0] = p[2]
    elif len(p) == 2:
        p[0] = []


def p_while(p: YaccProduction):
    """ while : KW_WHILE expr do_block
    """
    p[0] = ASTNode(ASTType.WHILE, p[2], p[3])


def p_do_block(p: YaccProduction):
    """ do_block : KW_DO do_stmt_
        do_stmt_ : stmt do_stmt_
                | KW_END
    """
    if len(p) == 3 and p[1] != 'do':
        p[0] = ASTNode(*[p[1], *p[2]])
    elif len(p) == 3 and p[1] == 'do':
        p[0] = p[2]
    elif len(p) == 2:
        p[0] = []


def p_error(p: LexToken):
    if p:
        lexer = p.lexer
        last_cr = lexer.lexdata.rfind('\n', 0, lexer.lexpos)
        if last_cr < 0:
            last_cr = 0
        col = (p.lexpos - last_cr) + 1
        print(f'Syntax error at line {lexer.lineno} col {col}, token {p.value}')
    else:
        print('Syntax error: unexpected EOF.')
