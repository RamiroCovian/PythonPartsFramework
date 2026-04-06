# -*- coding: utf-8 -*-
"""
Serialización de puntos_no_definidos para guardar/restaurar estado.
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


def serialize_puntos_no_definidos(puntos: List[dict]) -> List[dict]:
    """
    Convierte puntos_no_definidos a lista de dicts con pos serializado.
    """
    out = []
    for p in puntos or []:
        pc = dict(p)
        if "pos" in pc and hasattr(pc["pos"], "X"):
            pc["pos"] = point_to_dict(pc["pos"])
        out.append(pc)
    return out


def deserialize_puntos_no_definidos(data: List[dict]) -> List[dict]:
    """
    Restaura puntos_no_definidos desde lista de dicts.
    """
    if not data:
        return []
    out = []
    for p in data:
        pc = dict(p)
        if "pos" in pc and isinstance(pc["pos"], dict):
            pc["pos"] = point_from_dict(pc["pos"])
        out.append(pc)
    return out
