# -*- coding: utf-8 -*-
"""
Geometría de preview para elementos definidos: círculos, formas por tipo (T, cuadrado, triángulo).
Cualquier script puede usar estas funciones para dibujar marcadores en _draw_preview.
"""
from __future__ import annotations

import math
from typing import Any, List

try:
    import NemAll_Python_Geometry as AllplanGeo
    import NemAll_Python_BasisElements as AllplanBasisElements
except Exception:
    AllplanGeo = None
    AllplanBasisElements = None


def create_point_marker_geometry(
    point: Any,
    properties: Any,
    size: float,
    z_bias: float = 0.0,
) -> List[Any]:
    """
    Crea geometría de un marcador circular en el plano XY alrededor del punto.
    Devuelve lista de ModelElement3D (Line3D) para dibujar en preview.
    """
    if AllplanGeo is None or AllplanBasisElements is None:
        return []
    radius = max(size * 0.5, 0.1)
    cx = getattr(point, "X", 0.0)
    cy = getattr(point, "Y", 0.0)
    cz = getattr(point, "Z", 0.0) + (z_bias or 0.0)
    segments = 32
    elems = []
    prev_pt = None
    for i in range(segments + 1):
        ang = (2.0 * math.pi) * (i / segments)
        x = cx + radius * math.cos(ang)
        y = cy + radius * math.sin(ang)
        curr_pt = AllplanGeo.Point3D(x, y, cz)
        if prev_pt is not None:
            elems.append(
                AllplanBasisElements.ModelElement3D(
                    properties, AllplanGeo.Line3D(prev_pt, curr_pt)
                )
            )
        prev_pt = curr_pt
    return elems


def draw_marker_for_element_type(
    pos: Any,
    element_type: str,
    properties: Any,
    size: float = 45.0,
    create_point_marker_fn=None,
) -> List[Any]:
    """
    Dibuja la forma correspondiente al tipo de elemento:
    cuadrado=colze_base, círculo=clau_de_pas, T=t_sortida, triángulo=taps.
    create_point_marker_fn: opcional, (point, properties, size, z_bias) -> list;
    si no se pasa, se usa create_point_marker_geometry de este módulo.
    """
    if AllplanGeo is None or AllplanBasisElements is None:
        return []
    cx = getattr(pos, "X", 0.0)
    cy = getattr(pos, "Y", 0.0)
    cz = getattr(pos, "Z", 0.0)
    h = size * 0.5
    elems = []
    et = (element_type or "").strip().lower()
    if et == "colze_base":
        p1 = AllplanGeo.Point3D(cx - h, cy - h, cz)
        p2 = AllplanGeo.Point3D(cx + h, cy - h, cz)
        p3 = AllplanGeo.Point3D(cx + h, cy + h, cz)
        p4 = AllplanGeo.Point3D(cx - h, cy + h, cz)
        for a, b in [(p1, p2), (p2, p3), (p3, p4), (p4, p1)]:
            elems.append(
                AllplanBasisElements.ModelElement3D(
                    properties, AllplanGeo.Line3D(a, b)
                )
            )
    elif et == "t_sortida":
        p_bottom = AllplanGeo.Point3D(cx, cy - h, cz)
        p_top = AllplanGeo.Point3D(cx, cy + h, cz)
        p_left = AllplanGeo.Point3D(cx - h, cy + h, cz)
        p_right = AllplanGeo.Point3D(cx + h, cy + h, cz)
        elems.append(
            AllplanBasisElements.ModelElement3D(
                properties, AllplanGeo.Line3D(p_bottom, p_top)
            )
        )
        elems.append(
            AllplanBasisElements.ModelElement3D(
                properties, AllplanGeo.Line3D(p_left, p_right)
            )
        )
    elif et == "taps":
        p1 = AllplanGeo.Point3D(cx, cy - h, cz)
        p2 = AllplanGeo.Point3D(cx - h, cy + h * 0.5, cz)
        p3 = AllplanGeo.Point3D(cx + h, cy + h * 0.5, cz)
        for a, b in [(p1, p2), (p2, p3), (p3, p1)]:
            elems.append(
                AllplanBasisElements.ModelElement3D(
                    properties, AllplanGeo.Line3D(a, b)
                )
            )
    else:
        fn = create_point_marker_fn or create_point_marker_geometry
        elems = fn(pos, properties, size, 0.0)
    return elems


def make_circle_polyline_for_marker(
    center: Any,
    radius: float,
    segments: int = 24,
):
    """
    Crea una Polyline3D circular en el plano XY para marcadores de elementos definidos.
    Útil para geometría auxiliar (ej. script object).
    """
    if AllplanGeo is None or radius <= 0 or segments < 3:
        return None
    cx = getattr(center, "X", 0.0)
    cy = getattr(center, "Y", 0.0)
    cz = getattr(center, "Z", 0.0)
    poly = AllplanGeo.Polyline3D()
    for i in range(segments + 1):
        ang = 2.0 * math.pi * (i / segments)
        x = cx + radius * math.cos(ang)
        y = cy + radius * math.sin(ang)
        poly += AllplanGeo.Point3D(x, y, cz)
    return poly
