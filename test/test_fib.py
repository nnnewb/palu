from palu.parser import parse
from palu.transpiler import Transpiler


def test_compile_fib():
    transpiler = Transpiler()
    result = transpiler.transpile(parse(b'''\
    mod fib

    type bytes = *u8
    external fn printf(fmt: bytes, ...) -> i32

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
    assert result =='typedef u8* bytes;extern i32 printf(bytes fmt,...);i32 fib_fib(i32 n) {if((n) == (1)) {return 0;}if((n) == (2)) {return 1;}return (fib((n) - (1))) + (fib((n) - (2)));}'
