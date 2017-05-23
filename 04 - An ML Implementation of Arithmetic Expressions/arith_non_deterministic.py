"""
An implementation of the `arith` language from "Types and Programming Languages".

This code is a copy-and-paste extension to the simpler code in `arith.py`. It
contains two main improvements.

1. The introduction of a `term()` factory function allows for significantly
   more concise definition of ConcreteTerm classes.
2. `reduce()` and `evaluate()` are now generators. This allows them to return
   multiple results in cases where more that one rule matches. This becomes
   important for Exercise 3.5.13. which introduces 2 new rules (E-Funny1 and
   E-Funny2) which introduce exactly that sort of non determinism.
"""


class AbstractTerm:
    """Abstract superclass of the non-primitive terms in our language.

    Subclasses need to define self._template to be a fomatting string which
    describes syntax of the term.
    """

    def __init__(self, *args):
        """Create an object representing a term in our language.

        All args to this fuction represent subterms of our terms. The number of
        such subterms is defined by concrete subclasses of `AbstractTerm`
        defining self._template
        """
        # Pull the names of the sub_terms out of self._template. For example
        # - self._template == 'true'
        #     -> sub_terms == [].
        # - self._template == 'if {t1} then {t2} else {t3}')'
        #     -> sub_terms == ['t1', 't2'm 't3']
        sub_terms = [x.split('}')[0] for x in self._template.split('{')[1:]]

        # Since we don't know how many subterms our subclasses will support we
        # have to use the *args parameter to capture them all regardless of
        # number. That means we have to do our own checking that the correct
        # number fo arguments have been supplied.
        if len(args) != len(sub_terms):
            raise TypeError(f'__init__() takes {len(sub_terms)} positional arguments but {len(args)} were given')

        # Stick all of the arguments into self so that they can be accessed
        # using dot notation.
        self.__dict__.update({k:v for (k,v) in zip(sub_terms, args)})

    def __eq__(self, other):
        """Compare terms for equality by value rather than identity."""
        return type(self) == type(other) and self.__dict__ == other.__dict__

    def __str__(self):
        """Format the term as a string.

        Concrete subclasses of `Term` will need to define self.format.
        """
        return self._template.format(**self.__dict__)

    def __repr__(self):
        """Format the term using parens to make nesting a bit simpler to read."""
        repr_template = self._template.replace('{', '({').replace('}', '!r})')
        return repr_template.format(**self.__dict__)


def term(template):
    """Factory for term classes and singletons.

    Given a string `template` this will create and return a "thing" which can be
    used to constuct language terms matching that template.
    If `template` contains "{}" formatting characters then the "thing" returned
    will be a subclass of `AbstractTerm`.
    If `template` does not contain "{}" formatting characters then the "thing"
    returned will be a singleton instance of a subclass of `AbstractTerm`. This
    reduces the number of parentheses needed when building terms.
    """
    class ConcreteTerm(AbstractTerm):
        _template = template
    if '{' in template:
        return ConcreteTerm
    else:
        # Primitive terms (i.e. terms with no subterms) can be singletons so we
        # return the object here rather than the class. Doing this reduces the
        # number of parentheses needed when building terms.
        return ConcreteTerm()


true_ = term('true')
false_ = term('false')
zero_ = term('0')
if_ = term('if {condition} then {then_branch} else {else_branch}')
succ_ = term('succ {t}')
pred_ = term('pred {t}')
iszero_ = term('iszero {t}')


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


# This will be populated with all of the evaluation rules in our language by the
# @rule decorator.
rules = []


def rule(original_function):
    """Decorator which adds the decorated function to the `rules` global."""
    rules.append(original_function)
    return original_function


@rule
def E_IfTrue(term, rules):
    """Evaluation rule: if true then t₂ else t₃ → t₂."""
    if isinstance(term, if_) and term.condition == true_:
        yield term.then_branch


@rule
def E_IfFalse(term, rules):
    """Evaluation rule: if false then t₂ else t₃ → t₃."""
    if isinstance(term, if_) and term.condition == false_:
        yield term.else_branch


@rule
def E_If(term, rules):
    """Evaluation rule: if t₁ then t₂ else t₃ → if t₁ʹ the t₂ else t₃ given t₁ → t₁ʹ."""
    if isinstance(term, if_):
        for reduced_condition in reduce(term.condition, rules):
            yield if_(reduced_condition, term.then_branch, term.else_branch)


@rule
def E_Succ(term, rules):
    """Evaluation rule: succ t → succ tʹ given t → tʹ."""
    if isinstance(term, succ_):
        for reduced_t in reduce(term.t, rules):
            yield succ_(reduced_t)


@rule
def E_PredZero(term, rules):
    """Evaluation rule: pred 0 → 0."""
    if isinstance(term, pred_) and term.t == zero_:
        yield zero_


@rule
def E_PredSucc(term, rules):
    """Evaluation rule: pred succ nv → nv given nv ∈ NV."""
    if isinstance(term, pred_) and isinstance(term.t, succ_) and is_numeric_value(term.t.t):
        yield term.t.t


@rule
def E_Pred(term, rules):
    """Evaluation rule: pred t → pred tʹ given t → tʹ."""
    if isinstance(term, pred_):
        for reduced_t in reduce(term.t, rules):
            yield pred_(reduced_t)


@rule
def E_IsZeroZero(term, rules):
    """Evaluation rule: iszero 0 → true."""
    if isinstance(term, iszero_) and term.t == zero_:
        yield true_


@rule
def E_IsZeroSucc(term, rules):
    """Evaluation rule: iszero succ nv → false given nv ∈ NV."""
    if isinstance(term, iszero_) and isinstance(term.t, succ_) and is_numeric_value(term.t.t):
        yield false_


@rule
def E_IsZero(term, rules):
    """Evaluation rule: iszero t → iszero tʹ given t → tʹ."""
    if isinstance(term, iszero_):
        for reduced_t in reduce(term.t, rules):
            yield iszero_(reduced_t)


# This deliberately does not have the @rule decorator so that it is not in the
# default set of rules.
def E_Funny1(term, rules):
    """Bad rule: if true the t₂ else t₃ → t₃.

    This is a non-standard "Funny" rule from Execise 3.5.13.
    """
    if isinstance(term, if_) and term.condition == true_:
        yield term.else_branch


# This deliberately does not have the @rule decorator so that it is not in the
# default set of rules.
def E_Funny2(term, rules):
    """Non-standard rule: if t₁ then t₂ else t₃ → if t₁ then t₂ʹ else t₃ given t₂ → t₂ʹ.

    This is a non-standard "Funny" rule from Execise 3.5.13.
    """
    if isinstance(term, if_):
        for reduced_then_branch in reduce(term.then_branch, rules):
            yield if_(term.condition, reduced_then_branch, term.else_branch)


rules_inc_funny_1 = rules + [E_Funny1]
rules_inc_funny_2 = rules + [E_Funny2]


def reduce(term, rules):
    """Generate all results of evaluating `term` a single step using `rules`.

    This generator will evaluate `term` according to the single-step evaluation
    rules defined in chapter 3 section 3.5.3 and yield the resulting terms. If
    multiple rules match `term` then multiple results will be yielded. If no
    rules match then nothing will be yielded.

    This is roughly equivalent to the `eval1` function in Chapter 4's OCaml code.
    """
    for rule in rules:
        yield from rule(term, rules)


def evaluate(term, rules):
    """Generate all results of reducing `term` using `rules` until it cannot be reduced further.

    This generator will evaluate `term` according to the multi-step evaluation
    rules defined in chapter 3 section 3.5.9 and yield the resulting terms. If
    multiple evaluations are possible then multiple results will be yielded. If
    `term` is already in Normal Form and cannot be reduced further then `term`
    will be yielded once unchanged.

    This is roughly equivalent to the `eval` function in Chapter 4's OCaml code.
    """
    bottomed_out = True
    for reduction in reduce(term, rules):
        bottomed_out = False
        yield from evaluate(reduction, rules)
    if bottomed_out:
        yield term


if __name__ == '__main__':
    # Demonstrate non-determinism using E_Funny1
    term = if_(true_, true_, false_)
    print('The rule E_Funny1 introduces non-determinism by breaking the')
    print('definition of "if":')
    print('For example, using the normal rules:')
    print(f'    reduce({term})')
    reductions = list(reduce(term, rules))
    assert len(reductions) == 1
    print('    ->', reductions[0])
    print()
    print('But with E_Funny1 it has two possible reductions:')
    print(f'    reduce({term})')
    for reduction in reduce(term, rules_inc_funny_1):
        print('    ->', reduction)
    print()

    # Demonstrate non-determinism using E_Funny2
    term = if_(true_, pred_(zero_), false_)
    print('E_Funny2 introduces a slightly different type of non-determinism by')
    print('allowing the eager evaluation of then clauses:')
    print(f'    reduce({term})')
    for reduction in reduce(term, rules_inc_funny_2):
        print('    ->', reduction)
    print()
    print('Unlike E_Funny1, E_Funny2 only introduces non-determinism in the')
    print('order of rule evaluation, not in the final result. This means that')
    print('the multi-step evaluation function can yield the same result')
    print('multiple times:')
    print(f'    evaluate({term})')
    for reduction in evaluate(term, rules_inc_funny_2):
        print('    ->*', reduction)
