"""Tree-Based Equation Solver by Areez Chishtie: Expr Module
(CSC111 Winter 2024 Project 2)

Description
===============================

Contains the Expr class, its subclasses, and related helper functions.

Copyright
===============================

This file is Copyright © 2024 Areez Chishtie. All rights reserved."""

from typing import Any


class Expr:
    """
    An abstract class that represents a mathematical expression.
    """


class MonoData(Expr):
    """
    An expression that represents a numerical quantity associated with a monomial.
    A monomial is a mathematical expression of the form ax^n, where a, n ∈ R.

    Instance Attributes:
        - type: Which numerical quantity self represents:
                'coeff' - coefficient, 'deg' - degree.
        - value: The value of the numerical quantity.

    Representation Invariants:
        - type in {'coeff', 'deg'}
    """
    type: str
    value: float

    def __init__(self, _type: str, value: float) -> None:
        """
        Initialize a MonoData object.
        """
        self.type = _type
        self.value = value

    def __repr__(self) -> str:
        """
        Return a string representing this MonoData object.
        """
        return normalize_fstr(str(self.value))


class Unit(Expr):
    """
    An expression that represents either a sum, product, or monomial.

    Instance Attributes:
        - op: Which operation self represents:
              '+' - sum, '*' - product, 'x' - monomial.
        - terms: The terms within the sum or product, if op is '+' or '*'.
                 A list [a, n] where a, n are coefficient, degree MonoData objects, respectively, if op is 'x'.

    Representation Invariants:
        - op in {'+', '*', 'x'}
        - (op == 'x') == (len(self.terms) == 2
                          and isinstance(self.terms[0], MonoData) and self.terms[0].type == 'coeff'
                          and isinstance(self.terms[1], MonoData) and self.terms[1].type == 'deg')
          # self is a monomial if and only if self.terms consists of one coefficient and one degree MonoData.
        - (op == 'x') or all(isinstance(t, Unit) for t in self.terms)
          # if self is not a monomial, then each of its terms is a Unit.

    >>> sum = Unit('+', [mono(2, 1), mono(1, 1), mono(1, 0), mono(0, 0)])  # 2x + x + 1 + 0
    >>> _ = sum.simplify()
    >>> print(sum)
    (3x + 1)

    >>> prod = Unit('*', [ \
                            Unit('+', [mono(1, 1), mono(-1, 0)]), \
                            Unit('+', [mono(1, 1), mono(1, 0)]) \
                           ])  # (x - 1)(x + 1)
    >>> _ = prod.simplify()
    >>> print(prod)
    (x^2 + -1)

    >>> mon = Unit('*', [mono(2, 1), mono(1, 1), mono(3, 0), mono(1, 0)])  # 2x * x * 3 * 1
    >>> _ = mon.simplify()
    >>> print(mon)
    6x^2

    >>> quad = Unit('+', [ \
                           Unit('*', [ \
                                       Unit('+', [mono(1, 1), mono(3, 0)]), \
                                       Unit('+', [mono(1, 1), mono(3, 0)]) \
                                      ]), \
                           mono(1, 0) \
                           ])  # (x + 3)(x + 3) + 1
    >>> _ = quad.simplify()
    >>> print(quad)
    (x^2 + 6x + 10)
    """
    op: str
    terms: list[Expr]

    def __init__(self, op: str, terms: list[Expr]) -> None:
        """
        Initialize a new Unit.
        """
        self.op = op
        self.terms = terms

    def __repr__(self) -> str:
        """
        Return a string representing this Unit.
        """
        if self.op == 'x':
            coeff, deg = self.terms[0].value, self.terms[1].value

            if deg != 0 and coeff == 1:
                coeff_str = ''
            elif deg != 0 and coeff == -1:
                coeff_str = '-'
            else:
                coeff_str = str(coeff)

            if deg == 0:
                return normalize_fstr(coeff_str)
            elif deg == 1:
                return f'{normalize_fstr(coeff_str)}x'
            else:
                return f'{normalize_fstr(coeff_str)}x^{normalize_fstr(str(deg))}'
        else:
            # Prioritize monomials, in nonincreasing order of degree.
            # After monomials, prioritize products, and then sums.
            self.terms.sort(key=lambda t: (t.terms[1].value if t.op == 'x' else 0,
                                           int(t.op == '*'),
                                           int(t.op == '+')), reverse=True)
            return f'({f" {self.op} ".join([str(t) for t in self.terms])})'

    def simplify(self) -> list[tuple]:
        """
        Simplify the terms in this unit.
        The algorithm aims to *expand* the terms, so that the result is a sum of monomials
        of unique degrees.
        
        Returns a list of graphs (see Unit.get_graph) representing self and its children at 
        each stage of the simplification in chronological order.
        """
        match self.op:
            case '+':
                return self._simplify_sum()
            case '*':
                return self._simplify_prod()
            case 'x':
                return [self.get_graph()]
            case _:  # we should never hit this case due to the representation invariant
                raise ValueError

    def _simplify_sum(self) -> list[tuple]:
        """
        Simplify this sum to obtain a result as in Unit.simplify.

        Returns a list of graphs (see Unit.get_graph) representing self and its children at 
        each stage of the simplification in chronological order.

        Preconditions:
            - self.op = '+'
        """
        graphs = [self.get_graph()]

        # Simplify the terms
        for term in self.terms:
            graphs.append(term.simplify())

        # FLatten the sum (promote nested sums)
        self._flatten_sum()

        # Collect like terms
        coeff_by_deg = {}
        i = 0

        while i < len(self.terms):
            term = self.terms[i]
            if term.op == 'x':
                if term.terms[1].value in coeff_by_deg:
                    coeff_by_deg[term.terms[1].value] += term.terms[0].value
                else:
                    coeff_by_deg[term.terms[1].value] = term.terms[0].value
                self.terms.pop(i)
            else:
                i += 1

        for deg in coeff_by_deg:
            if coeff_by_deg[deg] != 0:  # ignore (+ 0x^)'s
                self.terms.append(mono(coeff_by_deg[deg], deg))

        if len(self.terms) == 0:  # handle (0x^ + ... + 0x^)'s
            self.terms = [MonoData('coeff', 0), MonoData('deg', 0)]
            self.op = 'x'

        # Promote a single-term sum consisting of a monomial
        if len(self.terms) == 1 and self.terms[0].op == 'x':
            self.terms = self.terms[0].terms
            self.op = 'x'

        graphs.append(self.get_graph())

        return flatten_list(graphs)


    def _flatten_sum(self) -> None:
        """
        Flatten this sum so the resulting self.terms does not contain any sums.

        Preconditions:
            - self.op = '+'
        """
        flat_terms = []

        while len(self.terms) > 0:
            term = self.terms.pop(0)
            if term.op == '+':
                term._flatten_sum()
                flat_terms.extend(term.terms)
            else:
                flat_terms.append(term)

        self.terms = flat_terms

    def _simplify_prod(self) -> list[tuple]:
        """
        Simplify this product to obtain a result as in Unit.simplify.

        Returns a list of graphs (see Unit.get_graph) representing self and its children at 
        each stage of the simplification in chronological order.

        Preconditions:
            - self.op = '*'
        """
        graphs = [self.get_graph()]

        # Search for the first sum
        if len(self.terms) == 0:
            return []

        i = 0
        term = self.terms[0]

        while not (i + 1 >= len(self.terms) or term.op == '+'):
            i += 1
            term = self.terms[i]

        # If self.terms contains a sum
        if term.op == '+':
            # Distribute self.terms - [term] over term
            self.terms.pop(i)
            expansion_terms = []
            for subterm in term.terms:
                expansion_terms.append(Unit('*', self.terms + [subterm]))

            # The product becomes a sum
            self.terms = expansion_terms
            self.op = '+'

            # Recursively simplify the sum (which may distribute again if necessary)
            graphs.append(self.simplify())

        # If self.terms only contains products
        else:
            # Collect like factors
            i = 0
            coeff = 1
            deg = 0

            while not (i >= len(self.terms) or coeff == 0):
                term = self.terms[i]
                if term.op == 'x':
                    coeff *= term.terms[0].value
                    deg += term.terms[1].value
                    self.terms.pop(i)
                else:
                    i += 1

            if coeff == 0:  # handle (0x^ * ...)'s
                self.terms = [MonoData('coeff', 0), MonoData('deg', 0)]
                self.op = 'x'
            elif not (deg == 0 and coeff == 1 and len(self.terms) > 0):  # ignore non-isolated (* 1)'s
                self.terms.append(mono(coeff, deg))

            # Promote a single-term product consisting of a monomial
            if len(self.terms) == 1 and self.terms[0].op == 'x':
                self.terms = self.terms[0].terms
                self.op = 'x'

            graphs.append(self.get_graph())

        return flatten_list(graphs)

    def get_graph(self, root: int = 0) -> tuple:
        """
        Return a graph that represents self. The returned value is a tuple (edges, labels), where
            - edges is a list of tuples referring to unique int ids >= root for every term that is a child of self.
              The id with value 'root' corresponds to self, i.e., the root of the graph.
            - labels is a dict mapping int ids to str representations of the terms.
        If the graph has a single vertex (i.e., self is a monomial), then edges = (root, root) is returned.
        Otherwise, the returned graph is a tree (i.e., an acyclic connected graph).
        """
        if self.op == 'x':
            return ([(root, root)], {root: str(self)})
        else:
            edges = []
            labels = {root: self.op}
            i = root + 1

            for term in self.terms:
                edges.append((root, i))
                if term.op == 'x':
                    labels[i] = str(term)
                    i += 1
                else:
                    sub_edges, sub_labels = term.get_graph(i)
                    edges.extend(sub_edges)
                    labels.update(sub_labels)
                    i += len(sub_labels)

            return (edges, labels)


def mono(coeff: float, deg: float) -> Unit:
    """
    Return a Unit representing the monomial with the given coefficient and degree.
    """
    return Unit('x', [MonoData('coeff', coeff), MonoData('deg', deg)])


def normalize_fstr(s: str) -> str:
    """
    Return a normalized string for a float by removing any trailing zeroes after the decimal.

    Preconditions:
        - s represents a float.
    """
    return s.rstrip('0').rstrip('.') if '.' in s else s


def flatten_list(lst: Any) -> list:
    """
    Return a flat (un-nested) list containing
        - lst, if lst is not a list; or
        - the same elements as lst, if list is a list.
    """
    if not isinstance(lst, list):
        return [lst]
    else:
        flat_lst = []
        for sublst in lst:
            flat_lst.extend(flatten_list(sublst))
        return flat_lst


if __name__ == '__main__':
    import doctest
    doctest.testmod(verbose=True)

    import python_ta
    python_ta.check_all(config={
        'max-line-length': 120,
        'disable': ['E1136', 'E1101'],
        # 'extra-imports': [],
        'max-nested-blocks': 4
    })
