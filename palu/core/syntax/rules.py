from logging import getLogger

from ply.yacc import YaccProduction

from palu.core.annotations.ply.lex import LexToken
from palu.core.lex.rules import tokens
from palu.core.ast import ASTNode, ASTType, Identifier

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
            | def
            | return
    """
    p[0] = p[1]


def p_expr(p: YaccProduction):
    """ expr : expr_ KW_OR expr
            | expr_ KW_AND expr
            | expr_
        expr_ : expr__ OP_ASSIGN expr_
            | expr__ OP_EQ expr_
            | expr__ OP_NE expr_
            | expr__ OP_GT expr_
            | expr__ OP_GE expr_
            | expr__ OP_LT expr_
            | expr__ OP_LE expr_
            | expr__
        expr__ : term '+' expr__
            | term '-' expr__
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
            | LITERAL_STRING
            | LITERAL_STRING_TEMPLATE
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
        # | IDENTIFIER
        p[0] = Identifier(p[1])
    else:
        # | IDENTIFIER '(' args ')'
        p[0] = ASTNode(Identifier(p[1]), *p[3])


def p_args(p: YaccProduction):
    """
    arg : expr
        | empty
    args : arg
        | arg ',' args
    """
    if len(p) == 4:
        # | arg , args
        p[0] = [*p[1], *p[3]]
    elif len(p) == 2:
        if p[1] is None:
            # | empty
            p[0] = []
        elif isinstance(p[1], list):
            # | arg
            p[0] = p[1]
        else:
            # | literals/fncall
            p[0] = [p[1]]


def p_block(p: YaccProduction):
    """ block : stmt block
                | empty
    """
    if len(p) == 2:
        p[0] = ASTNode(ASTType.BLOCK)
    else:
        p[0] = ASTNode(ASTType.BLOCK, p[1], *p[2][1:])


def p_if(p: YaccProduction):
    """ if : KW_IF expr then_
            | KW_IF expr else_
        then_ : KW_THEN block KW_END
        else_ : KW_THEN block KW_ELSE block KW_END
    """
    if len(p) == 4:
        if p[1] == 'if':
            # | KW_IF expr then_/else_
            p[0] = ASTNode(ASTType.IF, p[2], *p[3])
        elif p[1] == 'then':
            # | KW_THEN block KW_END
            p[0] = [*p[2][1:]]
    elif len(p) == 6:
        # | KW_THEN block KW_ELSE block KW_END
        p[0] = ASTNode(ASTNode(ASTType.THEN, *p[2][1:]), ASTNode(ASTType.ELSE, *p[4][1:]))


def p_while(p: YaccProduction):
    """ while : KW_WHILE expr KW_DO block KW_END
    """
    p[0] = ASTNode(ASTType.WHILE, p[2], *p[4][1:])


def p_def(p: YaccProduction):
    """ def : KW_DEF IDENTIFIER '(' params ')' block KW_END
    """
    p[0] = ASTNode(ASTType.FNDEF, Identifier(p[2]), ASTNode(*p[4]), *p[6][1:])


def p_params(p: YaccProduction):
    """ params : IDENTIFIER ',' params
                | IDENTIFIER empty
                | empty
    """
    if len(p) == 2:
        p[0] = []
    elif len(p) == 3:
        p[0] = ASTNode(ASTType.PARAMETERS, p[1])
    else:
        p[0] = ASTNode(ASTType.PARAMETERS, p[1], *p[3][1:])


def p_return(p: YaccProduction):
    """ return : KW_RETURN expr ';'
    """
    p[0] = ASTNode(ASTType(p[1]), p[2])


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
