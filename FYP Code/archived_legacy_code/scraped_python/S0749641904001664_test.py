import numpy as np
from sympy import Symbol, Eq, solve

# A (unit=(−))
A = 2.883
# B (unit=(MPa))
B = 55.504
# C (unit=(−))
C = 39.966
# D (unit=(s^(−1) ))
D = 0.151
# K (unit=(MPa))
K = 43.247
# r (unit=(MPa s^(−1)))
r = 98.253
# n_1 (unit=(−))
n_1 = 6.229
# n_2 (unit=(−))
n_2 = 7.592
# n_3 (unit=(−))
n_3 = 0.195
# n_4 (unit=(−))
n_4 = 1.671
# sigma_0 (unit=(MPa))
sigma_0 = 45.605

dotepsilon = Symbol("dotepsilon")
D = Symbol("D")
dotS = Symbol("dotS")
dotS = Symbol("dotS")
dotP = Symbol("dotP")
dotsigma_y = Symbol("dotsigma_y")
dotepsilon_p = Symbol("dotepsilon_p")
dotS = Symbol("dotS")
dotsigma_y = Symbol("dotsigma_y")
dotR = Symbol("dotR")
dotrho = Symbol("dotrho")
sigma = Symbol("sigma")
fx = Symbol("fx")
omega1_ij = Symbol("omega1_ij")
omega2_ij = Symbol("omega2_ij")
dotepsilon = Symbol("dotepsilon")

exprs = [
    Eq(dotepsilon, 0.1),
    Eq(D, D_0 * np.exp(- Q / (R_GC * T_SHT))),
    Eq(dotS, f * (D , S)),
    Eq(dotS, D * (1 - S) ** n_3),
    Eq(dotP, (r * y) * ((L - y) / L)),
    Eq(dotsigma_y, - rS * (1 - S) ** n_4),
    Eq(dotepsilon_p, ((sigma - R - sigma_y) / K) ** n_1),
    Eq(dotS, D * (1 - S) ** n_3),
    Eq(dotsigma_y, - rS * (1 - S) ** n_4),
    Eq(dotR, 1 / 2 * B * rho ** (-1 / (2)) * dotrho),
    Eq(dotrho, A * (1 - rho) * abs(dotepsilon_p) - C * rho ** n_2),
    Eq(sigma, E * (epsilon_T - epsilon_p)),
    Eq(fx, sum_(j=1) ** M sum_(i=1) ** N_j * {omega * 1_ij * ((sigma_ij ** e - sigma_ij ** c) / (alpha * sigma_(N_j * j) ** e)) ** 2 + omega * 2_ij * ((epsilon_ij ** e - epsilon_ij ** c) / (alpha * epsilon_(N_j * j) ** e)) ** 2}),
    Eq(omega1_ij, sigma_ij ** e *  / ( sum_(j=1) ** M sum_(i=1) ** N_j * (sigma_ij ** e))),
    Eq(omega2_ij, epsilon_ij ** e *  / ( sum_(j=1) ** M sum_(i=1) ** N_j * (epsilon_ij ** e))),
    Eq(dotepsilon, 0.01 , 0.1 , 1.0),
]

sol = solve(exprs)[0]

for key, val in sol.items():
    exec("{} = {}".format(key, val))
