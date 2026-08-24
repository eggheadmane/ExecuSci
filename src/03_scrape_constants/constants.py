"""Constants scraped from sample_paper_5.md.

Names match symbols in the companion equations module (e.g. ``lamda``,
``sigma_U``). Tool-specific values are grouped under ``_TOOL``, material
property-table values under ``_MATERIAL``, and every name also exists as
a SymPy symbol in ``SYMBOLS`` for substitution into symbolic equations.
"""

from __future__ import annotations

import math
from typing import Dict, List, Optional

import sympy as sp

# Shared blank / lubricant / model parameters (independent of tool material).
_SHARED = {
    "A": 0.0005,  # m^{2} — Table 1
    "Q_b": -1730.0,  # J/mol — Table 1
    "R": 8.314,  # J/molK — Table 1
    "b_0": 1.69,  # s/m^{2} — Table 1
    "beta": 8300.0,  # Table 1
    "gamma": 150000,  # m^{-1} — Table 1
    "lamda": 5.0,  # Table 1
    "m": 0.64,  # Table 1
    "n": 0.56,  # Table 1
    "omega": 4.2e-05,  # Table 1
}

# Tool thermal conductivity and roughness by material.
_TOOL = {
}

# Thermophysical properties of each material, as printed by the paper.
_MATERIAL = {
    "AA6082": {
        "E": 70.0,  # Young's modulus — GPa — Table 3
        "R_a": 430.0,  # Surface roughness — nm — Table 2
        "R_s": 4.3e-07,  # Surface roughness — nm — Table 2
        "c_p": 890.0,  # Specific heat capacity — J/kgK — Table 3
        "k": 170.0,  # Thermal conductivity — W/mK — Table 3
        "k_s": 0.17,  # Thermal conductivity — W/mK — Table 3
        "rho": 2700.0,  # Density $\left(\mathrm{kg} / \mathrm{m}^{3}\right)$ — Table 3
    },
    "AA7075": {
        "E": 140.0,  # Young's modulus — GPa — Table 3
        "R_a": 340.0,  # Surface roughness — nm — Table 2
        "R_s": 3.4e-07,  # Surface roughness — nm — Table 2
        "c_p": 1060.0,  # Specific heat capacity — J/kgK — Table 3
        "k": 140.0,  # Thermal conductivity — W/mK — Table 3
        "k_s": 0.14,  # Thermal conductivity — W/mK — Table 3
        "rho": 2707.0,  # Density $\left(\mathrm{kg} / \mathrm{m}^{3}\right)$ — Table 3
    },
    "CrN": {
        "delta_c": 6e-06,  # Thickness — mum — Table 2
        "k": 12.0,  # Thermal conductivity — kW/mK — Table 2
        "k_c": 12.0,  # Thermal conductivity — kW/mK — Table 2
        "thickness": 6.0,  # Thickness — mum — Table 2
    },
    "D6510": {
        "R_a": 180.0,  # Surface roughness — nm — Table 2
        "R_t": 1.8e-07,  # Surface roughness — nm — Table 2
        "k": 35.2,  # Thermal conductivity — W/mK — Table 2
        "k_t": 0.0352,  # Thermal conductivity — W/mK — Table 2
    },
    "G3500": {
        "R_a": 810.0,  # Surface roughness — nm — Table 2
        "R_t": 8.1e-07,  # Surface roughness — nm — Table 2
        "k": 44.0,  # Thermal conductivity — W/mK — Table 2
        "k_t": 0.044,  # Thermal conductivity — W/mK — Table 2
    },
    "Graphite": {
        "k": 24.0,  # Thermal conductivity — kW/mK — Table 2
        "k_l": 24.0,  # Thermal conductivity — kW/mK — Table 2
    },
    "H13": {
        "R_a": 980.0,  # Surface roughness — nm — Table 2
        "R_t": 9.8e-07,  # Surface roughness — nm — Table 2
        "k": 24.4,  # Thermal conductivity — W/mK — Table 2
        "k_t": 0.0244,  # Thermal conductivity — W/mK — Table 2
    },
    "P20": {
        "E": 205.0,  # Young's modulus — GPa — Table 3
        "R_a": 960.0,  # Surface roughness — nm — Table 2
        "R_t": 9.6e-07,  # Surface roughness — nm — Table 2
        "c_p": 473.0,  # Specific heat capacity — J/kgK — Table 3
        "k": 31.5,  # Thermal conductivity — W/mK — Table 3
        "k_t": 0.0315,  # Thermal conductivity — W/mK — Table 3
        "rho": 7850.0,  # Density $\left(\mathrm{kg} / \mathrm{m}^{3}\right)$ — Table 3
    },
    "TiN": {
        "delta_c": 8e-06,  # Thickness — mum — Table 2
        "k": 19.0,  # Thermal conductivity — kW/mK — Table 2
        "k_c": 19.0,  # Thermal conductivity — kW/mK — Table 2
        "thickness": 8.0,  # Thickness — mum — Table 2
    },
    "WC-Co": {
        "delta_c": 2e-06,  # Thickness — mum — Table 2
        "k": 29.2,  # Thermal conductivity — kW/mK — Table 2
        "k_c": 29.2,  # Thermal conductivity — kW/mK — Table 2
        "thickness": 2.0,  # Thickness — mum — Table 2
    },
}

DEFAULT_TOOL = "P20"
DEFAULT_MATERIAL = "AA6082"
DEFAULT_DELTA = 1.5e-05  # m — lubricant film thickness (user-supplied)

# Equation inputs the paper does not tabulate (pressure, time, …).
# Pass these when calling the generated eq_* functions.
OPERATING_INPUTS = ("P", "T")

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
    """Tool materials the paper gives IHTC model constants or properties for."""
    names = list(_TOOL.keys())
    for material in _MATERIAL:
        if material in {"H13", "P20", "CastIron", "G3500", "D6510"} and material not in names:
            names.append(material)
    return names


def available_materials() -> List[str]:
    """Materials the paper gives thermophysical properties for."""
    return list(_MATERIAL.keys())


def get_constants(
    tool: Optional[str] = DEFAULT_TOOL,
    delta: float = DEFAULT_DELTA,
    material: Optional[str] = DEFAULT_MATERIAL,
    coating: Optional[str] = None,
) -> Dict[str, float]:
    """Return a flat constant dict, per tool / blank where the paper gives one."""
    known = set(available_tools())
    consts: Dict[str, float] = {**_SHARED, "delta": float(delta), "delta_l": float(delta)}
    if tool:
        if tool in _TOOL:
            consts.update(_TOOL[tool])
        elif known and tool not in known and tool not in _MATERIAL:
            raise ValueError(
                f"Unknown tool {tool!r}. Choose from: {', '.join(known)}"
            )
        if tool in _MATERIAL:
            consts.update(_MATERIAL[tool])
    if material and material in _MATERIAL:
        consts.update(_MATERIAL[material])
    if coating and coating in _MATERIAL:
        consts.update(_MATERIAL[coating])
    if "Graphite" in _MATERIAL:
        consts.update(_MATERIAL["Graphite"])
    if "theta" not in consts and consts.get("R_s") is not None and consts.get("R_t") is not None:
        consts["theta"] = math.radians(20.0 if consts["R_s"] < consts["R_t"] else 70.0)
    if "h_a" not in consts:
        consts["h_a"] = 0.0
    return consts


def material_properties(material: str) -> Dict[str, float]:
    """Thermophysical properties (``E``, ``rho``, ``k``, …) of one material."""
    if not _MATERIAL:
        raise ValueError("This paper states no material property table")
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


def subs_map(
    tool: Optional[str] = DEFAULT_TOOL,
    delta: float = DEFAULT_DELTA,
    material: Optional[str] = DEFAULT_MATERIAL,
) -> Dict[sp.Symbol, float]:
    """``{Symbol: value}`` substitution map for SymPy expressions."""
    values = get_constants(tool=tool, delta=delta, material=material)
    return {SYMBOLS[name]: float(value) for name, value in values.items() if name in SYMBOLS}


def as_dict() -> Dict[str, float]:
    """All shared constants plus every tool-qualified name (``k_t_H13``, …)."""
    out = {k: float(v) for k, v in _SHARED.items()}
    for tool, vals in _TOOL.items():
        for name, value in vals.items():
            out[f"{name}_{tool}"] = float(value)
    return out
