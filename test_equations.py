"""Executable equations extracted from test_eq.md."""

from numpy import (
    exp, log, sqrt, sin, cos, tan, sinh, cosh, tanh, pi,
    arcsin as asin, arccos as acos, arctan as atan, abs as Abs,
)


def sigma_y(sigma_1, sigma_2, sigma_3):
    """sigma_y = sqrt((-sigma_1 + sigma_3)**2/2 + (sigma_1 - sigma_2)**2/2 + (sigma_2 - sigma_3)**2/2)

    LaTeX: \\sigma_y = \\sqrt{\\frac{1}{2}\\left[(\\sigma_1 - \\sigma_2)^2 + (\\sigma_2 - \\sigma_3)^2 + (\\sigma_3 - \\sigma_1)^2\\right]}
    """
    return sqrt((-sigma_1 + sigma_3)**2/2 + (sigma_1 - sigma_2)**2/2 + (sigma_2 - sigma_3)**2/2)
