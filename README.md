# palu

palu is toy programing language interpreter writing by Python and [PLY](https://github.com/dabeaz/ply).

internal presentation just like scheme.

## mile stone

- [X] simple binary expr syntax
- [X] function call syntax
- [X] branches/loop syntax
- [X] user function syntax
- [ ] AST execute
- [ ] builtin function
- [ ] maybe something else...? I don't known.
- [ ] module
- [ ] AOT/JIT compile support (try LLVM)

## example

### 1. binary expression

```
REPL => (S(t0+deltaT)-S(t0))/deltaT
?> (/ (- (S (+ t0 deltaT)) (S t0)) deltaT)
```

### 2. function call

```
REPL => sqrt(abs(2*2)+abs(2*2));
?> (sqrt (+ (abs (* 2 2)) (abs (* 2 2))))
```

### 3. branches

```
REPL => if dividend then
            divisor/dividend;
        else
            print('dividend should not be zero');
        end
?> (if dividend (then (/ divisor dividend)) (else (print 'dividend should not be zero')))
```

### 4. user function

```
REPL => def fib(n)
            if n == 0 or n == 1 then
                return n;
            else
                return fib(n - 1) + fib(n - 2);
            end
        end
?> (define fib (parameters 'n')
        (if (or (== n 0) (== n 1)) 
        (then 
            (return n)) 
        (else 
            (return 
                (+ (fib (- n 1)) 
                   (fib (- n 2)))))))
```
