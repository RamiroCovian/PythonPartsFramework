# -*- coding: utf-8 -*-
"""
Geometría de preview para puntos indicativos sin objetos definidos.
Formas: círculo (inicio), cuadrado (final), triángulo (bifurcación),
rombo (intermedio ordenado), pentágono (intermedio libre).
"""
from __future__ import annotations

import math
from typing import Any, List

try:
    import NemAll_Python_Geometry as AllplanGeo
    import NemAll_Python_BasisElements as AllplanBasisElements
    import NemAll_Python_BaseElements as AllplanBaseElements
except Exception:
    AllplanGeo = None
    AllplanBasisElements = None
    AllplanBaseElements = None

from . import constants
from .common_points import detect_common_point_groups


def _make_properties(color_id: int, base_props: Any = None) -> Any:
    """Crea CommonProperties para preview con el color indicado."""
    if AllplanBaseElements is None:
        return None
    try:
        if base_props is not None and hasattr(base_props, "GetGlobalProperties"):
            prop = AllplanBaseElements.CommonProperties()
            prop.GetGlobalProperties()
            # Copiar atributos relevantes si base_props tiene _clone_properties
            if hasattr(base_props, "Pen"):
                prop.Pen = getattr(base_props, "Pen", 1)
        else:
            prop = AllplanBaseElements.CommonProperties()
            prop.GetGlobalProperties()
        prop.Color = int(color_id)
        prop.ColorByLayer = False
        prop.PenByLayer = False
        prop.Construction = True
        return prop
    except Exception:
        return None


def _create_circle_lines(
    cx: float, cy: float, cz: float, size: float, segments: int = 32
) -> List[tuple]:
    """Genera pares de puntos para un círculo en el plano XY."""
    if AllplanGeo is None:
        return []
    radius = max(size * 0.5, 0.1)
    pts = []
    for i in range(segments + 1):
        ang = (2.0 * math.pi) * (i / segments)
        x = cx + radius * math.cos(ang)
        y = cy + radius * math.sin(ang)
        pts.append(AllplanGeo.Point3D(x, y, cz))
    return [(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]


def _create_square_lines(
    cx: float, cy: float, cz: float, size: float
) -> List[tuple]:
    """Genera pares de puntos para un cuadrado en el plano XY."""
    if AllplanGeo is None:
        return []
    h = size * 0.5
    p1 = AllplanGeo.Point3D(cx - h, cy - h, cz)
    p2 = AllplanGeo.Point3D(cx + h, cy - h, cz)
    p3 = AllplanGeo.Point3D(cx + h, cy + h, cz)
    p4 = AllplanGeo.Point3D(cx - h, cy + h, cz)
    return [(p1, p2), (p2, p3), (p3, p4), (p4, p1)]


def _create_triangle_lines(
    cx: float, cy: float, cz: float, size: float
) -> List[tuple]:
    """Genera pares de puntos para un triángulo en el plano XY."""
    if AllplanGeo is None:
        return []
    h = size * 0.5
    p1 = AllplanGeo.Point3D(cx, cy - h, cz)
    p2 = AllplanGeo.Point3D(cx - h, cy + h * 0.5, cz)
    p3 = AllplanGeo.Point3D(cx + h, cy + h * 0.5, cz)
    return [(p1, p2), (p2, p3), (p3, p1)]


def _create_rhombus_lines(
    cx: float, cy: float, cz: float, size: float
) -> List[tuple]:
    """Genera pares de puntos para un rombo en el plano XY."""
    if AllplanGeo is None:
        return []
    h = size * 0.5
    p_top = AllplanGeo.Point3D(cx, cy + h, cz)
    p_right = AllplanGeo.Point3D(cx + h, cy, cz)
    p_bottom = AllplanGeo.Point3D(cx, cy - h, cz)
    p_left = AllplanGeo.Point3D(cx - h, cy, cz)
    return [(p_top, p_right), (p_right, p_bottom), (p_bottom, p_left), (p_left, p_top)]


def _create_pentagon_lines(
    cx: float, cy: float, cz: float, size: float
) -> List[tuple]:
    """Genera pares de puntos para un pentágono en el plano XY."""
    if AllplanGeo is None:
        return []
    radius = max(size * 0.5, 0.1)
    pts = []
    for i in range(5):
        ang = (2.0 * math.pi) * (i / 5) - math.pi / 2
        x = cx + radius * math.cos(ang)
        y = cy + radius * math.sin(ang)
        pts.append(AllplanGeo.Point3D(x, y, cz))
    return [(pts[i], pts[(i + 1) % 5]) for i in range(5)]


def create_shape_geometry(
    pos: Any,
    shape: str,
    size: float = 45.0,
) -> List[tuple]:
    """
    Genera pares (p1, p2) de puntos para las líneas de la forma.
    shape: circle, square, triangle, rhombus, pentagon
    """
    cx = float(getattr(pos, "X", 0.0) or 0.0)
    cy = float(getattr(pos, "Y", 0.0) or 0.0)
    cz = float(getattr(pos, "Z", 0.0) or 0.0)
    shape = (shape or "").strip().lower()
    if shape == "square":
        return _create_square_lines(cx, cy, cz, size)
    if shape == "triangle":
        return _create_triangle_lines(cx, cy, cz, size)
    if shape == "rhombus":
        return _create_rhombus_lines(cx, cy, cz, size)
    if shape == "pentagon":
        return _create_pentagon_lines(cx, cy, cz, size)
    return _create_circle_lines(cx, cy, cz, size)


def draw_marker_for_tipo_punto(
    pos: Any,
    tipo_punto: str,
    properties: Any,
    size: float = 45.0,
) -> List[Any]:
    """
    Dibuja la forma geométrica correspondiente al tipo de punto.
    Devuelve lista de ModelElement3D (Line3D) para DrawElementPreview.
    """
    if AllplanGeo is None or AllplanBasisElements is None:
        return []
    shape = constants.get_shape_for_tipo(tipo_punto)
    line_pairs = create_shape_geometry(pos, shape, size)
    elems = []
    for p1, p2 in line_pairs:
        elems.append(
            AllplanBasisElements.ModelElement3D(
                properties, AllplanGeo.Line3D(p1, p2)
            )
        )
    return elems


def draw_preview_at_cursor(
    pos: Any,
    build_ele: Any,
    base_props: Any = None,
    size: float = 45.0,
) -> List[Any]:
    """
    Dibuja la forma de preview en la posición del cursor (modo añadir punto).
    Lee tipo y color desde build_ele.
    """
    from . import palette

    tipo = palette.get_tipo_punto_orden(build_ele)
    color_id = palette.get_color_puntos(build_ele, 6)
    prop = _make_properties(color_id, base_props)
    if prop is None:
        return []
    return draw_marker_for_tipo_punto(pos, tipo, prop, size)


def draw_all_puntos_no_definidos(
    puntos: List[dict],
    default_color_id: int = 6,
    base_props: Any = None,
    size: float = 45.0,
    build_ele: Any = None,
) -> List[Any]:
    """
    Dibuja todos los puntos no definidos.
    Cada punto puede tener color_id propio (para distinguir caminos);
    si no, usa default_color_id.
    puntos: lista de dict con {"pos": Point3D, "tipo": str, "color_id": int?}
    """
    if not puntos:
        return []
    from . import palette

    result = []
    common_enabled = palette.get_common_points_detection_enabled(
        build_ele, default=True
    )
    common_tol_mm = palette.get_common_points_tolerance_mm(
        build_ele, default=constants.COMMON_POINT_TOLERANCE_MM
    )
    common_halo_color_id = palette.get_common_points_halo_color_id(
        build_ele, default=constants.COMMON_POINT_COLOR_ID
    )

    if common_enabled:
        common_groups = detect_common_point_groups(
            puntos,
            tolerance_mm=common_tol_mm,
            min_distinct_paths=2,
        )
    else:
        common_groups = []
    common_indices = {
        idx
        for group in common_groups
        for idx in group.get("indices", [])
    }
    common_prop = _make_properties(common_halo_color_id, base_props)

    for idx, p in enumerate(puntos):
        pos = p.get("pos")
        tipo = p.get("tipo", constants.TIPO_INICIO)
        color_id = p.get("color_id")
        if color_id is None:
            color_id = default_color_id
        if pos is None:
            continue
        prop = _make_properties(int(color_id), base_props)
        if prop is None:
            continue
        result.extend(draw_marker_for_tipo_punto(pos, tipo, prop, size))
        if (
            idx in common_indices
            and common_prop is not None
            and AllplanBasisElements is not None
            and AllplanGeo is not None
        ):
            halo_size = size * constants.COMMON_POINT_HALO_SCALE
            halo_pairs = _create_circle_lines(
                float(getattr(pos, "X", 0.0)),
                float(getattr(pos, "Y", 0.0)),
                float(getattr(pos, "Z", 0.0)),
                halo_size,
                segments=24,
            )
            for p1, p2 in halo_pairs:
                result.append(
                    AllplanBasisElements.ModelElement3D(
                        common_prop, AllplanGeo.Line3D(p1, p2)
                    )
                )
    return result
