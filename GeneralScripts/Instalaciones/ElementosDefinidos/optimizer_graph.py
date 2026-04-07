# -*- coding: utf-8 -*-
"""
Construcción de nodos exportables para elementos definidos.

Replica el contrato base usado en ElementosNoDefinidos, adaptado a:
- ``element_markers``: marcadores colocados sobre una polilínea
- ``free_placed_points``: puntos libres colocados fuera del flujo de polilínea
"""
from __future__ import annotations

from collections import defaultdict
from typing import Any, Dict, List, Optional, Tuple


def _point_to_coords(pos: Any) -> Dict[str, float]:
    if pos is None:
        return {"x": 0.0, "y": 0.0, "z": 0.0}
    return {
        "x": float(getattr(pos, "X", 0.0)),
        "y": float(getattr(pos, "Y", 0.0)),
        "z": float(getattr(pos, "Z", 0.0)),
    }


def _distance_sq(a: Any, b: Any) -> float:
    try:
        dx = float(getattr(a, "X", 0.0)) - float(getattr(b, "X", 0.0))
        dy = float(getattr(a, "Y", 0.0)) - float(getattr(b, "Y", 0.0))
        dz = float(getattr(a, "Z", 0.0)) - float(getattr(b, "Z", 0.0))
    except Exception:
        return float("inf")
    return dx * dx + dy * dy + dz * dz


def _segment_sort_key(pos: Any, path_points: List[Any]) -> Optional[float]:
    if pos is None or not path_points:
        return None
    if len(path_points) == 1:
        return 0.0

    best_idx = None
    best_dist = None
    for idx in range(len(path_points) - 1):
        a = path_points[idx]
        b = path_points[idx + 1]
        d = min(_distance_sq(pos, a), _distance_sq(pos, b))
        if best_dist is None or d < best_dist:
            best_dist = d
            best_idx = idx

    if best_idx is None:
        return None
    return float(best_idx) + 0.5


def _resolve_marker_path_idx(
    marker: dict,
    saved_paths: List[List[Any]],
) -> Optional[int]:
    path_idx = marker.get("path_idx")
    if path_idx is not None:
        try:
            return int(path_idx)
        except Exception:
            return None

    pos = marker.get("pos")
    if pos is None or not saved_paths:
        return None

    best_path_idx = None
    best_dist = None
    for idx, path_points in enumerate(saved_paths):
        if not path_points:
            continue
        sort_key = _segment_sort_key(pos, path_points)
        if sort_key is None:
            continue
        seg_idx = int(sort_key)
        point_a = path_points[seg_idx]
        point_b = path_points[min(seg_idx + 1, len(path_points) - 1)]
        d = min(_distance_sq(pos, point_a), _distance_sq(pos, point_b))
        if best_dist is None or d < best_dist:
            best_dist = d
            best_path_idx = idx
    return best_path_idx


def _resolve_marker_sort_key(
    marker: dict,
    path_points: List[Any],
    fallback_index: int,
) -> float:
    pt_idx = marker.get("pt_idx")
    if pt_idx is not None:
        try:
            return float(pt_idx)
        except Exception:
            pass

    projected = _segment_sort_key(marker.get("pos"), path_points)
    if projected is not None:
        return projected

    return float(len(path_points) + fallback_index)


def _logical_tipo_from_marker(marker: dict) -> str:
    kind = str(marker.get("kind", "") or "").strip().lower()
    if kind == "start":
        return "inicio"
    if kind == "end":
        return "final"
    return "intermedio_libre"


def _logical_tipo_from_free_point(point: dict) -> str:
    return str(point.get("flag", "") or "intermedio_libre").strip().lower()


def _normalize_node_tipo(raw_tipo: str) -> str:
    if raw_tipo == "inicio":
        return "inicio"
    if raw_tipo == "final":
        return "final"
    if raw_tipo in ("bifurcacion", "bifurcación", "intermedio_libre"):
        return "union"
    if raw_tipo == "intermedio_ordenado":
        return "codo"
    return "union"


def _build_node_id(path_index: int, counters: dict, node_tipo: str) -> str:
    if node_tipo == "inicio":
        counters["inicio"] += 1
        return f"A{counters['inicio']}"
    if node_tipo == "final":
        counters["final"] += 1
        return f"B{counters['final']}"
    if node_tipo == "codo":
        counters["codo"] += 1
        return f"C{path_index}-{counters['codo']}"

    counters["union"] += 1
    return f"U{path_index}-{counters['union']}"


def _build_path_groups(
    element_markers: List[dict],
    saved_paths: List[List[Any]],
) -> Dict[str, List[dict]]:
    grouped: Dict[str, List[dict]] = defaultdict(list)
    for fallback_index, marker in enumerate(element_markers or []):
        path_idx = _resolve_marker_path_idx(marker, saved_paths)
        path_key = (
            f"path_{path_idx}"
            if path_idx is not None
            else f"path_indefinido_{fallback_index}"
        )
        path_points = (
            saved_paths[path_idx]
            if path_idx is not None and 0 <= path_idx < len(saved_paths)
            else []
        )
        grouped[path_key].append(
            {
                "source": "element_marker",
                "data": marker,
                "tipo_logico": _logical_tipo_from_marker(marker),
                "sort_key": _resolve_marker_sort_key(
                    marker,
                    path_points,
                    fallback_index,
                ),
                "path_idx": path_idx,
            }
        )
    return grouped


def build_nodos_export_data(
    element_markers: List[dict],
    saved_paths: Optional[List[List[Any]]] = None,
    free_placed_points: Optional[List[dict]] = None,
) -> List[dict]:
    """
    Devuelve una lista plana de nodos con este contrato:
    - id
    - tipo
    - coordenadas
    - anterior
    - siguientes

    Los nodos derivados de ``free_placed_points`` se exportan sin conectividad.
    """
    saved_paths = saved_paths or []
    free_placed_points = free_placed_points or []
    grouped = _build_path_groups(element_markers or [], saved_paths)

    nodos: List[dict] = []
    ordered_path_keys = sorted(grouped.keys())
    for path_index, path_key in enumerate(ordered_path_keys, start=1):
        group = sorted(
            grouped[path_key],
            key=lambda item: (float(item.get("sort_key", 0.0)), path_key),
        )
        counters = {
            "inicio": 0,
            "final": 0,
            "codo": 0,
            "union": 0,
        }
        node_ids: List[str] = []
        for item in group:
            node_tipo = _normalize_node_tipo(str(item.get("tipo_logico", "") or ""))
            node_ids.append(_build_node_id(path_index, counters, node_tipo))

        for idx, item in enumerate(group):
            data = item.get("data", {}) or {}
            pos = data.get("pos")
            nodos.append(
                {
                    "id": node_ids[idx],
                    "tipo": _normalize_node_tipo(
                        str(item.get("tipo_logico", "") or "")
                    ),
                    "coordenadas": _point_to_coords(pos),
                    "anterior": node_ids[idx - 1] if idx > 0 else None,
                    "siguientes": (
                        [node_ids[idx + 1]] if idx < len(node_ids) - 1 else []
                    ),
                    "path_key": path_key,
                    "path_idx": item.get("path_idx"),
                    "element_type": data.get("element_type"),
                    "source": item.get("source"),
                }
            )

    free_offset = len(ordered_path_keys)
    for idx, point in enumerate(free_placed_points, start=1):
        logical_tipo = _logical_tipo_from_free_point(point)
        node_tipo = _normalize_node_tipo(logical_tipo)
        path_index = free_offset + idx
        node_id = _build_node_id(
            path_index,
            {"inicio": 0, "final": 0, "codo": 0, "union": 0},
            node_tipo,
        )
        nodos.append(
            {
                "id": node_id,
                "tipo": node_tipo,
                "coordenadas": _point_to_coords(point.get("pos")),
                "anterior": None,
                "siguientes": [],
                "path_key": f"free_point_{idx}",
                "path_idx": None,
                "element_type": point.get("element_type"),
                "source": "free_placed_point",
            }
        )

    return nodos


def build_optimizer_graph_json(
    element_markers: List[dict],
    saved_paths: Optional[List[List[Any]]] = None,
    free_placed_points: Optional[List[dict]] = None,
    graph_id: Optional[str] = None,
    graph_name: Optional[str] = None,
) -> dict:
    """
    Construye un contenedor simple con la lista de nodos exportables.
    """
    return {
        "id": graph_id or "elementos_definidos",
        "nombre": graph_name or "Elementos Definidos",
        "nodos": build_nodos_export_data(
            element_markers=element_markers,
            saved_paths=saved_paths,
            free_placed_points=free_placed_points,
        ),
    }
