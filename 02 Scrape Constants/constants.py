"""Constants scraped from mathpix_pdf.md.

Names match symbols in the companion equations module (e.g. ``lamda``,
``sigma_U``). Tool-specific values are grouped under ``_TOOL``.
"""

from __future__ import annotations

from typing import Dict

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

DEFAULT_TOOL = "P20"
DEFAULT_DELTA = 1.5e-05  # m — lubricant film thickness (user-supplied)


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


def as_dict() -> Dict[str, float]:
    """All shared constants plus every tool-qualified name (``k_t_H13``, …)."""
    out = {k: float(v) for k, v in _SHARED.items()}
    for tool, vals in _TOOL.items():
        for name, value in vals.items():
            out[f"{name}_{tool}"] = float(value)
    return out
