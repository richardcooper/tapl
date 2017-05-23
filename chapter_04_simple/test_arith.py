import pytest

from arith import *

expressions_in_normal_form = [
    # Boolean Values
    true_,
    false_,

    # Numeric Values
    zero_,
    succ_(zero_),
    succ_(succ_(succ_(succ_(succ_(succ_(succ_(succ_(succ_(succ_(zero_)))))))))),

    # Non-values which are in normal form because the matching congruence rule
    # cannot reduce the subterm.
    if_(zero_,true_,false_),
    succ_(false_),
    pred_(true_),
    iszero_(false_),
    succ_(pred_(iszero_(if_(zero_,true_,false_)))),

    # Non-values which are in normal form because the matching rules only
    # applies if the subterm is a numeric value.
    pred_(succ_(true_)),
    iszero_(succ_(succ_(false_))),
]

# TODO parametrize this
def test_zero_is_a_numeric_value():
    assert is_numeric_value(zero_)

# TODO parametrize this
def test_succ_zero_is_a_numeric_value():
    assert is_numeric_value(succ_(zero_))

# TODO parametrize this
def test_true_is_not_a_numeric_value():
    assert not is_numeric_value(true_)

# TODO parametrize this
def test_invalid_succ_is_not_a_numeric_value():
    assert not is_numeric_value(succ_(true_))

# TODO parametrize this
def test_true_is_a_value():
    assert is_value(true_)

# TODO parametrize this
def test_false_is_a_value():
    assert is_value(false_)

# TODO parametrize this
def test_if_expression_is_not_a_value():
    assert not is_value(if_(true_, true_, true_))

@pytest.mark.parametrize("test_input,expected_result", [
    (if_(true_, zero_, succ_(zero_)), zero_), # E-IfTrue
    (if_(false_, zero_, succ_(zero_)), succ_(zero_)), # E-IfFalse
    (pred_(zero_), zero_), # E-PredZero
    (pred_(succ_(succ_(zero_))), succ_(zero_)), # E-PredSucc
    (iszero_(zero_), true_), # E-IsZeroZero
    (iszero_(succ_(zero_)), false_), # E-IsZeroSucc
])
def test_reduce_on_computation_rules(test_input, expected_result):
    assert reduce(test_input) == expected_result

@pytest.mark.parametrize("test_input,expected_result", [
    (if_(iszero_(zero_), true_, false_), if_(true_, true_, false_)), # E-If
    (succ_(pred_(zero_)), succ_(zero_)), # E-Succ
    (pred_(pred_(zero_)), pred_(zero_)), # E-Pred
    (iszero_(pred_(zero_)), iszero_(zero_)), # E-IsZero
])
def test_reduce_on_congruence_rules(test_input, expected_result):
    assert reduce(test_input) == expected_result


@pytest.mark.parametrize("test_input", expressions_in_normal_form)
def test_reduce_on_normal_forms(test_input):
    with pytest.raises(NoValidReduction):
        reduce(test_input)

@pytest.mark.parametrize("test_input", expressions_in_normal_form)
def test_evaluate_on_normal_forms(test_input):
    assert evaluate(test_input) == test_input


def test_evaluate_large_expression():
    test_input = if_(
        if_(iszero_(succ_(pred_(succ_(zero_)))), zero_, iszero_(zero_)),
        succ_(pred_(succ_(pred_(zero_)))),
        false_
    )
    expected_result = succ_(zero_)
    assert evaluate(test_input) == expected_result
