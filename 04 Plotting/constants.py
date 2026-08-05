"""Paper constants for the IHTC model (Hu et al., J. Mater. Process. Technol.).

Names match the translated symbols in ``equations.py`` (e.g. ``lamda``, ``sigma_U``).
Tool-specific values (``k_t``, ``R_t``) come from Table 3 in the paper.
"""

from __future__ import annotations

from typing import Dict

# Shared blank / lubricant / model parameters (independent of tool material).
_SHARED = {
    "k_s": 0.14,          # kW/mK — blank (AA7075)
    "k_l": 0.024,         # kW/mK — lubricant
    "R_s": 3.4e-07,       # m — blank roughness
    "h_a": 0.8,           # kW/m²K — air gap contribution
    "sigma_U": 21.0,      # MPa — ultimate strength
    "alpha": 0.000201,    # — solid-contact coefficient
    "lamda": 6.05,        # — pressure-sensitivity coefficient
    "beta": 0.00011,      # — lubricant-contact coefficient
    "gamma": 200000.0,    # m⁻¹ — lubricant film coefficient
}

# Tool thermal conductivity and roughness by material.
_TOOL = {
    "P20": {"k_t": 0.0315, "R_t": 9.6e-07},
    "H13": {"k_t": 0.0244, "R_t": 9.8e-07},
    "CastIron": {"k_t": 0.044, "R_t": 8.1e-07},
}

DEFAULT_TOOL = "P20"
DEFAULT_DELTA = 1.5e-5  # m — lubricant film thickness (user-set in FYP)


def available_tools() -> list[str]:
    return list(_TOOL.keys())


def get_constants(tool: str = DEFAULT_TOOL, delta: float = DEFAULT_DELTA) -> Dict[str, float]:
    """Return a flat constant dict for the given tool material."""
    if tool not in _TOOL:
        raise ValueError(
            f"Unknown tool {tool!r}. Choose from: {', '.join(available_tools())}"
        )
    consts = {**_SHARED, **_TOOL[tool], "delta": float(delta)}
    return consts
