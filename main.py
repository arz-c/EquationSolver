"""Tree-Based Equation Solver by Areez Chishtie: Main Module
(CSC111 Winter 2024 Project 2)

Description
===============================

Runs the main loop of the equation solver. The user inputs an equation according
to the format provided in parse.py / get_unit. If the equation is constant,
linear, or quadratic, then the solution set is printed. The user is then asked
to view a visualization of the solution process. To view the next step in the
visualization, the user must close the current window.

Copyright
===============================

This file is Copyright © 2024 Areez Chishtie. All rights reserved."""

from parse import *
from visualize import *


if __name__ == '__main__':
    string = input('Equation?\n> ')

    # =============================== EXAMPLES ===============================
    # = Comment the line above, and uncomment the lines below one at a time. =
    # = Note: You may want to skip visualization on the more complex inputs, =
    # = as they tend to be quite long.                                       =
    # ========================================================================
    # string = 'x^2 = (x + 1)'  # quadratic, sum, two roots
    # string = '((x + 2) * (x + -2)) = 0'  # quadratic, product, two roots
    # string = '(x^2 + x + 1) = 0'  # quadratic, no roots
    # string = '((x + 1) * (x + 1)) = (x^2 + 2x + 1)'  # quadratic, inf roots
    # string = '((2 * x) + x) = 9'  # linear
    # string = '7 = 7'  # const, inf roots
    # string = '0 = 1'  # const, no roots
    # string = 'x^3 = 0'  # cubic (unsupported)

    while string != '':
        try:
            eqn = get_equation(string)
        except:  # since error types can be unexpected for bad inputs,
                 # we assume get_equation satisfies its specifications
            print('Incorrect format. See parse.py / get_unit.')
        else:
            sols, graphs = eqn.solve(5)

            if len(sols) == 0:
                print('No solutions.')
            elif any(math.isnan(s) for s in sols):
                print('This equation is not supported.')
            elif any(math.isinf(s) for s in sols):
                print('Every value of x is a solution.')
            else:
                sols_str = ', '.join([normalize_fstr(str(x)) for x in sorted(list(sols))])
                print(f'x = {sols_str}')

                if input('Visualize? (Y/N)\n> ') == 'Y':
                    for graph in graphs:
                        visualize(graph)

        string = input('Equation?\n> ')
