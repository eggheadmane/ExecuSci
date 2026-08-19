# import numpy as np
# from sympy import Symbol, Eq, solve
#
# # Si (unit=Unknown)
# Si = 0.09
# # Fe (unit=Unknown)
# Fe = 0.13
# # Cu (unit=Unknown)
# Cu = 1.4
# # Mn (unit=Unknown)
# Mn = 0.05
# # Mg (unit=Unknown)
# Mg = 2.6
# # Cr (unit=Unknown)
# Cr = 0.19
# # Zn (unit=Unknown)
# Zn = 5.7
# # Ti (unit=Unknown)
# Ti = 0.03
# # TiZr (unit=Unknown)
# TiZr = 0.04
# # OthersEach (unit=Unknown)
# OthersEach = 0.02
# # H13 (unit=Unknown)
# H13 = 210.0
# # Castiron (unit=Unknown)
# Castiron = 101.4
# # P20 (unit=Unknown)
# P20 = 205.0
# # k_s (unit=(kW/mK))
# k_s = 0.14
# # k_t (unit=(H13))
# k_t = 0.0244
# # k_t (unit=(Cast iron))
# k_t = 0.044
# # k_t (unit=(P20))
# k_t = 0.0315
# # k_l (unit=(Lubricant))
# k_l = 0.024
# # R_s (unit=(m))
# R_s = 3.4e-07
# # R_t (unit=(H13))
# R_t = 9.8e-07
# # R_t (unit=(Cast iron))
# R_t = 8.1e-07
# # R_t (unit=(P20))
# R_t = 9.6e-07
# # h_a (unit=(kW/m^(2)K))
# h_a = 0.8
# # sigma_U (unit=Unknown)
# sigma_U = 21.0
# # alpha (unit=(−))
# alpha = 0.000201
# # lambda_ (unit=(−))
# lambda_ = 6.05
# # beta (unit=(−))
# beta = 0.00011
# # gamma (unit=(m^(−1)))
# gamma = 200000.0
#
# delta =1e-7
# # P = np.concatenate(([0.0, 5.0], np.linspace(10.0, 100.0, num=10), np.linspace(120.0,180.0,num=3),[200.0,250.0]))
# P = 0
#
# h = Symbol("h")
# h = Symbol("h")
# h = Symbol("h")
# h = Symbol("h")
# h = Symbol("h")
# h = Symbol("h")
# h_c = Symbol("h_c")
# K_st = Symbol("K_st")
# R = Symbol("R")
# N_P = Symbol("N_P")
# h_l = Symbol("h_l")
# K_stl = Symbol("K_stl")
# N_L = Symbol("N_L")
#
# exprs = [
#     # Eq(h, h_g + h_c),
#     # Eq(h, 1.45 * k * (np.tan(theta)) / sigma * (p / H) ** 0.985),
#     # Eq(h, 8000 * barlambda_ * (p / (C * sigma_U) * K) ** 0.86),
#     # Eq(h, A * (1 - np.exp(- B * P))),
#     # Eq(h, (1 - A) / h_f * (2 * k_f * k_t * k_w) / (2 * k_t * k_w - k_w * k_f - k_f * k_t)),
#     Eq(h, h_a + h_c + h_l),
#     Eq(h_c, alpha * (K_st * N_P) / R),
#     Eq(K_st, 2 / (k_s ** (-1) + k_t ** (-1))),
#     Eq(R, np.sqrt(R_s ** 2 + R_t ** 2)),
#     Eq(N_P, 1 - np.exp(- lambda_ * P / sigma_U)),
#     Eq(h_l, beta * (K_stl * N_L) / R),
#     Eq(K_stl, 3 / (k_s ** (-1) + k_t ** (-1) + k_l ** (-1))),
#     Eq(N_L, 1 - np.exp(- gamma * delta)),
# ]
#
# sol = solve(exprs)[0]
# print(sol)
#
# for key, val in sol.items():
#     exec('{} = {}'.format(key, val))
#
# print(h)


# from converter import Converter
# tex = r'$ \dot{S}=D(1-S)^{{n}_{3}}\text{,}$'
#
# c = Converter()
# print(c.tex2ascii(tex))
#
# import re
# a = r'$ \begin{array}{cc}\hfill & {\dot{\epsilon }}_{\mathrm{p}}={\left(\frac{\sigma -R-{\sigma }_{y}}{K}\right)}^{{n}_{1}}\text{,}\hfill \\ \hfill & \dot{S}=D{\left(1-S\right)}^{{n}_{3}}\text{,}\hfill \\ \hfill & {\dot{\sigma }}_{y}=-\mathrm{rS}(1-S)^{{n}_{4}}\text{,}\hfill \\ \hfill & \dot{R}=\frac{1}{2}B{\rho }^{-1/2}\dot{\rho }\text{,}\hfill \\ \hfill & \dot{\rho }=A\left(1-\rho \right)\left|{\dot{\epsilon }}_{\mathrm{p}}\right|-C{\rho }^{{n}_{2}}\text{,}\hfill \\ \hfill & \sigma =E({\epsilon }_{T}-{\epsilon }_{\mathrm{p}})\text{,}\hfill \end{array}$'

# a = r'''$ \begin{array}{cc}\hfill &
# {\dot{\epsilon }}_{\mathrm{p}}={\left(\frac{\sigma -R-{\sigma }_{y}}{K}\right)}^{{n}_{1}}\text{,}\hfill \\ \hfill &
# \dot{S}=D{\left(1-S\right)}^{{n}_{3}}\text{,}\hfill \\ \hfill &
# {\dot{\sigma }}_{y}=-\mathrm{rS}(1-S)^{{n}_{4}}\text{,}\hfill \\ \hfill &
# \dot{R}=\frac{1}{2}B{\rho }^{-1/2}\dot{\rho }\text{,}\hfill \\ \hfill &
# \dot{\rho }=A\left(1-\rho \right)\left|{\dot{\epsilon }}_{\mathrm{p}}\right|-C{\rho }^{{n}_{2}}\text{,}\hfill \\ \hfill &
# \sigma =E({\epsilon }_{T}-{\epsilon }_{\mathrm{p}})\text{,}\hfill \end{array}$'''

#
# a = a.split(' & ')
# print(a)
#
#
# if r'\begin{array}' in a:
#     for expr in a[1:]:
#         i = expr.find('\hfill')
#         print(expr[:i])
#


# m, n = map(int, input().strip().split())
# s1 = input().strip()
# s2 = input().strip()

# s1 = 'abc'
# s2 = 'def'
#
# dp = [[0 for i in range(len(s2)+1)] for j in range(len(s1)+1)]
# max_len, idx = 0, []
#
# for i in range(len(s1)):
#     for j in range(len(s2)):
#         if s1[i] == s2[j]:
#             dp[i+1][j+1] = dp[i][j] + 1
#             if dp[i+1][j+1] > max_len:
#                 max_len = dp[i+1][j+1]
#                 idx = [i+1]
#             elif dp[i+1][j+1] == max_len:
#                 idx.append(i+1)
#
# if max_len < 2:
#     print('0')
# else:
#     print(min([s1[i-max_len:i] for i in idx]))
import collections

n, r = map(int, input().strip().split())
tasks = map(int, input().strip().split())
relation = []
for _ in range(r):
    relation.append(map(int, input().strip().split()))

# n, r = 2, 2
# tasks = [0, 1]
# relation = [[0, 1], [1, 0]]

graph = collections.defaultdict(list)
indegree = {}
for t in tasks:
    indegree[t] = 0
res = []

for a, b in relation:
    graph[a].append(b)
    indegree[b] += 1

while True:
    for t in tasks:
        next = -1
        if indegree[t] == 0:
            next = t
            indegree[t] -= 1
            break

    if next == -1:
        break

    for c in graph[next]:
        indegree[c] -= 1

    res.append(next)

if len(res) < n:
    print('-1')
else:
    print(' '.join(map(str, res)))
