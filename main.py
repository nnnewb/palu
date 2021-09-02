from tree_sitter import Language, Parser
from prompt_toolkit import prompt
import tree_sitter

lang_lib = 'build/palu.dll'

Language.build_library(lang_lib, ['tree-sitter-palu'])
palu = Language(lang_lib, 'palu')

parser = Parser()
parser.set_language(palu)

while True:
    inp = prompt('REPL => ')
    tree = parser.parse(inp.encode('utf-8'))
    print('?> {}'.format(tree.root_node.sexp()))
