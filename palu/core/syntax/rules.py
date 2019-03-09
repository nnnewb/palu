from ply.yacc import YaccProduction

from palu.core.ast import BinaryExpr, FuncCallArgs, FuncCall, WhileLoop, CodeBlock
from palu.core.lex.rules import tokens

tokens = tokens
start = 'stmt'


def p_stmt(p: YaccProduction):
    """ stmt : expr ';'
             | while
    """
    p[0] = p[1]


def p_empty(p: YaccProduction):
    'empty :'
    pass


def p_factor(p: YaccProduction):
    """ factor : LParen expr RParen
               | LITERAL_NUMBER
               | LITERAL_STRING
               | LITERAL_STRING_TEMPLATE
    """
    if len(p) == 4:
        return p[2]
    else:
        return p[1]


def p_binary_expr(p: YaccProduction):
    """ binary_expr : term OP_PLUS expr
                    | term OP_MINUS expr
        term : factor OP_TIMES term
             | factor OP_DIVIDE term
             | factor
    """
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = BinaryExpr(p[2], p[1], p[3])


def p_expr(p: YaccProduction):
    """ expr : binary_expr
             | factor
             | func_call
    """
    p[0] = p[1]


def p_func_call(p: YaccProduction):
    """ func_call : IDENTIFIER func_call_args
                  | IDENTIFIER
    """
    if len(p) == 3:
        p[0] = FuncCall(p[1], p[2])
    else:
        p[0] = FuncCall(p[1], tuple())


def p_func_call_args(p: YaccProduction):
    """ func_call_args : factor
                       | factor COMMA func_call_args
                       | IDENTIFIER OP_ARROW factor COMMA func_call_args
    """
    if len(p) == 4:
        p[3].positional_args.append(p[1])
        p[0] = p[3]
    elif isinstance(p[1], FuncCallArgs):
        p[0] = p[1]
    else:
        p[0] = FuncCallArgs(p[1])


def p_while(p: YaccProduction):
    """ while : KW_WHILE expr do_block
    """
    p[0] = WhileLoop(p[2], p[3])


def p_do_block(p: YaccProduction):
    """ do_block : KW_DO cb KW_END
        cb : stmt cb
           | empty
    """
    if len(p) == 2:
        p[0] = CodeBlock()
    elif len(p) == 4:
        if p[1] == 'do':
            p[0] = p[2]
        else:
            p[3].all_expr.append(p[1])
            p[0] = p[3]


if __name__ == '__main__':
    from ply import yacc
    from ply.lex import lex
    from palu.core.lex import rules
    from logging import getLogger, basicConfig, DEBUG

    basicConfig(level=DEBUG, format='%(filename)10s:%(lineno)4d: %(message)s')

    lexLogger = getLogger('lex')
    yaccLogger = getLogger('yacc')

    lexer = lex(rules, debug=True, debuglog=lexLogger)
    parser = yacc.yacc(debug=True, debuglog=yaccLogger)
    result = parser.parse('''say hi;''', lexer=lexer, debug=yaccLogger)
    print(result)
    # while True:
    #     try:
    #         s = input('prompt > ')
    #     except EOFError:
    #         break
    #     if not s:
    #         continue
    #     result = parser.parse(s, lexer=lexer)
    #     print(result)
