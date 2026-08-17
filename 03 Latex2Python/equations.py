"""Executable equations extracted from markdown equation.md."""

from numpy import (
    exp, log, sqrt, sin, cos, tan, sinh, cosh, tanh, pi,
    arcsin as asin, arccos as acos, arctan as atan, abs as Abs,
)


def eq_1(h_c, h_g):
    """h = h_c + h_g

    LaTeX: h=h_{g}+h_{c}
    """
    return h_c + h_g


def eq_2(H, k, p, sigma, theta):
    """h = 1.45*k*(p/H)**0.985*tan(theta)/sigma

    LaTeX: h=1.45 k \\frac{\\tan \\theta}{\\sigma}\\left(\\frac{p}{H}\\right)^{0.985}
    """
    return 1.45*k*(p/H)**0.985*tan(theta)/sigma


def eq_3(C, K, lamda_bar, p, sigma_U):
    """h = 8000*lamda_bar*(K*p/(C*sigma_U))**0.86

    LaTeX: h=8000 \\bar{\\lambda}\\left(\\frac{p}{C \\sigma_{U}} K\\right)^{0.86}
    """
    return 8000*lamda_bar*(K*p/(C*sigma_U))**0.86


def eq_4(A, B, P):
    """h = A*(1 - exp(-B*P))

    LaTeX: h=A(1-\\exp (-B P))
    """
    return A*(1 - exp(-B*P))


def eq_5(A, h_f, k_f, k_t, k_w):
    """h = 2*k_f*k_t*k_w*(1 - A)/(h_f*(-k_f*k_t - k_f*k_w + 2*k_t*k_w))

    LaTeX: h=\\frac{1-A}{h_{f}} \\frac{2 k_{f} k_{t} k_{w}}{2 k_{t} k_{w}-k_{w} k_{f}-k_{f} k_{t}}
    """
    return 2*k_f*k_t*k_w*(1 - A)/(h_f*(-k_f*k_t - k_f*k_w + 2*k_t*k_w))


def eq_6(h_a, h_c, h_l):
    """h = h_a + h_c + h_l

    LaTeX: h=h_{a}+h_{c}+h_{l}
    """
    return h_a + h_c + h_l


def eq_7(K_st, N_P, R, alpha):
    """h_c = K_st*N_P*alpha/R

    LaTeX: h_{c}=\\alpha \\frac{K_{s t} N_{P}}{R}
    """
    return K_st*N_P*alpha/R


def eq_8(k_s, k_t):
    """K_st = 2/(1/k_t + 1/k_s)

    LaTeX: K_{s t}=\\frac{2}{k_{s}^{-1}+k_{t}^{-1}}
    """
    return 2/(1/k_t + 1/k_s)


def eq_9(R_s, R_t):
    """R = sqrt(R_s**2 + R_t**2)

    LaTeX: R=\\sqrt{R_{s}{ }^{2}+R_{t}{ }^{2}}
    """
    return sqrt(R_s**2 + R_t**2)


def eq_10(P, lamda, sigma_U):
    """N_P = 1 - exp(-P*lamda/sigma_U)

    LaTeX: N_{P}=1-\\exp \\left(-\\lambda \\frac{P}{\\sigma_{U}}\\right)
    """
    return 1 - exp(-P*lamda/sigma_U)


def eq_11(K_stl, N_L, R, beta):
    """h_l = K_stl*N_L*beta/R

    LaTeX: h_{l}=\\beta \\frac{K_{s t l} N_{L}}{R}
    """
    return K_stl*N_L*beta/R


def eq_12(k_l, k_s, k_t):
    """K_stl = 3/(1/k_t + 1/k_s + 1/k_l)

    LaTeX: K_{s t l}=\\frac{3}{k_{s}^{-1}+k_{t}^{-1}+k_{l}^{-1}}
    """
    return 3/(1/k_t + 1/k_s + 1/k_l)


def eq_13(delta, gamma):
    """N_L = 1 - exp(-delta*gamma)

    LaTeX: N_{L}=1-\\exp (-\\gamma \\delta)
    """
    return 1 - exp(-delta*gamma)
