from typing import Sequence, Tuple
from palu.ast.node import Node


class ModDeclare(Node):
    def __init__(self, start: Tuple[int, int], end: Tuple[int, int], name: str) -> None:
        super().__init__(start, end)
        self.name = name


class SourceFile(Node):
    def __init__(self, start: Tuple[int, int], end: Tuple[int, int], statements: Sequence[Node]) -> None:
        super().__init__(start, end)
        self.mod = ''
        self.statements = statements

        for stmt in self.statements:
            if isinstance(stmt, ModDeclare):
                self.mod = stmt.name
