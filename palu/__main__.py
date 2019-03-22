from logging import basicConfig
from prompt_toolkit import prompt

from palu.core.parser import lexer, parser

basicConfig(level='DEBUG', format='%(levelname)8s - %(asctime)10s - %(name)18s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S')

# REPL

while True:
    inp = prompt('REPL => ', multiline=True)
    result = parser.parse(inp, lexer=lexer)
    print('?> {}'.format(result))
