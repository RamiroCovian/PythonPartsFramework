# -*- coding: utf-8 -*-
"""
Helpers para leer desde la paleta (build_ele) en elementos definidos.
Cualquier script (fontaneria, etc.) puede usar estas funciones para obtener
tipo de elemento, tipo de punto libre y tolerancia de selección.
"""
from __future__ import annotations

from typing import Optional, Tuple

from . import catalogo


def get_defined_element_settings(
    build_ele,
    instalacion: str = "AGUA",
) -> Tuple[str, float]:
    """
    Obtiene (element_key, radius) desde la paleta (DefinedElementType, ElementRadius).
    Usa el catálogo para convertir el label del ComboBox a key interna.
    """
    if build_ele is None:
        return "t_sortida", 50.0
    raw = (
        getattr(getattr(build_ele, "DefinedElementType", None), "value", "T sortida")
        or "T sortida"
    )
    label = str(raw).strip()
    element_key = (
        catalogo.label_a_key_agua(label)
        if instalacion.upper() == "AGUA"
        else label.lower().replace(" ", "_")
    )
    radius = 50.0
    try:
        radius = float(
            getattr(getattr(build_ele, "ElementRadius", None), "value", 50) or 50.0
        )
    except Exception:
        radius = 50.0
    if radius <= 0.0:
        radius = 50.0
    return element_key, radius


def get_free_point_type_flag(
    build_ele,
    instalacion: str = "AGUA",
    default_element_key: Optional[str] = None,
) -> str:
    """
    Obtiene la función (inicio/final/intermedio_*) desde TipoPuntoLibre (ComboBox)
    en modo puntos libres. Si no hay valor, infiere según elemento.
    """
    if build_ele is None:
        return "intermedio_libre"
    tipo_param = getattr(build_ele, "TipoPuntoLibre", None)
    raw = None
    if tipo_param is not None:
        raw = getattr(tipo_param, "value", None) or getattr(tipo_param, "Value", None)
    if raw is not None and str(raw).strip():
        raw = str(raw).strip()
        try:
            return catalogo.label_tipo_punto_to_funcion(raw)
        except Exception:
            pass
    # Inferir según elemento: intermedios → intermedio_libre, resto → final
    element_key, _ = get_defined_element_settings(build_ele, instalacion)
    if default_element_key:
        element_key = default_element_key
    if element_key in ("t_sortida", "clau_de_pas"):
        return "intermedio_libre"
    return "final"


def get_free_point_selection_tolerance(build_ele, default_mm: float = 40.0) -> float:
    """
    Tolerancia en mm para seleccionar un punto libre ya colocado
    (paleta ToleranciaSeleccionPunto). Límites 5–200 mm.
    """
    try:
        if build_ele is None:
            return default_mm
        p = getattr(build_ele, "ToleranciaSeleccionPunto", None)
        if p is None:
            return default_mm
        v = getattr(p, "value", None) or getattr(p, "Value", None)
        if v is None:
            return default_mm
        t = float(v)
        return max(5.0, min(200.0, t))
    except Exception:
        return default_mm


def get_element_z_abs(build_ele) -> float:
    """Cota Z absoluta para elemento definido desde paleta ElementZAbs."""
    try:
        if build_ele is None:
            return 0.0
        return float(
            getattr(getattr(build_ele, "ElementZAbs", None), "value", 0) or 0.0
        )
    except Exception:
        return 0.0


def get_element_point_mode(build_ele) -> int:
    """Modo de posición en polilínea: 0=Inicio, 1=Final, 2=Intermedio."""
    try:
        return int(
            getattr(getattr(build_ele, "ElementPointMode", None), "value", 0) or 0
        )
    except Exception:
        return 0
