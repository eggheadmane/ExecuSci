# All libraries go here
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from sympy import Symbol, Eq, solve


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


# Si (unit=Unknown)
Si = 0.09
# Fe (unit=Unknown)
Fe = 0.13
# Cu (unit=Unknown)
Cu = 1.4
# Mn (unit=Unknown)
Mn = 0.05
# Mg (unit=Unknown)
Mg = 2.6
# Cr (unit=Unknown)
Cr = 0.19
# Zn (unit=Unknown)
Zn = 5.7
# Ti (unit=Unknown)
Ti = 0.03
# TiZr (unit=Unknown)
TiZr = 0.04
# OthersEach (unit=Unknown)
OthersEach = 0.02
# H13 (unit=Unknown)
H13 = 210.0
# Castiron (unit=Unknown)
Castiron = 101.4
# P20 (unit=Unknown)
P20 = 205.0
# k_s (unit=(kW/mK))
k_s = 0.14
# k_t (unit=(H13))
# k_t = 0.0244
# k_t (unit=(Cast iron))
# k_t = 0.044
# k_t (unit=(P20))
k_t = 0.0315
# k_l (unit=(Lubricant))
k_l = 0.024
# R_s (unit=(m))
R_s = 3.4e-07
# R_t (unit=(H13))
# R_t = 9.8e-07
# R_t (unit=(Cast iron))
# R_t = 8.1e-07
# R_t (unit=(P20))
R_t = 9.6e-07
# h_a (unit=(kW/m^(2)K))
h_a = 0.8
# sigma_U (unit=Unknown)
sigma_U = 21.0
# alpha (unit=(−))
alpha = 0.000201
# lambda_ (unit=(−))
lambda_ = 6.05
# beta (unit=(−))
beta = 0.00011
# gamma (unit=(m^(−1)))
gamma = 200000.0

h = Symbol("h")
h = Symbol("h")
h = Symbol("h")
h = Symbol("h")
h = Symbol("h")
h = Symbol("h")
h_c = Symbol("h_c")
K_st = Symbol("K_st")
R = Symbol("R")
N_P = Symbol("N_P")
h_l = Symbol("h_l")
K_stl = Symbol("K_stl")
N_L = Symbol("N_L")

delta = 1.5e-5

# P_list = np.concatenate(([0.0, 5.0], np.linspace(10.0, 100.0, num=10), np.linspace(120.0, 180.0, num=3), [200.0, 250.0]))
# P_list = np.arange(0, 20.5, 0.5)
# h_list = []

colomn_name = ['P', 'h']
# df = pd.read_csv('figures\\cast_iron.csv', header=None, names=colomn_name)
df = pd.read_csv('figures\\p20.csv', header=None, names=colomn_name)
P_list = pd.to_numeric(df['P']).tolist()
h_list_paper = pd.to_numeric(df['h']).tolist()
h_list = []

for P in P_list:
    exprs = [
        # Eq(h, h_g + h_c),
        # Eq(h, 1.45 * k * (np.tan(theta)) / sigma * (p / H) ** 0.985),
        # Eq(h, 8000 * barlambda_ * (p / (C * sigma_U) * K) ** 0.86),
        # Eq(h, A * (1 - np.exp(- B * P))),
        # Eq(h, (1 - A) / h_f * (2 * k_f * k_t * k_w) / (2 * k_t * k_w - k_w * k_f - k_f * k_t)),
        Eq(h, h_a + h_c + h_l),
        Eq(h_c, alpha * (K_st * N_P) / R),
        Eq(K_st, 2 / (k_s ** (-1) + k_t ** (-1))),
        Eq(R, np.sqrt(R_s ** 2 + R_t ** 2)),
        Eq(N_P, 1 - np.exp(- lambda_ * P / sigma_U)),
        Eq(h_l, beta * (K_stl * N_L) / R),
        Eq(K_stl, 3 / (k_s ** (-1) + k_t ** (-1) + k_l ** (-1))),
        Eq(N_L, 1 - np.exp(- gamma * delta)),
    ]

    # print(P)
    # print(solve(exprs)[0])
    sol = solve(exprs)[0]

    # for key, val in sol.items():
    #     exec("{} = {}".format(key, val))

    # print(sol)
    h_list.append(sol[h])


print(P_list)
print(h_list)
print(h_list_paper)

plot_figure(P_list, h_list, h_list_paper)
plot_error_analysis(P_list, h_list, h_list_paper)
