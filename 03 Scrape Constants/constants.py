"""Constants scraped from target_paper.md.

Names match symbols in the companion equations module (e.g. ``lamda``,
``sigma_U``). Tool-specific values are grouped under ``_TOOL``, material
property-table values under ``_MATERIAL``, and every name also exists as
a SymPy symbol in ``SYMBOLS`` for substitution into symbolic equations.
"""

from __future__ import annotations

from typing import Dict, List

import sympy as sp

# Shared blank / lubricant / model parameters (independent of tool material).
_SHARED = {
    "R_s": 3.4e-07,  # m — Table 3
    "alpha": 0.000201,  # Table 3
    "beta": 0.00011,  # Table 3
    "gamma": 200000,  # m^{-1} — Table 3
    "h_a": 0.8,  # kW/m^{2}K — Table 3
    "k_l": 0.024,  # Table 3
    "k_s": 0.14,  # kW/mK — Table 3
    "lamda": 6.05,  # Table 3
    "sigma_U": 21.0,  # Table 3
}

# Tool thermal conductivity and roughness by material.
_TOOL = {
    "CastIron": {
        "R_t": 8.1e-07,  # Table 3
        "k_t": 0.044,  # Table 3
    },
    "H13": {
        "R_t": 9.8e-07,  # Table 3
        "k_t": 0.0244,  # Table 3
    },
    "P20": {
        "R_t": 9.6e-07,  # Table 3
        "k_t": 0.0315,  # Table 3
    },
}

# Thermophysical properties of each material, as printed by the paper.
_MATERIAL = {
    "CastIron": {
        "E": 101.4,  # Young's modulus — GPa — Table 2
        "c_p": 465.0,  # Specific heat capacity — J/kgK — Table 2
        "k": 0.044,  # Thermal conductivity — kW/mK — Table 2
        "nu": 0.29,  # Poisson's ratio — Table 2
        "rho": 7150.0,  # Density — kg/m^{3} — Table 2
    },
    "H13": {
        "E": 210.0,  # Young's modulus — GPa — Table 2
        "c_p": 460.0,  # Specific heat capacity — J/kgK — Table 2
        "k": 0.0244,  # Thermal conductivity — kW/mK — Table 2
        "nu": 0.3,  # Poisson's ratio — Table 2
        "rho": 7800.0,  # Density — kg/m^{3} — Table 2
    },
    "P20": {
        "E": 205.0,  # Young's modulus — GPa — Table 2
        "c_p": 473.0,  # Specific heat capacity — J/kgK — Table 2
        "k": 0.0315,  # Thermal conductivity — kW/mK — Table 2
        "nu": 0.285,  # Poisson's ratio — Table 2
        "rho": 7850.0,  # Density — kg/m^{3} — Table 2
    },
}

# Properties the paper gives as functions of temperature T (in K).
# They are not constants, so they are kept as the paper's expressions
# rather than being turned into numbers.
TEMPERATURE_DEPENDENT = {
    "AA7075.E": "-39.082 T+82532",  # Young's modulus
    "AA7075.rho": "-6.7537 e-05 T^{2}-0.15 T+2.8608 e 03",  # Density
    "AA7075.k": "-5.145 e-08 T^{2}+1.368 e-04 T +0.085224",  # Thermal conductivity
    "AA7075.c_p": "8.721 e-07 T^{3}-1.4625 e-03 T^{2}+1.2 T+608.3",  # Specific heat capacity
    "AA7075.nu": "3.893 e-08 T^{2}+0.000013505 T +0.325165",  # Poisson's ratio
    "AA7075.alpha_t": "0.0216 T+16.499",  # Thermal expansion
}

DEFAULT_TOOL = "P20"
DEFAULT_DELTA = 1.5e-05  # m — lubricant film thickness (user-supplied)

# One SymPy symbol per scraped constant; the names are the ones the
# generated equations use, so ``expr.subs(subs_map())`` just works.
SYMBOLS: Dict[str, sp.Symbol] = {
    name: sp.Symbol(name)
    for name in sorted(
        {*_SHARED, *(n for vals in _TOOL.values() for n in vals),
         *(n for vals in _MATERIAL.values() for n in vals), "delta"}
    )
}


def available_tools() -> List[str]:
    """Tool materials the paper gives IHTC model constants for."""
    return list(_TOOL.keys())


def available_materials() -> List[str]:
    """Materials the paper gives thermophysical properties for."""
    return list(_MATERIAL.keys())


def get_constants(tool: str = DEFAULT_TOOL, delta: float = DEFAULT_DELTA) -> Dict[str, float]:
    """Return a flat constant dict for the given tool material."""
    if tool not in _TOOL:
        raise ValueError(
            f"Unknown tool {tool!r}. Choose from: {', '.join(available_tools())}"
        )
    consts = {**_SHARED, **_TOOL[tool], "delta": float(delta)}
    return consts


def material_properties(material: str) -> Dict[str, float]:
    """Thermophysical properties (``E``, ``rho``, ``k``, …) of one material."""
    if material not in _MATERIAL:
        raise ValueError(
            f"Unknown material {material!r}. Choose from: "
            f"{', '.join(available_materials())}"
        )
    return dict(_MATERIAL[material])


def symbol(name: str) -> sp.Symbol:
    """The SymPy symbol scraped for ``name`` (e.g. ``symbol("k_s")``)."""
    if name not in SYMBOLS:
        raise KeyError(f"No constant named {name!r} was scraped from the paper")
    return SYMBOLS[name]


def subs_map(tool: str = DEFAULT_TOOL, delta: float = DEFAULT_DELTA) -> Dict[sp.Symbol, float]:
    """``{Symbol: value}`` substitution map for SymPy expressions."""
    return {SYMBOLS[name]: float(value) for name, value in get_constants(tool, delta).items()}


def as_dict() -> Dict[str, float]:
    """All shared constants plus every tool-qualified name (``k_t_H13``, …)."""
    out = {k: float(v) for k, v in _SHARED.items()}
    for tool, vals in _TOOL.items():
        for name, value in vals.items():
            out[f"{name}_{tool}"] = float(value)
    return out
