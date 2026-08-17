"""Executable equations extracted from test_eq.md."""

from numpy import (
    exp, log, sqrt, sin, cos, tan, sinh, cosh, tanh, pi,
    arcsin as asin, arccos as acos, arctan as atan, abs as Abs,
)


def sigma_f(C, epsilon, epsilon_0, n):
    """sigma_f = C*(epsilon + epsilon_0)**n

    LaTeX: \\sigma_f = C \\left( \\varepsilon_0 + \\varepsilon \\right)^n
    """
    return C*(epsilon + epsilon_0)**n
