from palu.core.ast import ASTNode, Identifier, ASTType


def expect_ast(ast, expect):
    for node, ex in zip(ast, expect):
        if isinstance(node, ASTNode):
            expect_ast(node, ex)
        elif isinstance(node, Identifier):
            assert node.identifier == ex
        elif isinstance(node, ASTType):
            assert node.value == ex
        else:
            assert node == ex
