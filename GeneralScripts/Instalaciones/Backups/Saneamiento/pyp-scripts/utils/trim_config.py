# -*- coding: utf-8 -*-
"""
Configuración de recortes de tubos según elemento de unión (codo, manguito, TE).
Valores en mm aplicados a cada extremo del tubo que toca el fitting.
"""
from __future__ import annotations

# Recorte por manguito: (diam_izq, diam_der) -> mm a recortar en cada tubo
MANGUITO_TRIM_BY_DIAM: dict[tuple[int, int], float] = {
    (20, 20): 14.5,
    (25, 25): 17.0,
    (20, 25): 14.5,
    (25, 20): 14.5,
}

# Recorte por codo 90°: diámetro -> mm a recortar en cada tubo
ELBOW_TRIM_BY_DIAM: dict[int, float] = {
    20: 27.0,
    25: 34.5,
}

# Recorte por TE: (main_in, branch, main_out) -> (trim_main_in, trim_branch, trim_main_out)
TE_TRIMS: dict[tuple[int, int, int], tuple[float, float, float]] = {
    (20, 20, 20): (27.0, 27.0, 27.0),
    (25, 25, 25): (34.5, 34.5, 34.5),
    (25, 20, 20): (32.0, 32.0, 27.0),
    (25, 25, 20): (34.5, 32.0, 32.0),
    (25, 20, 25): (32.0, 30.0, 32.0),
}
