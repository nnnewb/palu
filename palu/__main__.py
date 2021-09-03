from palu.core.parser import PaluSyntaxError, Parser
from prompt_toolkit import prompt


parser = Parser()

# REPL
while True:
    inp = prompt('REPL => ')
    try:
        result = parser.parse(inp.encode('utf-8'))
        print('?> {}'.format(result.root_node.sexp()))

        statements = parser.parse_ast(inp.encode('utf-8'))
        for stmt in statements:
            print('s> {}'.format(stmt.s_expr))
    except PaluSyntaxError as e:
        print(f'syntax error at {e.line}:{e.column}')
        print(e.tree.root_node.sexp())
    except NotImplementedError:
        pass
