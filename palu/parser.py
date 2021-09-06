from typing import Sequence

from tree_sitter import Language
from tree_sitter import Parser as TSParser

from palu import stubs
from palu.ast import ASTNode, SourceFile
from palu.transform import transform

lang_lib = 'build/palu.dll'

Language.build_library(lang_lib, ['tree-sitter-palu'])
palu = Language(lang_lib, 'palu')


class PaluSyntaxError(Exception):
    def __init__(self, tree, line, column) -> None:
        super().__init__((line, column))
        self.tree = tree
        self.line = line
        self.column = column


_parser: stubs.Parser = TSParser()
_parser.set_language(palu)


def _validate_recursive(tree: stubs.Tree, node: stubs.Node):
    if node.has_error or node.is_missing:
        raise PaluSyntaxError(tree, *node.start_point)

    for child in node.children:
        _validate_recursive(tree, child)


def parse(source: bytes) -> SourceFile:
    tree = _parser.parse(source)
    _validate_recursive(tree, tree.root_node)
    return transform(tree, source)
