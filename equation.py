"""Tree-Based Equation Solver by Areez Chishtie: Equation Module
(CSC111 Winter 2024 Project 2)

Description
===============================

Contains the Equation class and related helper functions.

Copyright
===============================

This file is Copyright © 2024 Areez Chishtie. All rights reserved."""

import math
from expr import *


class Equation:
    """
    A mathematical equation.

    Instance Attributes:
        - left: The expression on the left-hand side of the equation.
        - right: The expression on the right-hand side of the equation.
    """
    left: Unit
    right: Unit

    def __init__(self, left: Unit, right: Unit) -> None:
        """
        Initialize an Equation.
        """
        self.left = left
        self.right = right

    def __repr__(self) -> str:
        """
        Return a string representing this Equation.
        """
        return f'{self.left} = {self.right}'

    def solve(self, n: int) -> tuple[set[float], list]:
        """
        Solve this equation if the degrees of left and right are in {0, 1, 2}.
        Returns the tuple (sols, graphs), where
            - sols...
                - contains all (if any) solutions to the equation in x rounded to n decimal places,
                        if there are finitely-many solutions.
                - equals {float('inf')} if there are infinitely-many solutions.
                - equals {float('nan')} if the degrees of left or right are not in {0, 1, 2}.
            - graphs is a list of graphs (see Unit.get_graph) representing self and its left/right sides
              at each stage of the solution in chronological order.

        >>> left = Unit('+', [mono(2, 1), mono(1, 1), mono(1, 0)])  # 2x + x + 1
        >>> right = Unit('*', [mono(2, 1), mono(1, 1), mono(3, 0), mono(1, 0)])  # 2x * x * 3
        >>> eqn = Equation(left, right)  # 2x + x + 1 = 2x * x * 3  <==>  -6x^2 + 3x + 1 = 0
        >>> eqn.solve(5)[0] == {-0.22871, 0.72871}
        True
        """
        graphs = []

        # Create initial equation graph
        graphs.append(merge_graphs(self.left.get_graph(), self.right.get_graph(), '='))

        # Simplify both sides, and create left side, right side, and simplified equation graphs
        left_graphs = self.left.simplify()
        right_graphs = self.right.simplify()
        eqn_graph_simple = merge_graphs(left_graphs[-1], right_graphs[-1], '=')

        graphs.extend(left_graphs)
        graphs.extend(right_graphs)
        graphs.append(eqn_graph_simple)

        # Subtract right from left, and simplify left one final time to collect like-terms
        if self.left.op == 'x':  # if left is a monomial
            self.left = Unit('+', [self.left])  # then set left to a single-term sum in prep

        if self.right.op == 'x':  # if right is a monomial
            self.right.terms[0].value *= -1
            self.left.terms.append(self.right)
        else:  # if right is a sum
            while len(self.right.terms) > 0:
                term = self.right.terms[0]
                if term.op == 'x':
                    term.terms[0].value *= -1
                    self.right.terms.pop(0)
                    self.left.terms.append(term)
                else:  # if a non-monomial unit appears in right
                    raise ValueError

        self.right = mono(0, 0)
        self.left.simplify()

        # Create final equation graph
        graphs.append(merge_graphs(self.left.get_graph(), self.right.get_graph(), '='))

        # Look at the degree of left
        coeff_by_deg = {}
        if self.left.op == 'x':  # if left is a monomial
            coeff_by_deg[self.left.terms[1].value] = self.left.terms[0].value
        else:  # if left is a sum
            for term in self.left.terms:
                if term.op == 'x':
                    if term.terms[1].value in coeff_by_deg:
                        coeff_by_deg[term.terms[1].value] += term.terms[0].value
                    else:
                        coeff_by_deg[term.terms[1].value] = term.terms[0].value
                else:  # if a non-monomial unit appears in left
                    raise ValueError

        # Handle unsupported equations
        if any(deg not in {0, 1, 2} for deg in coeff_by_deg):
            sols = {float('nan')}

        # Solve quadratic equations
        elif 2 in coeff_by_deg:
            a = coeff_by_deg[2]
            b = coeff_by_deg.get(1, 0)
            c = coeff_by_deg.get(0, 0)

            discr_sq = b ** 2 - 4 * a * c

            if discr_sq < 0:
                sols = set()
            else:
                root_1 = (-b + math.sqrt(discr_sq)) / (2 * a)
                root_2 = (-b - math.sqrt(discr_sq)) / (2 * a)
                sols = {round(root_1, n), round(root_2, n)}

        # Solve linear equations
        elif 1 in coeff_by_deg:
            a = coeff_by_deg[1]
            b = coeff_by_deg.get(0, 0)

            sols = {round((-b / a), n)}

        # Solve constant equations
        elif 0 in coeff_by_deg:
            a = coeff_by_deg[0]

            if a == 0:
                sols = {float('inf')}
            else:
                sols = set()

        else:  # if left is the empty unit
            sols = {float('inf')}

        return ({s + 0 for s in sols}, graphs)  # + 0 avoids the float -0


def merge_graphs(g1: tuple, g2: tuple, root: str) -> tuple:
    """
    Creates a new graph (satisfying the conditions under Unit.get_graph) whose edges
    and labels are disjoint unions of the edges and labels, respectively, of g1 and g2.

    Preconditions:
        - g1 and g2 are graphs as in Unit.get_graph.
    """
    edges = []
    labels = {0: root}

    # Offset the vertices of g1 by 1 for the new root
    for e in g1[0]:
        if e[0] != e[1]:  # ignore circular edges
            edges.append((e[0] + 1, e[1] + 1))
    for l in g1[1]:
        labels[l + 1] = g1[1][l]

    # Offset the vertices of g2 by the size of g1, plus 1 for the new root
    offset = len(g1[1]) + 1
    for e in g2[0]:
        if e[0] != e[1]:  # ignore circular edges
            edges.append((e[0] + offset, e[1] + offset))
    for l in g2[1]:
        labels[l + offset] = g2[1][l]

    # Connect roots of g1 and g2 to the new root
    edges.append((0, 1))
    edges.append((0, offset))

    return (edges, labels)


if __name__ == '__main__':
    import doctest
    doctest.testmod(verbose=True)

    import python_ta
    python_ta.check_all(config={
        'max-line-length': 120,
        'disable': ['E1136', 'E1101', 'W0401', 'R0912', 'R0915', 'C9103'],
        'extra-imports': ['expr', 'math'],
        'max-nested-blocks': 4
    })
