class FunctionCallExpr:

    def __init__(self, function_name, *args, **kwargs):
        self.function_name = function_name
        self.positional_arguments = args
        self.keyword_arguments = kwargs


class BinaryExpr:

    def __init__(self, operator, l_operand, r_operand):
        self.operator = operator
        self.left_operand = l_operand
        self.right_operand = r_operand


class FuncCall:

    def __init__(self, identifier, args):
        self.func_identifier = identifier
        self.func_args = args


class FuncCallArgs:

    def __init__(self, *args, **kwargs):
        self.positional_args = [*args]
        self.keyword_args = {**kwargs}


class WhileLoop:

    def __init__(self, condition, do_block):
        self.condition = condition
        self.do_block = do_block


class CodeBlock:

    def __init__(self, *expr):
        self.all_expr = [*expr]
