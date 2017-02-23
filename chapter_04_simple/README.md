# TaPL Chapter 4 - ~~An ML~~ *A Python* Implementation of Arithmetic Expressions

Chapter 3 of [TaPL](https://www.cis.upenn.edu/~bcpierce/tapl/) describes a
simple untyped language of boolean and arithmetic expressions. Chapter 4 goes on
to present an implementation of that language written in OCaml. This is an
implementation of that same language using Python.

Briefly a program in the language consists of a single expression built from:
- The boolean constants `true` and `false`
- The number `zero`
- The arithmetic functions `succ` (successor) and `pred` (predecessor)
- The function `iszero` which returns `true` what applied to `zero` and `false`
   when applied to any other number
- The conditional operator `if` which takes the form `if t1 then t2 else t3`
   and, as you would expect, evaluates to either t2 or t3 depending on the truth
   of t1

More information can be found on the LCC wiki:
- [Discussion of the material](https://github.com/computationclub/computationclub.github.io/wiki/Types-and-Programming-Languages-Chapter-3-Untyped-Arithmetic-Expressions)
- [Implementations by other members](https://github.com/computationclub/computationclub.github.io/wiki/Types-and-Programming-Languages-Chapter-4-An-ML-Implementation-of-Arithmetic-Expressions)
