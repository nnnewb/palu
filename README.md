# palu

palu is toy programing language interpreter writing by Python and [tree-sitter](https://tree-sitter.github.io/tree-sitter/).

## compiler features

- [x] intermediate ast structure
- [x] very basic transpiler
- [ ] type checker
- [ ] optimizer

## language features

- [x] variable in scalar type
- [x] if
- [x] else
- [x] while
- [x] fn
- [ ] slice(array?)
- [ ] pointer

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