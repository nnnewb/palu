from palu.parser import parse
from palu.transpiler import Transpiler


def test_compile_fib():
    transpiler = Transpiler()
    transpiler.transpile(parse(b'''\
    mod fib

    fn fib(n: i32) -> i32 do
        if n == 1 do
            return 0
        end

        if n == 2 do
            return 1
        end

        return fib(n-1) + fib(n-2)
    end
    '''))
