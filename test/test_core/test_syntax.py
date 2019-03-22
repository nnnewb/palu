from palu.core.parser import parser
from test.utils import expect_ast


def test_parse_mathematical_expr():
    result = parser.parse('1 + 2 * 3 / 4')
    expect = ('+', 1, ('*', 2, ('/', 3, 4)))
    expect_ast(result, expect)


def test_parse_fn_and_var():
    result = parser.parse('(S(t0+deltaT)-S(t0))/deltaT')
    expect = ('/', ('-', ('S', ('+', 't0', 'deltaT')), ('S', 't0')), 'deltaT')
    expect_ast(result, expect)


def test_parse_branches():
    result = parser.parse('if true then f1() else f2() end')
    expect = ('if', 'true', ('then', ('f1', )), ('else', ('f2', )))
    expect_ast(result, expect)


def test_parse_user_fn():
    result = parser.parse('def fn(n) return n + 1 end')
    expect = ('define', 'fn', ('parameters', 'n'), ('return', ('+', 'n', 1)))
    expect_ast(result, expect)
