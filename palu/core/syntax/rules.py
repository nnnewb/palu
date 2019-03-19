from logging import getLogger

from ply.yacc import YaccProduction

from palu.core.annotations.ply.lex import LexToken
from palu.core.lex.rules import tokens
from palu.core.ast import SimpleStmt, BinExpr, FnCall, Branches, Stmt, WhileLoop, Variable

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
    if len(p) == 3:
        p[0] = SimpleStmt(p[1])
    else:
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
        p[0] = BinExpr(p[2], p[1], p[3])


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
        p[0] = Variable(p[1])
    else:
        p[0] = FnCall(p[1], p[3])


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
    p[0] = [*p[2], p[1]] if len(p) == 3 else ([] if p[1] is None else [p[1]])


def p_if(p: YaccProduction):
    """ if : KW_IF expr then_block
    """
    p[0] = Branches(p[2], p[3])


def p_then_block(p: YaccProduction):
    """ then_block : KW_THEN then_stmt_
        then_stmt_ : stmt then_stmt_
                | KW_END
    """
    if len(p) == 3 and isinstance(p[1], Stmt):
        p[0] = [p[1], *p[2]]
    elif len(p) == 3 and p[1] == 'then':
        p[0] = p[2]
    elif len(p) == 2:
        p[0] = []


def p_while(p: YaccProduction):
    """ while : KW_WHILE expr do_block
    """
    p[0] = WhileLoop(p[2], p[3])


def p_do_block(p: YaccProduction):
    """ do_block : KW_DO do_stmt_
        do_stmt_ : stmt do_stmt_
                | KW_END
    """
    if len(p) == 3 and isinstance(p[1], Stmt):
        p[0] = [p[1], *p[2]]
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
