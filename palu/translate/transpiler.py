from abc import ABCMeta


class Transpiler(metaclass=ABCMeta):
    def __init__(self) -> None:
        super().__init__()

    def transpile(self, tree):
        raise NotImplemented

    def transpile_statement(self):
        raise NotImplemented

    def transpile_declare_stmt(self):
        raise NotImplemented

    def transpile_external_stmt(self):
        raise NotImplemented

    def transpile_while_stmt(self):
        raise NotImplemented

    def transpile_if_stmt(self):
        raise NotImplemented

    def transpile_else_stmt(self):
        raise NotImplemented

    def transpile_return_stmt(self):
        raise NotImplemented

    def transpile_expr(self):
        raise NotImplemented

    def transpile_ident_expr(self):
        raise NotImplemented

    def transpile_binary_expr(self):
        raise NotImplemented

    def transpile_unary_expr(self):
        raise NotImplemented

    def transpile_cond_expr(self):
        raise NotImplemented

    def transpile_call_expr(self):
        raise NotImplemented

    def transpile_lambda_expr(self):
        raise NotImplemented

    def transpile_parenthesized_expr(self):
        raise NotImplemented

    def transpile_number_literal(self):
        raise NotImplemented

    def transpile_string_literal(self):
        raise NotImplemented

    def transpile_true_literal(self):
        raise NotImplemented

    def transpile_false_literal(self):
        raise NotImplemented

    def transpile_null_literal(self):
        raise NotImplemented
