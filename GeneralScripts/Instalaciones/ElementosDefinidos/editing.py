# -*- coding: utf-8 -*-
"""
Utilidades para seleccionar y editar puntos ya colocados (elementos definidos en el plano).
Permite detectar qué punto libre está bajo el cursor o bajo un clic.
"""
from __future__ import annotations

from typing import Any, List


def find_hover_free_point(
    click_point: Any,
    free_placed_points: List[dict],
    tolerance_mm: float = 80.0,
) -> int:
    """
    Devuelve el índice del punto libre más cercano al click_point dentro de tolerance_mm.
    Cada elemento de free_placed_points debe tener clave "pos" con .X, .Y, .Z (p. ej. Point3D).

    Returns:
        Índice del punto encontrado (0-based) o -1 si ninguno está dentro de la tolerancia.
    """
    if not free_placed_points or tolerance_mm <= 0:
        return -1
    try:
        cx = getattr(click_point, "X", 0)
        cy = getattr(click_point, "Y", 0)
        cz = getattr(click_point, "Z", 0)
    except Exception:
        return -1

    min_dist = float("inf")
    found_idx = -1
    for i, fp in enumerate(free_placed_points):
        pos = fp.get("pos")
        if pos is None:
            continue
        try:
            px = getattr(pos, "X", 0)
            py = getattr(pos, "Y", 0)
            pz = getattr(pos, "Z", 0)
        except Exception:
            continue
        dist_sq = (cx - px) ** 2 + (cy - py) ** 2 + (cz - pz) ** 2
        dist = dist_sq**0.5
        if dist <= tolerance_mm and dist < min_dist:
            min_dist = dist
            found_idx = i
    return found_idx


def get_index_to_select_after_add(free_list: List[dict]) -> int:
    """
    Devuelve el índice del punto que debe quedar seleccionado tras añadir uno nuevo
    (normalmente el último: len(free_list) - 1).
    Útil para que, al añadir un punto libre, ese punto quede seleccionado en la UI.

    Returns:
        Índice a seleccionar (>= 0) o -1 si la lista está vacía.
    """
    if not free_list:
        return -1
    return len(free_list) - 1
