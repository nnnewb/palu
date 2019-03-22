from logging import basicConfig, getLogger, FileHandler
from prompt_toolkit import prompt


basicConfig(level='DEBUG', format='%(levelname)8s - %(asctime)10s - %(name)18s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S', handlers=[FileHandler('./parser.log', 'w+')])

# REPL

while True:
    from palu.core.parser import lexer, parser
    logger = getLogger('parser-runtime')
    inp = prompt('REPL => ', multiline=True)
    result = parser.parse(inp, lexer=lexer, debug=logger)
    print('?> {}'.format(result))
