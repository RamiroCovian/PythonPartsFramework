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
# (usado por vertex_utils.compute_segment_cuts_for_path en giros is_90_deg_turn).
# Ø25 saneamiento: NO duplicar — geo_handler suma CODO90_25_* / CODO45_25_* por vértice;
# si aquí 25 > 0, el tubo se recorta dos veces y queda separado del codo.
ELBOW_TRIM_BY_DIAM: dict[int, float] = {
    20: 27.0,
    25: 0.0,
}

# Recorte por TE: (main_in, branch, main_out) -> (trim_main_in, trim_branch, trim_main_out)
TE_TRIMS: dict[tuple[int, int, int], tuple[float, float, float]] = {
    (20, 20, 20): (27.0, 27.0, 27.0),
    (25, 25, 25): (34.5, 34.5, 34.5),
    (25, 20, 20): (32.0, 32.0, 27.0),
    (25, 25, 20): (34.5, 32.0, 32.0),
    (25, 20, 25): (32.0, 30.0, 32.0),
    # TE 110-110-110 (fecal u otro): hasta script dedicado fecal, mismo orden que BIF110_*.
    (110, 110, 110): (140.0, 148.0, 47.0),
}

# Manguitos asimétricos. Tap 40↔25: IN en Ø25, OUT en Ø40.
# Reductor 110↔40: IN en Ø110, OUT en Ø40 (ambos sentidos 110→40 y 40→110).
# Valores reexportados desde geo_handler; hot-reload: utils.trim_config en saneamiento_polyline.
TAPRED_40_25_TRIM_IN_MM = 3.0
TAPRED_40_25_TRIM_OUT_MM = 3.0
REDUCT_110_40_TRIM_IN_MM = 50.0
REDUCT_110_40_TRIM_OUT_MM = 100.0
SPLIT_FECAL_25_110_LAST_REDUCER_EXTRA_X_MM = 109.25
DIRECT_FECAL_40_110_FIRST_SEGMENT_CUT_DELTA_MM = -60.0


def manguito_asymmetric_trim_mm(d_prev: int, d_next: int, d_segment: int) -> float | None:
    """
    Recorte en el extremo del tramo ``d_segment`` en un nudo colineal d_prev → d_next.

    - d_prev / d_next: diámetros ordenados a lo largo de la polilínea (tramo i-1, tramo i).
    - d_segment: diámetro del tramo al que se aplica el corte (debe ser d_prev o d_next).

    Valores: constantes TAPRED_* / REDUCT_* en este módulo.
    """
    if d_segment not in (d_prev, d_next):
        return None

    if (d_prev, d_next) == (25, 40):
        return (
            float(TAPRED_40_25_TRIM_IN_MM)
            if d_segment == 25
            else float(TAPRED_40_25_TRIM_OUT_MM)
        )
    if (d_prev, d_next) == (40, 25):
        return (
            float(TAPRED_40_25_TRIM_OUT_MM)
            if d_segment == 40
            else float(TAPRED_40_25_TRIM_IN_MM)
        )
    if (d_prev, d_next) == (110, 40):
        return (
            float(REDUCT_110_40_TRIM_IN_MM)
            if d_segment == 110
            else float(REDUCT_110_40_TRIM_OUT_MM)
        )
    if (d_prev, d_next) == (40, 110):
        return (
            float(REDUCT_110_40_TRIM_OUT_MM)
            + float(DIRECT_FECAL_40_110_FIRST_SEGMENT_CUT_DELTA_MM)
            if d_segment == 40
            else float(REDUCT_110_40_TRIM_IN_MM)
        )
    if (d_prev, d_next) == (25, 110):
        return (
            float(TAPRED_40_25_TRIM_IN_MM)
            if d_segment == 25
            else float(REDUCT_110_40_TRIM_IN_MM)
            + float(SPLIT_FECAL_25_110_LAST_REDUCER_EXTRA_X_MM)
        )
    if (d_prev, d_next) == (110, 25):
        return (
            float(REDUCT_110_40_TRIM_IN_MM)
            + float(SPLIT_FECAL_25_110_LAST_REDUCER_EXTRA_X_MM)
            if d_segment == 110
            else float(TAPRED_40_25_TRIM_IN_MM)
        )
    return None
