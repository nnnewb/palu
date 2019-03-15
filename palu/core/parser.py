from ply.lex import lex
from ply.yacc import yacc

from palu.core.lex import rules as lex_rules_mod
from palu.core.syntax import rules as grammar_rules_mod

lexer = lex(lex_rules_mod, debug=True, debuglog=lex_rules_mod.logger)
parser = yacc(module=grammar_rules_mod, debug=True, debuglog=grammar_rules_mod.logger)
