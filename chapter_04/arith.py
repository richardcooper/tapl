"""
An implementation of the `arith` language from "Types and Programming Languages".

Chapter 3 of TaPL describes a simple untyped language of boolean and arithmetic
expressions. Chapter 4 goes on to present an implementation of that language
written in OCaml. This is an implementation of that same language using Python.

Briefly a program in the language consists of a single expression built from:
 - The boolean constants `true` and `false`
 - The number `zero`
 - The arithmetic functions `succ` (successor) and `pred` (predecessor)
 - The function `iszero` which returns `true` what applied to `zero` and `false`
   when applied to any other number
 - The conditional operator `if` which takes the form "if t1 then t2 else t3"
   and, as you would expect, evaluates to either t2 or t3 depending on the truth
   of t1

This implementation is pretty simple. That simplicity comes with a few costs:
 - There is a bunch of repetition and boilerplate in defining the terms.
 - reduce() is a big-old-pile of `if` statements which don't look very much like
   the rules they are derived from.
 - reduce() and evaluate() only return a single result. That is not a problem
   for the `arith` language because all of those rules are disjoint, but that's
   not the case in general. For example, adding rule E-Funny1 or E-Funny2 from
   Exercise 3.5.13 should make evaluation non-deterministic but we cannot model
   that using this code, instead this code would always pick a single evaluation
   based on whichever rule comes first in reduce().
"""

# The primitive terms in our language. Using strings rather than True, False and
# 0 ensures these terms don't accidentally inherit any semantics from Python.
true_ = 'true'
false_ = 'false'
zero_ = '0'


class Term:
    """Abstract superclass of the non-primitive terms in our language."""

    def __eq__(self, other):
        """Compare terms for equality by value rather than identity."""
        return type(self) == type(other) and self.__dict__ == other.__dict__

    def __str__(self):
        """Format the term as a string.

        Concrete subclasses of `Term` will need to define self.format.
        """
        return self.template.format(**self.__dict__)

    def __repr__(self):
        """Format the term using parens to make nesting a bit simpler to read."""
        repr_template = self.template.replace('{', '({').replace('}', '!r})')
        return repr_template.format(**self.__dict__)


class if_(Term):
    def __init__(self, condition, then_branch, else_branch):
        self.condition = condition
        self.then_branch = then_branch
        self.else_branch = else_branch
        self.template = 'if {condition} then {then_branch} else {else_branch}'


class succ_(Term):
    def __init__(self, t):
        self.t = t
        self.template = 'succ {t}'


class pred_(Term):
    def __init__(self, t):
        self.t = t
        self.template = 'pred {t}'


class iszero_(Term):
    def __init__(self, t):
        self.t = t
        self.template = 'iszero {t}'


def is_value(term):
    """Return whether `term` is a value.

    A  value in the `arith` language is either true, false or a numeric value as
    defined by `is_numeric_value()`.
    """
    return term == true_ or term == false_ or is_numeric_value(term)


def is_numeric_value(term):
    """Return whether `term` is a numeric value.

    A numeric value in the `arith` language is either 0 or succ of another
    numeric value. E.g.: '0', 'succ 0', 'succ succ 0', etc.
    """
    while isinstance(term, succ_):
        term = term.t
    return term == zero_


class NoValidReduction(Exception):
    """Raised by `reduce(term)` if `term` cannot be reduced further."""


def reduce(term):
    """Reduce `term` a single step and return the resulting new term.

    Returns the result of evaluating `term` once according to the single-step
    evaluation rules defined in chapter 3 section 3.5.3.

    Will raise NoValidReduction() if no rules apply.

    This is equivalent to the `eval1` function in Chapter 4's OCaml code.
    """
    # E-IfTrue
    if isinstance(term, if_) and term.condition == true_:
        return term.then_branch
    # E-IfFalse
    if isinstance(term, if_) and term.condition == false_:
        return term.else_branch
    # E-If
    if isinstance(term, if_):
        return if_(reduce(term.condition), term.then_branch, term.else_branch)
    # E-Succ
    if isinstance(term, succ_):
        return succ_(reduce(term.t))
    # E-PredZero
    if isinstance(term, pred_) and term.t == zero_:
        return zero_
    # E-PredSucc
    if isinstance(term, pred_) and isinstance(term.t, succ_) and is_numeric_value(term.t.t):
        return term.t.t
    # E-Pred
    if isinstance(term, pred_):
        return pred_(reduce(term.t))
    # E-IsZeroZero
    if isinstance(term, iszero_) and term.t == zero_:
        return true_
    # E-IsZeroSucc
    if isinstance(term, iszero_) and isinstance(term.t, succ_) and is_numeric_value(term.t.t):
        return false_
    # E-IsZero
    if isinstance(term, iszero_):
        return iszero_(reduce(term.t))

    raise NoValidReduction()


def evaluate(term):
    """Reduce `term` repeatedly until it cannot be reduced further.

    Returns the result of evaluating `term`  according to the multi-step
    evaluation rules defined in chapter 3 section 3.5.9. The result will be in
    Normal Form as defined in chapter 3 section 3.5.6

    If `term` is already in Normal Form and cannot be reduced further then
    `term` will be returned unchanged.

    This is equivalent to the `eval` function in Chapter 4's OCaml code.
    """
    try:
        while True:
            term = reduce(term)
    except NoValidReduction:
        return term


if __name__ == '__main__':
    # Evaluate an example term. I've picked this term because it uses all 10
    # rules during its evaluation.
    term = if_(
        if_(iszero_(succ_(pred_(succ_(zero_)))), zero_, iszero_(zero_)),
        succ_(pred_(succ_(pred_(zero_)))),
        false_
    )
    print('Example term:', term)
    print('Evaluates to:', evaluate(term))
    print('')
    print('The steps in that evaluation are:')
    print('   ', term)
    try:
        while True:
            term = reduce(term)
            print(' ->', term)
    except NoValidReduction:
        print('')
