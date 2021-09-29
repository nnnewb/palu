from enum import Enum
from typing import Optional, Sequence


class AmbiguousException(Exception):
    def __init__(self, msg) -> None:
        super().__init__(msg)


class Qualifier(Enum):
    Const = 'const'
    Volatile = 'volatile'
    Export = 'export'
    Extern = 'extern'
    Static = 'static'


class PaluSymbol(object):
    def __init__(self, name: str, specifier: Optional['PaluSymbol'], qualifiers: Sequence[Qualifier], *,
                 is_variable: bool = False, is_pointer: bool = False, is_slice: bool = False, is_array: bool = False, array_size: Optional[int] = None,
                 is_function: bool = False, params: Optional[Sequence['PaluSymbol']] = None, ret: Optional['PaluSymbol'] = None, function_receiver: Optional['PaluSymbol'] = None,
                 is_struct: bool = False, struct_fields: Optional[Sequence['PaluSymbol']] = None,
                 is_union: bool = False, union_fields: Optional[Sequence['PaluSymbol']] = None,
                 is_enum: bool = False, enum_fields: Optional[Sequence['PaluSymbol']] = None,
                 is_type_alias: bool = False,
                 is_builtin_type: bool = False) -> None:
        super().__init__()
        self._name = name
        self._specifier = specifier
        self._qualifiers = set(qualifiers)

        # variable
        self._is_variable = is_variable
        self._is_pointer = is_pointer
        self._is_slice = is_slice
        self._is_array = is_array
        self._array_size = array_size

        if self._is_variable:
            if self._is_pointer and self._is_slice:
                raise AmbiguousException("is pointer also slice")

            if self._is_pointer and self._is_array:
                raise AmbiguousException("is pointer also array")

            if self._is_array and self._is_slice:
                raise AmbiguousException("is array also slice")

        # function
        self._is_function = is_function
        self._params = params
        self._ret = ret
        self._function_receiver = function_receiver

        self._is_type_decl = False

        # struct
        self._is_struct = is_struct
        self._struct_fields = struct_fields

        # union
        self._is_union = is_union
        self._union_fields = union_fields

        # enum
        self._is_enum = is_enum
        self._enum_fields = enum_fields

        # alias
        self._is_type_alias = is_type_alias

        if self._is_struct or self._is_enum or self._is_union or self._is_type_alias:
            self._is_type_decl = True

        # builtin types
        self._is_builtin_type = is_builtin_type

    @property
    def name(self):
        return self._name

    @property
    def specifier(self):
        return self._specifier

    @property
    def is_static(self):
        return self._qualifiers.issubset((Qualifier.Static,))

    @property
    def is_export(self):
        return self._qualifiers.issubset((Qualifier.Export,))

    @property
    def is_extern(self):
        return self._qualifiers.issubset((Qualifier.Extern,))

    @property
    def is_const(self):
        return self._qualifiers.issubset((Qualifier.Const,))

    @property
    def is_volatile(self):
        return self._qualifiers.issubset((Qualifier.Volatile,))

    @property
    def is_variable(self):
        return self._is_variable

    @property
    def is_pointer(self):
        return self._is_pointer

    @property
    def is_slice(self):
        return self._is_slice

    @property
    def is_array(self):
        return self._is_array

    @property
    def array_size(self):
        return self._array_size

    @property
    def is_function(self):
        return self._is_function

    @property
    def params(self):
        return self._params

    @property
    def ret(self):
        return self._ret

    @property
    def function_receiver(self):
        return self._function_receiver

    @property
    def is_struct(self):
        return self._is_struct

    @property
    def struct_fields(self):
        return self._struct_fields

    @property
    def is_union(self):
        return self._is_union

    @property
    def union_fields(self):
        return self._union_fields

    @property
    def is_enum(self):
        return self._is_enum

    @property
    def enum_fields(self):
        return self._enum_fields

    @property
    def is_type_alias(self):
        return self._is_type_alias

    @property
    def is_type_decl(self):
        return self._is_type_decl

    @property
    def is_builtin_type(self):
        return self._is_builtin_type
