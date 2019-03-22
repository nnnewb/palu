from palu.core.parser import parser
from palu.core.ast import ASTNode, ASTType


def test_parse_binary_expr():
    script = """
    (S(t0 + deltaT) - S(t0)) / deltaT;
    """
    result = parser.parse(script)
    assert isinstance(result, ASTNode)
    assert isinstance(result[2], ASTNode)


def test_parse_fn_call():
    script = """
    fn(123,456,789);
    """
    result = parser.parse(script)
    assert isinstance(result, ASTNode)
    assert result[0].identifier == 'fn'
    assert result[1] == 123
    assert result[2] == 456
    assert result[3] == 789

    script = """
    fn(1, 2, 3, arg1, arg2, arg3, 1 + 1, 2 - 1, nestfn(), '123', '456');
    """
    result = parser.parse(script)
    print(result)
