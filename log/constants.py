"""Constants scraped from sample_1_mathpix.mmd.

Names match symbols in the companion equations module (e.g. ``lamda``,
``sigma_U``). Tool-specific values are grouped under ``_TOOL``, material
property-table values under ``_MATERIAL``, and every name also exists as
a SymPy symbol in ``SYMBOLS`` for substitution into symbolic equations.
"""

from __future__ import annotations

from typing import Dict, List, Optional

import sympy as sp

# Shared blank / lubricant / model parameters (independent of tool material).
_SHARED = {
}

# Tool thermal conductivity and roughness by material.
_TOOL = {
}

# Thermophysical properties of each material, as printed by the paper.
_MATERIAL = {
}

DEFAULT_TOOL = None
DEFAULT_DELTA = 1.5e-05  # m — lubricant film thickness (user-supplied)

# Equation inputs the paper does not tabulate (pressure, time, …).
# Pass these when calling the generated eq_* functions.
OPERATING_INPUTS = ("P", "delta", "h_a", "p")

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


def get_constants(tool: Optional[str] = DEFAULT_TOOL, delta: float = DEFAULT_DELTA) -> Dict[str, float]:
    """Return a flat constant dict, per tool material where the paper gives one."""
    if not _TOOL:
        # This paper states no tool-specific values, so there is nothing to select.
        return {**_SHARED, "delta": float(delta)}
    if tool not in _TOOL:
        raise ValueError(
            f"Unknown tool {tool!r}. Choose from: {', '.join(available_tools())}"
        )
    consts = {**_SHARED, **_TOOL[tool], "delta": float(delta)}
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


def subs_map(tool: Optional[str] = DEFAULT_TOOL, delta: float = DEFAULT_DELTA) -> Dict[sp.Symbol, float]:
    """``{Symbol: value}`` substitution map for SymPy expressions."""
    return {SYMBOLS[name]: float(value) for name, value in get_constants(tool, delta).items()}


def as_dict() -> Dict[str, float]:
    """All shared constants plus every tool-qualified name (``k_t_H13``, …)."""
    out = {k: float(v) for k, v in _SHARED.items()}
    for tool, vals in _TOOL.items():
        for name, value in vals.items():
            out[f"{name}_{tool}"] = float(value)
    return out
