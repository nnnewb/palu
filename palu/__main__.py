from palu.core.parser import PaluSyntaxError, Parser
from prompt_toolkit import prompt


parser = Parser()

# REPL
while True:
    inp = prompt('REPL => ')
    try:
        result = parser.parse('repl', inp)
        print('?> {}'.format(result.root_node.sexp()))

        parser.parse_ast('repl', inp)
    except PaluSyntaxError as e:
        print(f'syntax error at {e.line}:{e.column}')
    except NotImplementedError as e:
        pass
