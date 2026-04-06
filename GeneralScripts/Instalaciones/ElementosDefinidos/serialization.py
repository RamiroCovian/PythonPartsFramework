# -*- coding: utf-8 -*-
"""
Serialización de element_markers y free_placed_points para guardar/restaurar estado.
El script object (fontaneria, etc.) puede usar estas funciones dentro de su
_serialize_state_to_json / _deserialize_state_from_json.
"""
from __future__ import annotations

from typing import Any, Dict, List

try:
    import NemAll_Python_Geometry as AllplanGeo
except Exception:
    AllplanGeo = None


def point_to_dict(pos: Any) -> Dict[str, float]:
    """Convierte un Point3D (o objeto con X, Y, Z) a dict serializable."""
    if pos is None:
        return {"X": 0.0, "Y": 0.0, "Z": 0.0}
    return {
        "X": float(getattr(pos, "X", 0.0)),
        "Y": float(getattr(pos, "Y", 0.0)),
        "Z": float(getattr(pos, "Z", 0.0)),
    }


def point_from_dict(d: Dict[str, float]):
    """Convierte un dict {"X","Y","Z"} a Point3D."""
    if AllplanGeo is None or not d:
        return None
    return AllplanGeo.Point3D(
        float(d.get("X", 0.0)),
        float(d.get("Y", 0.0)),
        float(d.get("Z", 0.0)),
    )


def serialize_element_markers(markers: List[dict]) -> List[dict]:
    """
    Convierte element_markers (con pos como Point3D) a lista de dicts
    con pos como {"X","Y","Z"} para JSON.
    """
    out = []
    for m in markers or []:
        mc = dict(m)
        if "pos" in mc and hasattr(mc["pos"], "X"):
            mc["pos"] = point_to_dict(mc["pos"])
        out.append(mc)
    return out


def deserialize_element_markers(data: List[dict]) -> List[dict]:
    """
    Restaura element_markers desde lista de dicts (pos como {"X","Y","Z"}).
    Devuelve lista de marcadores con pos como Point3D.
    """
    if not data:
        return []
    out = []
    for m in data:
        mc = dict(m)
        if "pos" in mc and isinstance(mc["pos"], dict):
            mc["pos"] = point_from_dict(mc["pos"])
        out.append(mc)
    return out


def serialize_free_placed_points(free_list: List[dict]) -> List[dict]:
    """Convierte free_placed_points a lista de dicts con pos serializado."""
    out = []
    for fp in free_list or []:
        fpc = dict(fp)
        if "pos" in fpc and hasattr(fpc["pos"], "X"):
            fpc["pos"] = point_to_dict(fpc["pos"])
        out.append(fpc)
    return out


def deserialize_free_placed_points(data: List[dict]) -> List[dict]:
    """Restaura free_placed_points desde lista de dicts."""
    if not data:
        return []
    out = []
    for fp in data:
        fpc = dict(fp)
        if "pos" in fpc and isinstance(fpc["pos"], dict):
            fpc["pos"] = point_from_dict(fpc["pos"])
        out.append(fpc)
    return out
