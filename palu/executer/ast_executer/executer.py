from palu.executer.stack import Stack
from palu.executer.context import Context


class ASTExecuter:
    def __init__(self, *args, **kwargs):
        self._stack = Stack()
        self._stack.push(Context())

    def exec_(self, ast):
        pass
