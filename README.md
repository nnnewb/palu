# palu

palu is toy programing language interpreter writing by Python and [tree-sitter](https://tree-sitter.github.io/tree-sitter/).

## roadmap

**type checker**
  * [ ] check symbol redefine
    * [ ] ... check name conflict after name mangling
  * [ ] check symbol exists
  * [ ] simple type check: exact match
    * [ ] initialize
    * [ ] assignment
    * [ ] passing argument

**mod**
  * [ ] source files
    * [ ] function/method declarations
    * [ ] struct declaration
    * [ ] variables declaration

**native types**
  * [ ] scalar
    * [ ] i1/i8/i16/i32/i64/u8/u16/u32/u64 ... integral types
    * [ ] f32/f64 ... float types
    * [ ] pointer (raw pointer)
    * [ ] enum (as integral)
  * [ ] compound
    * [ ] struct
    * [ ] union
    * [ ] array (constant size, pass by reference)
  * [ ] function
    * [ ] method (this pointer as first parameter)
    * [ ] plain function
      * [ ] export function (as plain c function, no name mangling)
    * [ ] closure (how?)
  * [ ] external
    * [ ] macro (#define)
      * [ ] with feature rich macro language?
    * [ ] variable (global var)
    * [ ] function (C function, with optional call convention)

**builtin types**
  * [ ] linear
    * [ ] string (immutable, pass by reference)
    * [ ] slice (literal syntax, variadic size, pass by reference)
  * [ ] mapping
    * [ ] dict (literal syntax, just like python)

## try it!

let's have a try!

```bash
python -m palu test/fibonacci.palu -o fibonacci.c
gcc fibonacci.c -o fib
./fib
```

sample code:

```palu
mod fib

external fn printf(fmt: string, n: i32) -> i32

fn fib(n: i32) -> i32 do
    if n == 1 do
        return 0
    end

    if n == 2 do
        return 1
    end

    return fib(n-1) + fib(n-2)
end

fn main(void) -> i32 do
    let n: i32 = fib(6)
    while n < 10 do
        n += 1
    end
    printf("%d", n)
    return 0
end
```

transpile result

```c
// mod fib
// (external (declare printf fmt : string n : i32 i32))
int fib(int n) {
  if ((n == 1)) {
    return 0;
  }
  if ((n == 2)) {
    return 1;
  }
  return (fib((n - 1)) + fib((n - 2)));
}
int main() {
  int n = fib(6);
  while ((n < 10)) {
    n += 1;
  }
  printf("%d", n);
  return 0;
}
```