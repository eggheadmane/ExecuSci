"""Executable equations extracted from target_paper.md."""

from numpy import (
    exp, log, sqrt, sin, cos, tan, sinh, cosh, tanh, pi,
    arcsin as asin, arccos as acos, arctan as atan, abs as Abs,
)


def eq_1(h_c, h_g):
    """h = h_c + h_g

    LaTeX: h=h_{g}+h_{c}

    Args:
        h_c: the heat transfer coefficients across the air gap and for the solid contact respectively
        h_g: the heat transfer coefficients across the air gap and for the solid contact respectively
    """
    return h_c + h_g


def eq_2(H, k, p, sigma, theta):
    """h = 1.45*k*(p/H)**0.985*tan(theta)/sigma

    LaTeX: h=1.45 k \\frac{\\tan \\theta}{\\sigma}\\left(\\frac{p}{H}\\right)^{0.985}

    Args:
        H
        k: the mean thermal conductivity of two contact bodies
        p
        sigma: the standard deviation of the profile heights
        theta: the mean of the absolute slope of the surface profile
    """
    return 1.45*k*(p/H)**0.985*tan(theta)/sigma


def eq_3(C, K, lamda_bar, p, sigma_U):
    """h = 8000*lamda_bar*(K*p/(C*sigma_U))**0.86

    LaTeX: h=8000 \\bar{\\lambda}\\left(\\frac{p}{C \\sigma_{U}} K\\right)^{0.86}

    Args:
        C: model coefficients
        K: model coefficients
        lamda_bar: the mean thermal conductivity of the two contact bodies
        p
        sigma_U: the ultimate strength of the test specimens
    """
    return 8000*lamda_bar*(K*p/(C*sigma_U))**0.86


def eq_4(A, B, P):
    """h = A*(1 - exp(-B*P))

    LaTeX: h=A(1-\\exp (-B P))

    Args:
        A: model constants determined by the least square method using the experimental results
        B: model constants determined by the least square method using the experimental results
        P: the contact pressure between the specimen and tools
    """
    return A*(1 - exp(-B*P))


def eq_5(A, h_f, k_f, k_t, k_w):
    """h = 2*k_f*k_t*k_w*(1 - A)/(h_f*(-k_f*k_t - k_f*k_w + 2*k_t*k_w))

    LaTeX: h=\\frac{1-A}{h_{f}} \\frac{2 k_{f} k_{t} k_{w}}{2 k_{t} k_{w}-k_{w} k_{f}-k_{f} k_{t}}

    Args:
        A: model constants determined by the least square method using the experimental results
        h_f: the applied lubricant thickness
        k_f: the thermal conductivities of the lubricant, tool and workpiece, respectively
        k_t: the thermal conductivities of the lubricant, tool and workpiece, respectively
        k_w: the thermal conductivities of the lubricant, tool and workpiece, respectively
    """
    return 2*k_f*k_t*k_w*(1 - A)/(h_f*(-k_f*k_t - k_f*k_w + 2*k_t*k_w))


def eq_6(h_a, h_c, h_l):
    """h = h_a + h_c + h_l

    LaTeX: h=h_{a}+h_{c}+h_{l}

    Args:
        h_a: the heat transfer across the air gap between the specimen and tools with zero pressure, and typically has a low value
        h_c: the heat transfer coefficients across the air gap and for the solid contact respectively
        h_l: the application of lubricant between two solid surfaces
    """
    return h_a + h_c + h_l


def eq_7(K_st, N_P, R, alpha):
    """h_c = K_st*N_P*alpha/R

    LaTeX: h_{c}=\\alpha \\frac{K_{s t} N_{P}}{R}

    Args:
        K_st: the harmonic mean thermal conductivity of the contact solids
        N_P: a pressure dependent parameter
        R: the root mean square of surface roughness of the contact solids
        alpha: a model parameter

    Returns:
        h_c: the heat transfer coefficients across the air gap and for the solid contact respectively
    """
    return K_st*N_P*alpha/R


def eq_8(k_s, k_t):
    """K_st = 2/(1/k_t + 1/k_s)

    LaTeX: K_{s t}=\\frac{2}{k_{s}^{-1}+k_{t}^{-1}}

    Args:
        k_s: the average thermal conductivities of the specimen, tools and grease-based graphite lubricant respectively
        k_t: the thermal conductivities of the lubricant, tool and workpiece, respectively

    Returns:
        K_st: the harmonic mean thermal conductivity of the contact solids
    """
    return 2/(1/k_t + 1/k_s)


def eq_9(R_s, R_t):
    """R = sqrt(R_s**2 + R_t**2)

    LaTeX: R=\\sqrt{R_{s}^{2}+R_{t}^{2}}

    Args:
        R_s: the average surface roughness of the specimen
        R_t

    Returns:
        R: the root mean square of surface roughness of the contact solids
    """
    return sqrt(R_s**2 + R_t**2)


def eq_10(P, lamda, sigma_U):
    """N_P = 1 - exp(-P*lamda/sigma_U)

    LaTeX: N_{P}=1-\\exp \\left(-\\lambda \\frac{P}{\\sigma_{U}}\\right)

    Args:
        P: the contact pressure between the specimen and tools
        lamda: a model parameter
        sigma_U: the ultimate strength of the test specimens

    Returns:
        N_P: a pressure dependent parameter
    """
    return 1 - exp(-P*lamda/sigma_U)


def eq_11(K_stl, N_L, R, beta):
    """h_l = K_stl*N_L*beta/R

    LaTeX: h_{l}=\\beta \\frac{K_{s t l} N_{L}}{R}

    Args:
        K_stl: the harmonic mean thermal conductivity of the three contacting materials, i.e. the tools, lubricant and specimen
        N_L: a layer thickness dependent parameter
        R: the root mean square of surface roughness of the contact solids
        beta: a model parameter

    Returns:
        h_l: the application of lubricant between two solid surfaces
    """
    return K_stl*N_L*beta/R


def eq_12(k_l, k_s, k_t):
    """K_stl = 3/(1/k_t + 1/k_s + 1/k_l)

    LaTeX: K_{s t l}=\\frac{3}{k_{s}^{-1}+k_{t}^{-1}+k_{l}^{-1}}

    Args:
        k_l: the average thermal conductivities of the specimen, tools and grease-based graphite lubricant respectively
        k_s: the average thermal conductivities of the specimen, tools and grease-based graphite lubricant respectively
        k_t: the thermal conductivities of the lubricant, tool and workpiece, respectively

    Returns:
        K_stl: the harmonic mean thermal conductivity of the three contacting materials, i.e. the tools, lubricant and specimen
    """
    return 3/(1/k_t + 1/k_s + 1/k_l)


def eq_13(delta, gamma):
    """N_L = 1 - exp(-delta*gamma)

    LaTeX: N_{L}=1-\\exp (-\\gamma \\delta)

    Args:
        delta: the applied lubricant layer thickness
        gamma: a model parameter

    Returns:
        N_L: a layer thickness dependent parameter
    """
    return 1 - exp(-delta*gamma)
