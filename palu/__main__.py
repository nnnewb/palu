import io

import click
from prompt_toolkit import prompt

from palu.core.parser import PaluSyntaxError, Parser
from palu.transpile.transpiler import Transpiler


@click.command()
@click.option('--repl/--no-repl', default=False)
@click.option('-o', '--out', type=click.File('wb+', lazy=True), default='source.c')
@click.argument('source', type=click.File('rb'), required=False)
def run(repl: bool, out: io.FileIO, source: io.FileIO):
    parser = Parser()
    transpiler = Transpiler()

    if repl:
        while True:
            inp = prompt('REPL => ')
            try:
                result = parser.parse(inp.encode('utf-8'))

                statements = parser.parse_ast(inp.encode('utf-8'))
                for stmt in statements:
                    print('transpiled> {}'.format(transpiler.transpile(stmt)))
            except PaluSyntaxError as e:
                print('?> {}'.format(result.root_node.sexp()))
                print(f'syntax error at {e.line}:{e.column}')
                print(e.tree.root_node.sexp())
    else:
        statements = parser.parse_ast(source.read())
        for stmt in statements:
            out.write(transpiler.transpile(stmt).encode('utf-8'))
            out.write(b'\n')


run()
