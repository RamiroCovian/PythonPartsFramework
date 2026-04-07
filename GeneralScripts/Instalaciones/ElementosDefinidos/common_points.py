# -*- coding: utf-8 -*-
"""
Detección y topología de puntos comunes para ElementosDefinidos.

Replica la misma idea usada en ElementosNoDefinidos, pero partiendo de
``saved_paths`` y de los marcadores/elementos ya colocados sobre esos caminos.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Set, Tuple


def _point_xyz(pos: Any) -> Optional[Tuple[float, float, float]]:
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


def _distance_sq(
    a: Tuple[float, float, float],
    b: Tuple[float, float, float],
) -> float:
    dx = a[0] - b[0]
    dy = a[1] - b[1]
    dz = a[2] - b[2]
    return dx * dx + dy * dy + dz * dz


def _marker_kind_to_tipo(kind: str) -> str:
    kind = str(kind or "").strip().lower()
    if kind == "start":
        return "inicio"
    if kind == "end":
        return "final"
    return "intermedio_libre"


def _path_point_tipo(path_points: List[Any], pt_idx: int) -> str:
    if not path_points:
        return "intermedio_ordenado"
    if pt_idx <= 0:
        return "inicio"
    if pt_idx >= len(path_points) - 1:
        return "final"
    return "intermedio_ordenado"


def _flatten_saved_paths(saved_paths: List[List[Any]]) -> List[dict]:
    puntos: List[dict] = []
    for path_idx, path_points in enumerate(saved_paths or []):
        for pt_idx, pos in enumerate(path_points or []):
            puntos.append(
                {
                    "pos": pos,
                    "path_idx": path_idx,
                    "pt_idx": pt_idx,
                    "path_key": f"path_{path_idx}",
                    "tipo": _path_point_tipo(path_points, pt_idx),
                }
            )
    return puntos


def detect_common_point_groups(
    puntos: List[dict],
    tolerance_mm: float = 1.0,
    min_distinct_paths: int = 2,
) -> List[Dict[str, object]]:
    """
    Detecta grupos de puntos comunes por proximidad.

    Cada punto debe traer al menos:
    - pos
    - path_key
    """
    if not puntos:
        return []

    tol_sq = max(float(tolerance_mm), 0.0) ** 2
    prepared: List[Dict[str, object]] = []
    for idx, point_data in enumerate(puntos):
        xyz = _point_xyz(point_data.get("pos"))
        if xyz is None:
            continue
        prepared.append(
            {
                "idx": idx,
                "xyz": xyz,
                "path_key": str(point_data.get("path_key") or "default"),
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


def build_common_points_topology(
    saved_paths: List[List[Any]],
    tolerance_mm: float = 1.0,
) -> dict:
    """
    Construye topología de puntos comunes a partir de ``saved_paths``.

    Devuelve:
    - node_count
    - edge_count
    - nodes: [{id, path_keys, point_count, center}]
    - edges: [{a, b, via_node}]
    - adjacency: {path_key: [neighbors]}
    """
    puntos = _flatten_saved_paths(saved_paths)
    groups = detect_common_point_groups(
        puntos,
        tolerance_mm=tolerance_mm,
        min_distinct_paths=2,
    )

    nodes = []
    for idx, group in enumerate(groups, start=1):
        nodes.append(
            {
                "id": f"CP-{idx}",
                "path_keys": list(group.get("path_keys", [])),
                "point_count": len(group.get("indices", [])),
                "center": tuple(group.get("center", (0.0, 0.0, 0.0))),
                "indices": list(group.get("indices", [])),
            }
        )

    edge_set = set()
    edges = []
    for node in nodes:
        paths = list(node.get("path_keys", []))
        for i in range(len(paths)):
            for j in range(i + 1, len(paths)):
                a = str(paths[i])
                b = str(paths[j])
                key = tuple(sorted((a, b)) + [str(node.get("id"))])
                if key in edge_set:
                    continue
                edge_set.add(key)
                edges.append({"a": a, "b": b, "via_node": str(node.get("id"))})

    adjacency: Dict[str, set] = {}
    for edge in edges:
        a = str(edge.get("a"))
        b = str(edge.get("b"))
        adjacency.setdefault(a, set()).add(b)
        adjacency.setdefault(b, set()).add(a)

    adjacency_sorted = {k: sorted(list(v)) for k, v in adjacency.items()}

    return {
        "node_count": len(nodes),
        "edge_count": len(edges),
        "nodes": nodes,
        "edges": edges,
        "adjacency": adjacency_sorted,
        "points": puntos,
    }


def _suggest_element(path_count: int, tipos_punto: List[str]) -> str:
    tipos = set(tipos_punto)
    if path_count >= 3:
        return "t_sortida"
    if "bifurcación" in tipos or "bifurcacion" in tipos:
        return "t_sortida"
    if path_count == 2:
        has_inicio = "inicio" in tipos
        has_final = "final" in tipos
        if has_inicio and has_final:
            return "paso"
        if has_inicio or has_final:
            return "colze"
        return "paso"
    return "paso"


def build_common_junctions(
    saved_paths: List[List[Any]],
    topology: Optional[dict] = None,
    element_markers: Optional[List[dict]] = None,
    tolerance_mm: float = 1.0,
) -> List[dict]:
    """
    Genera junctions consumibles por otros módulos a partir de la topología.

    Si se pasan ``element_markers``, se incorporan sus tipos lógicos cuando caen
    cerca del nodo común.
    """
    topo = topology or build_common_points_topology(
        saved_paths,
        tolerance_mm=tolerance_mm,
    )
    puntos = list(topo.get("points", []))
    nodes = list(topo.get("nodes", []))
    tol_sq = max(float(tolerance_mm), 0.0) ** 2

    marker_points = []
    for marker in element_markers or []:
        xyz = _point_xyz(marker.get("pos"))
        if xyz is None:
            continue
        marker_points.append(
            {
                "xyz": xyz,
                "tipo": _marker_kind_to_tipo(str(marker.get("kind", ""))),
                "element_type": marker.get("element_type"),
            }
        )

    junctions = []
    for node in nodes:
        center = tuple(node.get("center", (0.0, 0.0, 0.0)))
        tipos_punto = set()
        element_types = set()

        for idx in node.get("indices", []):
            if 0 <= int(idx) < len(puntos):
                punto = puntos[int(idx)]
                tipo = punto.get("tipo")
                if tipo:
                    tipos_punto.add(str(tipo))

        for marker in marker_points:
            if _distance_sq(center, marker["xyz"]) <= tol_sq:
                if marker.get("tipo"):
                    tipos_punto.add(str(marker["tipo"]))
                if marker.get("element_type"):
                    element_types.add(str(marker["element_type"]))

        path_keys = list(node.get("path_keys", []))
        path_count = len(path_keys)
        suggested = _suggest_element(path_count, sorted(tipos_punto))

        junctions.append(
            {
                "node_id": str(node.get("id", "")),
                "x": float(center[0]) if len(center) > 0 else 0.0,
                "y": float(center[1]) if len(center) > 1 else 0.0,
                "z": float(center[2]) if len(center) > 2 else 0.0,
                "path_keys": path_keys,
                "path_count": path_count,
                "tipos_punto": sorted(tipos_punto),
                "element_types": sorted(element_types),
                "suggested_element": suggested,
            }
        )

    return junctions
