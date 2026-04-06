# -*- coding: utf-8 -*-
"""
Detección de puntos comunes entre caminos por proximidad.

Se consideran "comunes" los grupos de puntos que:
- están dentro de una tolerancia espacial configurable, y
- pertenecen al menos a 2 caminos distintos.
"""
from __future__ import annotations

from typing import Dict, List, Set, Tuple

from . import constants


def _point_xyz(point_data: dict) -> Tuple[float, float, float] | None:
    pos = point_data.get("pos")
    if pos is None:
        return None
    try:
        return (
            float(getattr(pos, "X", 0.0)),
            float(getattr(pos, "Y", 0.0)),
            float(getattr(pos, "Z", 0.0)),
        )
    except Exception:
        return None


def _distance_sq(a: Tuple[float, float, float], b: Tuple[float, float, float]) -> float:
    dx = a[0] - b[0]
    dy = a[1] - b[1]
    dz = a[2] - b[2]
    return dx * dx + dy * dy + dz * dz


def _resolve_path_key(point_data: dict) -> str:
    if "path_key" in point_data and point_data["path_key"] is not None:
        return str(point_data["path_key"])
    if "path_id" in point_data and point_data["path_id"] is not None:
        return f"path:{point_data['path_id']}"
    if "camino_id" in point_data and point_data["camino_id"] is not None:
        return f"camino:{point_data['camino_id']}"
    if "color_id" in point_data and point_data["color_id"] is not None:
        return f"color:{point_data['color_id']}"
    return "default"


def detect_common_point_groups(
    puntos: List[dict],
    tolerance_mm: float = constants.COMMON_POINT_TOLERANCE_MM,
    min_distinct_paths: int = 2,
) -> List[Dict[str, object]]:
    """
    Detecta grupos de puntos comunes por proximidad.

    Devuelve una lista de grupos con:
    - indices: índices en la lista original
    - path_keys: caminos distintos detectados
    - center: centro promedio del grupo (x, y, z)
    """
    if not puntos:
        return []

    tol_sq = max(float(tolerance_mm), 0.0) ** 2
    prepared: List[Dict[str, object]] = []
    for idx, point_data in enumerate(puntos):
        xyz = _point_xyz(point_data)
        if xyz is None:
            continue
        prepared.append(
            {
                "idx": idx,
                "xyz": xyz,
                "path_key": _resolve_path_key(point_data),
            }
        )

    if len(prepared) < 2:
        return []

    visited: Set[int] = set()
    groups: List[Dict[str, object]] = []

    for i in range(len(prepared)):
        if i in visited:
            continue

        stack = [i]
        component: List[int] = []
        visited.add(i)

        while stack:
            cur = stack.pop()
            component.append(cur)
            cur_xyz = prepared[cur]["xyz"]
            for j in range(len(prepared)):
                if j in visited:
                    continue
                if _distance_sq(cur_xyz, prepared[j]["xyz"]) <= tol_sq:
                    visited.add(j)
                    stack.append(j)

        if len(component) < 2:
            continue

        path_keys = {str(prepared[k]["path_key"]) for k in component}
        if len(path_keys) < max(int(min_distinct_paths), 2):
            continue

        xs = [prepared[k]["xyz"][0] for k in component]
        ys = [prepared[k]["xyz"][1] for k in component]
        zs = [prepared[k]["xyz"][2] for k in component]
        center = (
            sum(xs) / len(xs),
            sum(ys) / len(ys),
            sum(zs) / len(zs),
        )

        groups.append(
            {
                "indices": [int(prepared[k]["idx"]) for k in component],
                "path_keys": sorted(path_keys),
                "center": center,
            }
        )

    return groups

