"""Some useful definitions from the book."""

from arith import *


def constants(term):
    """Return the set of constants appearing in `term`.

    This is as per definition 3.3.1 in the book.
    """
    if term in (true_, false_, zero_):
        return {term}
    if isinstance(term, (succ_, pred_, iszero_)):
        return constants(term.t)
    if isinstance(term, if_):
        return constants(term.condition) | constants(term.then_branch) | constants(term.else_branch)


def size(term):
    """Return the number of nodes in the abstract syntax tree of `term`.

    This is as per definition 3.3.2 in the book.
    """
    if term in (true_, false_, zero_):
        return 1
    if isinstance(term, (succ_, pred_, iszero_)):
        return size(term.t) + 1
    if isinstance(term, if_):
        return size(term.condition) + size(term.then_branch) + size(term.else_branch) + 1


def depth(term):
    """Return the depth of the abstract syntax tree of `term`.

    This is as per definition 3.3.3 in the book.
    """
    if term in (true_, false_, zero_):
        return 1
    if isinstance(term, (succ_, pred_, iszero_)):
        return depth(term.t)
    if isinstance(term, if_):
        return max(depth(term.condition), depth(term.then_branch), depth(term.else_branch)) + 1


def is_normal_form(term):
    """Return whether `term` is a Normal Form. I.e. It cannot be evaluated any further.

    This is as per definition 3.5.6 in the book.
    """
    try:
        reduce(term)
        return False
    except NoValidReduction:
        return True
