# -*- coding: utf-8 -*-
"""
Helpers para leer desde la paleta (build_ele) en elementos no definidos.
Obtiene tipo de camino, tipo de punto y color para previsualización.
"""
from __future__ import annotations

from typing import Tuple

from . import constants


def get_tipo_camino(build_ele) -> int:
    """
    Obtiene el tipo de camino: 0=Camino Ordenado, 1=Camino Libre.
    Parámetro TipoCamino (RadioButtonGroup).
    """
    try:
        if build_ele is None:
            return constants.CAMINO_ORDENADO
        val = getattr(getattr(build_ele, "TipoCamino", None), "value", 0) or 0
        return int(val)
    except Exception:
        return constants.CAMINO_ORDENADO


def get_tipo_punto_orden(build_ele) -> str:
    """
    Obtiene el tipo de punto seleccionado (Inicio, Final, etc.)
    desde TipoPuntoOrden (StringComboBox).
    Devuelve la key interna (inicio, final, intermedio_libre, etc.).
    """
    try:
        if build_ele is None:
            return constants.TIPO_INICIO
        raw = (
            getattr(getattr(build_ele, "TipoPuntoOrden", None), "value", "Inicio")
            or "Inicio"
        )
        return constants.label_to_tipo(str(raw).strip())
    except Exception:
        return constants.TIPO_INICIO


COLOR_NAME_TO_ID: dict[str, int] = {
    "Negro": 1,
    "Rojo": 6,
    "Amarillo": 2,
    "Verde": 4,
    "Cyan": 3,
    "Azul": 7,
    "Magenta": 5,
}


def color_name_to_id(color_name: str, default: int = 1) -> int:
    """Mapea un nombre de color de paleta a color ID de Allplan."""
    if color_name is None:
        return default
    return COLOR_NAME_TO_ID.get(str(color_name).strip(), default)


def get_color_puntos(build_ele, default: int = 1) -> int:
    """
    Obtiene el ID de color para las formas geométricas de previsualización.
    Parámetro ColorPuntosNoDefinidos (StringComboBox).
    Permite distinguir entre distintos caminos en la misma ejecución.
    """
    try:
        if build_ele is None:
            return default
        param = getattr(build_ele, "ColorPuntosNoDefinidos", None)
        if param is None:
            return default
        val = getattr(param, "value", None) or getattr(param, "Value", None)
        if val is None:
            return default
        return color_name_to_id(str(val), default)
    except Exception:
        return default


def get_path_key_puntos(build_ele, color_id: int, tipo_camino: int) -> str:
    """
    Devuelve una clave estable de camino para detectar puntos comunes.
    Prioriza PathId si existe en paleta; si no, usa color y tipo de camino.
    """
    try:
        path_param = getattr(build_ele, "PathId", None) if build_ele is not None else None
        path_raw = (
            getattr(path_param, "value", None)
            or getattr(path_param, "Value", None)
            if path_param is not None
            else None
        )
        if path_raw is not None:
            path_id = int(path_raw)
            if path_id > 0:
                return f"path:{path_id}"
    except Exception:
        pass
    try:
        return f"modo:{int(tipo_camino)}|color:{int(color_id)}"
    except Exception:
        return "modo:0|color:1"


def get_common_points_detection_enabled(build_ele, default: bool = True) -> bool:
    """Lee si la detección de puntos comunes está activa en la paleta."""
    try:
        param = (
            getattr(build_ele, "DeteccionPuntosComunesActiva", None)
            if build_ele is not None
            else None
        )
        if param is None:
            return bool(default)
        val = getattr(param, "value", None)
        if val is None:
            val = getattr(param, "Value", None)
        if val is None:
            return bool(default)
        return bool(val)
    except Exception:
        return bool(default)


def get_common_points_tolerance_mm(build_ele, default: float) -> float:
    """Lee tolerancia (mm) para detectar puntos comunes."""
    try:
        param = (
            getattr(build_ele, "ToleranciaPuntosComunesMm", None)
            if build_ele is not None
            else None
        )
        if param is None:
            return float(default)
        val = getattr(param, "value", None)
        if val is None:
            val = getattr(param, "Value", None)
        if val is None:
            return float(default)
        tol = float(val)
        if tol <= 0.0:
            return float(default)
        return tol
    except Exception:
        return float(default)


def get_common_points_halo_color_id(build_ele, default: int) -> int:
    """Lee color de resaltado para puntos comunes."""
    try:
        param = (
            getattr(build_ele, "ColorResaltadoPuntosComunes", None)
            if build_ele is not None
            else None
        )
        if param is None:
            return int(default)
        val = getattr(param, "value", None)
        if val is None:
            val = getattr(param, "Value", None)
        if val is None:
            return int(default)
        return color_name_to_id(str(val), int(default))
    except Exception:
        return int(default)


def get_tipo_camino_and_punto(build_ele) -> Tuple[int, str]:
    """Obtiene (tipo_camino, tipo_punto) desde la paleta."""
    return get_tipo_camino(build_ele), get_tipo_punto_orden(build_ele)
