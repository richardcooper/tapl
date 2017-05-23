import re

from inference import Syntax, Rule, Rules


class SimplyTypedLambdaCalculus(Rules):
    # Syntax
    # This grammar differs slightly from what's in the book. I'm using a
    # recursive decent parser so I need to avoid left-recursive productions.
    # I do that in term and type by introducing termʹ and typeʹ and doing the
    # usual transformations to remove the left-recursion.
    rule = Syntax(
        '{context} ⊢ {term} : {type}',
        '{var} : {type} ∈ {context}',
    )
    term = Syntax(
        '( {term} ) {termʹ}',
        'true {termʹ}',
        'false {termʹ}',
        'if {term} then {term} else {term} {termʹ}',
        '{var} {termʹ}',
        'λ {var} : {type} . {term} {termʹ}',
    )
    termʹ = Syntax(
        '{term} {termʹ}',
        '',
    )
    var = Syntax(
        re.compile(r"[a-z]('+|\b)")
    )
    type = Syntax(
        '( {type} ) {typeʹ}',
        '{base_type} {typeʹ}',
    )
    typeʹ = Syntax(
        '→ {type} {typeʹ}',
        '',
    )
    base_type = Syntax(
        'Bool',
    )
    context = Syntax(
        '( {context} )',
        '∅',
        '{var} : {type} , {context}'
    )

    # Lambda Calculus Typing
    T_VAR = Rule('{Γ} ⊢ {x}:{T}', given=[
        '{x}:{T} ∈ {Γ}'
    ])
    T_ABS = Rule('{Γ} ⊢ λ{x}:{T1}.{t2} : {T1}→{T2}', given=[
        '{x}:{T1},{Γ} ⊢ {t2} : {T2}',
    ])
    T_APP = Rule('{Γ} ⊢ {t1} {t2} : {T12}', given=[
        '{Γ} ⊢ {t1} : {T11}→{T12}',
        '{Γ} ⊢ {t2} : {T11}',
    ])

    # Boolean Typing
    T_TRUE = Rule('{Γ} ⊢ true : Bool')
    T_FALSE = Rule('{Γ} ⊢ false : Bool')
    T_IF = Rule('{Γ} ⊢ if {t1} then {t2} else {t3} : {T}', given=[
        '{Γ} ⊢ {t1} : Bool',
        '{Γ} ⊢ {t2} : {T}',
        '{Γ} ⊢ {t3} : {T}',
    ])

    # List Membership
    M_HEAD = Rule('{x}:{T} ∈ {x}:{T}, {Γ}')
    M_TAIL = Rule('{x}:{T} ∈ {y}:{T1}, {Γ}', given=[
        '{x}:{T} ∈ {Γ}',
    ])

    @classmethod
    def infer_type(cls, expression, context='∅'):
        goal = f'{context} ⊢ {expression} : {{__result__}}'
        return cls.solve(goal)
