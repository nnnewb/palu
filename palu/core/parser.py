from typing import Sequence
from palu import stubs
from palu.core.ast.transformer import Transformer
from palu.core.ast.node import ASTNode
from tree_sitter import Language, Parser as TSParser

lang_lib = 'build/palu.dll'

Language.build_library(lang_lib, ['tree-sitter-palu'])
palu = Language(lang_lib, 'palu')


class PaluSyntaxError(Exception):
    def __init__(self, tree, line, column) -> None:
        super().__init__((line, column))
        self.tree = tree
        self.line = line
        self.column = column


class Parser(object):
    def __init__(self) -> None:
        super().__init__()
        self._parser = TSParser()
        self._parser.set_language(palu)
        self._transformer = Transformer()

    def parse(self, source: bytes) -> stubs.Tree:
        tree: stubs.Tree = self._parser.parse(source)
        self.validate_recursive(tree, tree.root_node)

        return tree

    def parse_ast(self, source: bytes) -> Sequence[ASTNode]:
        tree = self.parse(source)
        return self._transformer.transform(source, tree)

    def validate_recursive(self, tree: stubs.Tree, node: stubs.Node):
        if node.has_error or node.is_missing:
            raise PaluSyntaxError(tree, *node.start_point)

        for child in node.children:
            self.validate_recursive(tree, child)
