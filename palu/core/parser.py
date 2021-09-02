from palu.core.ast.transformer import Transformer
from tree_sitter import Language, Parser as TSParser

lang_lib = 'build/palu.dll'

Language.build_library(lang_lib, ['tree-sitter-palu'])
palu = Language(lang_lib, 'palu')


class TextDocument(object):
    def __init__(self, filename, source) -> None:
        super().__init__()
        self.filename = filename
        self.source = source
        self.lines = source.splitlines()

    def get_line(self, lineno):
        return self.lines[lineno]


class PaluSyntaxError(Exception):
    def __init__(self, line, column) -> None:
        super().__init__((line, column))
        self.line = line
        self.column = column


class Parser(object):
    def __init__(self) -> None:
        super().__init__()
        self._parser = TSParser()
        self._parser.set_language(palu)
        self._source = TextDocument('', '')
        self._transformer = Transformer()

    def parse(self, filename: str, source: str):
        self._source = TextDocument(filename, source)
        tree = self._parser.parse(source.encode('utf-8'))
        self.validate_recursive(tree.root_node)

        return tree

    def parse_ast(self, filename, source):
        tree = self.parse(filename, source)
        self._transformer.transform(source, tree)

    def validate_recursive(self, node):
        if node.has_error or node.is_missing:
            raise PaluSyntaxError(*node.start_point)

        for child in node.children:
            self.validate_recursive(child)
