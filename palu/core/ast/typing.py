from typing import Union
from .expr import IdentExpr, TypedIdent


class Typing(object):
    def __init__(self, *ident) -> None:
        super().__init__()
        self.type_ident = ident


class FunctionSignature(object):
    def __init__(self, ret: Union[IdentExpr, 'FunctionSignature'], *params: TypedIdent) -> None:
        super().__init__()
        self.params = params
        self.ret = ret
