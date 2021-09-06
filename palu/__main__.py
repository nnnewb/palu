import io

import click
from prompt_toolkit import prompt

from palu.parser import PaluSyntaxError, parse
from palu.transpiler import Transpiler


@click.command()
@click.option('--repl/--no-repl', default=False)
@click.option('-o', '--out', type=click.File('wb+', lazy=True), default='source.c')
@click.argument('source', type=click.File('rb'), required=False)
def run(repl: bool, out: io.FileIO, source: io.FileIO):
    transpiler = Transpiler()

    if repl:
        while True:
            inp = prompt('REPL => ')
            try:
                src = parse(inp.encode('utf-8'))
                print('transpiled> {}'.format(transpiler.transpile(src)))
            except PaluSyntaxError as e:
                print(f'syntax error at {e.line}:{e.column}')
                print(e.tree.root_node.sexp())
    else:
        src = parse(source.read())
        out.write(transpiler.transpile(src).encode('utf-8'))


run()
