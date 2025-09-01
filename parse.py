"""Tree-Based Equation Solver by Areez Chishtie: Parse Module
(CSC111 Winter 2024 Project 2)

Description
===============================

Contains functions relating to parsing input strings.

Copyright
===============================

This file is Copyright © 2024 Areez Chishtie. All rights reserved."""

from equation import *


def get_equation(string: str) -> Equation:
    """
    Returns an Equation representing the given string.

    Preconditions:
        - string is of the form 'left = right',
            where left and right are strings satisfying the preconditions of get_unit
    
    >>> eqn = get_equation('(2x + x + 1) = (2x * x * 3)')
    >>> print(eqn)
    (2x + x + 1) = (2x * x * 3)
    """
    left, right = string.split(' = ')
    return Equation(get_unit(left), get_unit(right))


def get_unit(string: str) -> Unit:
    """
    Returns a Unit representing the given string.

    Preconditions:
        - string ∈ S, where the set S is defined recursively as follows:
            Base cases:
                1. a ∈ S for all a ∈ R
                2. x ∈ S
                3. -x ∈ S
                4. ax ∈ S for all a ∈ R
                5. x^n ∈ S for all n ∈ R
                6. ax^n ∈ S for all a, n ∈ R
            Constructor cases:
                If p1, ..., pk ∈ S, then
                1. (p1 + ... + pk) ∈ S
                2. (p1 * ... * pk) ∈ S
    
    >>> bc_1 = get_unit('37')
    >>> print(bc_1)
    37

    >>> bc_2 = get_unit('x')
    >>> print(bc_2)
    x

    >>> bc_3 = get_unit('-6x')
    >>> print(bc_3)
    -6x

    >>> bc_4 = get_unit('x^12')
    >>> print(bc_4)
    x^12

    >>> bc_5 = get_unit('100x^8')
    >>> print(bc_5)
    100x^8

    >>> cc_1 = get_unit('(6x^2 + x + x + -17)')
    >>> print(cc_1)
    (6x^2 + x + x + -17)

    >>> cc_2 = get_unit('(x * 2x * 4)')
    >>> print(cc_2)
    (x * 2x * 4)

    >>> quad = get_unit('(((x + 3) * (x + 3)) + 1)')
    >>> print(quad)
    (((x + 3) * (x + 3)) + 1)
    """
    # Base cases
    if '+' not in string and '*' not in string:
        x_pos = string.find('x')
        if x_pos == -1:  # 1
            coeff = string
            deg = 0
        elif x_pos == 0:  # 2 or 5
            coeff = 1
            if len(string) == 1:  # 2
                deg = 1
            else:  # 4
                deg = string[x_pos + 2:]
        elif string == '-x':  # 3
            coeff = -1
            deg = 1
        else:  # 4 or 6
            coeff = string[:x_pos]
            if x_pos == len(string) - 1:  # 4
                deg = 1
            else:  # 6
                deg = string[x_pos + 2:]

        return mono(float(coeff), float(deg))

    # Constructor cases
    else:
        op_looking_for = ''
        ops_found = []
        depth = 0

        for i in range(len(string)):
            c = string[i]
            if c == '(':
                depth += 1
            elif c == ')':
                depth -= 1
            elif depth == 1 and c == op_looking_for:
                ops_found.append(i)
            elif depth == 1 and op_looking_for == '' and c in {'+', '*'}:
                op_looking_for = c
                ops_found.append(i)

        term_strings = [
            string[1:ops_found[0] - 1],
            string[ops_found[len(ops_found) - 1] + 2:-1]
        ]

        for i in range(1, len(ops_found)):
            term_strings.append(string[ops_found[i - 1] + 2:ops_found[i] - 1])

        terms = []

        for term_string in term_strings:
            terms.append(get_unit(term_string))

        return Unit(op_looking_for, terms)


if __name__ == '__main__':
    import doctest
    doctest.testmod(verbose=True)

    import python_ta
    python_ta.check_all(config={
        'max-line-length': 120,
        'disable': ['E1136', 'E1101', 'W0401', 'R0912'],
        'extra-imports': ['equation'],
        'max-nested-blocks': 4
    })
