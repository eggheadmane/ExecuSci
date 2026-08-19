# All libraries go here
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from sympy import Symbol, Eq, solve
from tqdm import tqdm


def compute_percent_error(Y, Y_true):
    Y, Y_true = np.asarray(Y, dtype=np.float32), np.asarray(Y_true, dtype=np.float32)
    return np.around(np.abs(Y - Y_true) / Y_true, 5)


def plot_figure(X, Y, Y_true):
    plt.plot(X, Y, label='h from autonomous framework')
    plt.plot(X, Y_true, label='h from paper')
    plt.legend()
    # plt.scatter(X, Y, marker='x')
    plt.xlabel('Contact Pressure (MPa)')
    plt.ylabel('IHTC (kW/m²K)')
    # plt.title('The IHTC Evolutions with Contact Pressure (Cast Iron)')
    plt.title('The IHTC Evolutions with Contact Pressure (P20)')
    plt.show()


def plot_error_analysis(X, Y, Y_true):
    percent_error = compute_percent_error(Y, Y_true) * 100
    plt.plot(X, percent_error)
    plt.xlabel('Contact Pressure (MPa)')
    plt.ylabel('Percentage Error (%)')
    # plt.title('Error Analysis (Cast Iron)')
    plt.title('Error Analysis (P20)')
    plt.show()


# All equation parameters go here
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
# delta = 1.5e-5

colomn_name = ['P', 'h']
# df = pd.read_csv('figures\\cast_iron.csv', header=None, names=colomn_name)
df = pd.read_csv('figures\\p20.csv', header=None, names=colomn_name)
P_list = pd.to_numeric(df['P']).tolist()
h_list_paper = pd.to_numeric(df['h']).tolist()
h_list = []

for P in tqdm(P_list, desc='Generating Curve'):
    # All equations go here
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

    # print(P)
    # print(solve(exprs)[0])
    sol = solve(exprs)[0]

    # for key, val in sol.items():
    #     exec("{} = {}".format(key, val))

    # print(sol)
    h_list.append(round(sol[h], 5))


print('X: {}'.format(P_list))
print('Y: {}'.format(h_list))
print('Y_true: {}'.format(h_list_paper))

plot_figure(P_list, h_list, h_list_paper)
plot_error_analysis(P_list, h_list, h_list_paper)