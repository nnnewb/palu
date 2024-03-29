from palu.transpiler import Transpiler
import click
from prompt_toolkit import prompt

from palu.parser import PaluSyntaxError, parse


@click.command()
def run():
    transpiler = Transpiler()
    while True:
        inp = prompt('REPL => ')
        try:
            src = parse(inp.encode('utf-8'))
            print('transpiled> {}'.format(transpiler.transpile(src)))
        except PaluSyntaxError as e:
            print(f'syntax error at {e.line}:{e.column}')
            print(e.tree.root_node.sexp())


run()
