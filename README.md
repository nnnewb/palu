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
