"""Executable equations extracted from sample_paper_5.md."""

from numpy import (
    exp, log, sqrt, sin, cos, tan, sinh, cosh, tanh, pi,
    arcsin as asin, arccos as acos, arctan as atan, abs as Abs,
)


def eq_1(h_a, h_c, h_l, h_s):
    """h = h_a + h_c + h_l + h_s

    LaTeX: h=h_{a}+h_{s}+h_{l}+h_{c},

    Args:
        h_a: the air-contact IHTC
        h_c: the coating-contact IHTC
        h_l: the lubricant-contact IHTC
        h_s: the solid-contact IHTC
    """
    return h_a + h_c + h_l + h_s


def eq_2(K_st, L, N_P, R_st, alpha):
    """h_s = K_st*L*N_P*alpha/R_st

    LaTeX: h_{s}=\\alpha \\frac{K_{s t}}{R_{s t}} N_{P} L,

    Args:
        K_st: the equivalent thermal conductivity of the interface between the blank and forming tools
        L: a blank thickness dependent parameter
        N_P: a contact pressure dependent parameter
        R_st: the equivalent interfacial surface roughness
        alpha: the temperature dependent thermal diffusivity of the blank

    Returns:
        h_s: the solid-contact IHTC
    """
    return K_st*L*N_P*alpha/R_st


def eq_3(B, c_p, k_s, rho):
    """alpha = B*k_s/(c_p*rho)

    LaTeX: \\alpha=B(T) \\frac{k_{s}(T)}{\\rho(T) c_{p}(T)},

    The paper writes as functions of T: B(T), c_p(T), k_s(T), rho(T)

    Args:
        B: a temperature dependent parameter
        c_p: the thermal conductivity, density and heat capacity of the aluminium alloy at the target initial blank temperature respectively
        k_s: the thermal conductivity, density and heat capacity of the aluminium alloy at the target initial blank temperature respectively
        rho: the thermal conductivity, density and heat capacity of the aluminium alloy at the target initial blank temperature respectively

    Returns:
        alpha: the temperature dependent thermal diffusivity of the blank
    """
    return B*k_s/(c_p*rho)


def eq_4(Q_b, R, T, b_0):
    """B = b_0*exp(Q_b/(R*T))

    LaTeX: B(T)=b_{0} \\exp \\left(\\frac{Q_{b}}{R T}\\right),

    The paper writes as functions of T: B(T)

    Args:
        Q_b: model constants
        R: the molar gas constant
        T: the absolute temperature
        b_0: model constants

    Returns:
        B: a temperature dependent parameter
    """
    return b_0*exp(Q_b/(R*T))


def eq_5(P, f, lamda, sigma_U):
    """N_P = 1 - exp(-P*f*lamda/sigma_U)

    LaTeX: N_{P}=1-\\exp \\left(-\\lambda f \\frac{P}{\\sigma_{U}}\\right),

    Args:
        P: the applied pressure
        f: a tempering correction factor
        lamda: a model constant
        sigma_U: the temperature dependent ultimate strength of the blank

    Returns:
        N_P: a contact pressure dependent parameter
    """
    return 1 - exp(-P*f*lamda/sigma_U)


def eq_6(Q_sigma, R, T, sigma_0):
    """sigma_U = sigma_0*exp(Q_sigma/(R*T))

    LaTeX: \\sigma_{U}=\\sigma_{0} \\exp \\left(\\frac{Q_{\\sigma}}{R T}\\right),

    Args:
        Q_sigma: model constants, identified by the high-temperature uniaxial tensile tests
        R: the molar gas constant
        T: the absolute temperature
        sigma_0: model constants, identified by the high-temperature uniaxial tensile tests

    Returns:
        sigma_U: the temperature dependent ultimate strength of the blank
    """
    return sigma_0*exp(Q_sigma/(R*T))


def eq_7(x):
    """f = x/6

    LaTeX: f=\\frac{\\sigma_{U}(T x)}{\\sigma_{U}(T 6)},

    Returns:
        f: a tempering correction factor
    """
    return x/6


def eq_8(k_s, k_t):
    """K_st = 2/(1/k_t + 1/k_s)

    LaTeX: K_{s t}=\\frac{2}{k_{s}^{-1}+k_{t}^{-1}},

    Args:
        k_s: the thermal conductivity, density and heat capacity of the aluminium alloy at the target initial blank temperature respectively
        k_t: the thermal conductivities of the aluminium blank (specimen) and forming tools at their initial (forming) temperatures

    Returns:
        K_st: the equivalent thermal conductivity of the interface between the blank and forming tools
    """
    return 2/(1/k_t + 1/k_s)


def eq_9(R_s, R_t, theta):
    """R_st = sqrt(R_s**2 + R_t**2)*sin(theta)

    LaTeX: R_{s t}=\\sin \\theta \\sqrt{R_{s}^{2}+R_{t}^{2}},

    Args:
        R_s: the average (mean) surface roughness of the aluminium blank (specimen) and forming tools respectively before compression, generally describing the height variations in the contact surfaces
        R_t: the average (mean) surface roughness of the aluminium blank (specimen) and forming tools respectively before compression, generally describing the height variations in the contact surfaces
        theta: the initial deformation angle of the blank contact profile, and thus \\sin \\theta describes the mean modulus of the slope of the blank contact profile [34,45]

    Returns:
        R_st: the equivalent interfacial surface roughness
    """
    return sqrt(R_s**2 + R_t**2)*sin(theta)


def eq_10(l, m, n):
    """L = m*log(l) + n

    LaTeX: L=m \\ln (l)+n,

    Args:
        l: the blank thickness
        m: model constants
        n: model constants

    Returns:
        L: a blank thickness dependent parameter
    """
    return m*log(l) + n


def eq_11(K_slt, N_delta, R_st, omega):
    """h_l = K_slt*N_delta*omega/R_st

    LaTeX: h_{l}=\\omega \\frac{K_{s l t}}{R_{s t}} N_{\\delta},

    Args:
        K_slt: the equivalent mean thermal conductivity of the interface between the blank, forming tools and lubricant
        N_delta: a lubricant thickness dependent parameter
        R_st: the equivalent interfacial surface roughness
        omega: a model constant

    Returns:
        h_l: the lubricant-contact IHTC
    """
    return K_slt*N_delta*omega/R_st


def eq_12(k_l, k_s, k_t):
    """K_slt = 3/(1/k_t + 1/k_s + 1/k_l)

    LaTeX: K_{s l t}=\\frac{3}{k_{s}^{-1}+k_{l}^{-1}+k_{t}^{-1}},

    Args:
        k_l: the thermal conductivity of the lubricant
        k_s: the thermal conductivity, density and heat capacity of the aluminium alloy at the target initial blank temperature respectively
        k_t: the thermal conductivities of the aluminium blank (specimen) and forming tools at their initial (forming) temperatures

    Returns:
        K_slt: the equivalent mean thermal conductivity of the interface between the blank, forming tools and lubricant
    """
    return 3/(1/k_t + 1/k_s + 1/k_l)


def eq_13(delta_l, gamma):
    """N_delta = 1 - exp(-delta_l*gamma)

    LaTeX: N_{\\delta}=1-\\exp \\left(-\\gamma \\delta_{l}\\right),

    Args:
        delta_l: the lubricant layer thickness
        gamma: a model parameter

    Returns:
        N_delta: a lubricant thickness dependent parameter
    """
    return 1 - exp(-delta_l*gamma)


def eq_14(A, N_P, beta, delta_c, k_c, k_l, k_s, theta):
    """h_c = N_P*beta*delta_c*k_s*log(k_c/k_l)*tan(theta)/A

    LaTeX: h_{c}=\\beta \\frac{k_{s}}{A} \\tan \\theta \\cdot \\ln \\left(k_{c} / k_{l}\\right) \\delta_{c} \\cdot N_{P},

    Args:
        A: the apparent contact area between the blank and forming tools
        N_P: a contact pressure dependent parameter
        beta: a model parameter
        delta_c: the layer thickness of the tool coating
        k_c: the thermal conductivity of the tool coating
        k_l: the thermal conductivity of the lubricant
        k_s: the thermal conductivity, density and heat capacity of the aluminium alloy at the target initial blank temperature respectively
        theta: the initial deformation angle of the blank contact profile, and thus \\sin \\theta describes the mean modulus of the slope of the blank contact profile [34,45]

    Returns:
        h_c: the coating-contact IHTC
    """
    return N_P*beta*delta_c*k_s*log(k_c/k_l)*tan(theta)/A
