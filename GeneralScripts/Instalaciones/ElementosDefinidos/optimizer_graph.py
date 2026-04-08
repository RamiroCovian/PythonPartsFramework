# -*- coding: utf-8 -*-
"""
Construcción de exportes de nodos para ElementosDefinidos.

El módulo expone dos vistas complementarias:

- ``build_nodos_export_data(...)``:
  lista plana de nodos enriquecidos, útil para consumidores simples.
- ``build_optimizer_graph_json(...)``:
  contenedor tipo grafo con caminos, segmentos y metadatos topológicos.
"""
from __future__ import annotations

from collections import defaultdict
from typing import Any, Dict, List, Optional, Tuple


def _point_to_coords(pos: Any) -> Dict[str, float]:
    """Convierte un punto con atributos X/Y/Z a un dict serializable."""
    if pos is None:
        return {"x": 0.0, "y": 0.0, "z": 0.0}
    return {
        "x": float(getattr(pos, "X", 0.0)),
        "y": float(getattr(pos, "Y", 0.0)),
        "z": float(getattr(pos, "Z", 0.0)),
    }


def _distance_sq(a: Any, b: Any) -> float:
    """Distancia al cuadrado entre dos puntos con atributos X/Y/Z."""
    try:
        dx = float(getattr(a, "X", 0.0)) - float(getattr(b, "X", 0.0))
        dy = float(getattr(a, "Y", 0.0)) - float(getattr(b, "Y", 0.0))
        dz = float(getattr(a, "Z", 0.0)) - float(getattr(b, "Z", 0.0))
    except Exception:
        return float("inf")
    return dx * dx + dy * dy + dz * dz


def _center_to_point(center: Any) -> Any:
    """Normaliza un centro de nodo común a una tupla comparable."""
    if isinstance(center, tuple) and len(center) >= 3:
        return center
    if isinstance(center, list) and len(center) >= 3:
        return (float(center[0]), float(center[1]), float(center[2]))
    return None


def _distance_sq_to_center(pos: Any, center: Any) -> float:
    """Distancia al cuadrado entre un punto y un centro expresado como tupla."""
    center_tuple = _center_to_point(center)
    if pos is None or center_tuple is None:
        return float("inf")
    try:
        dx = float(getattr(pos, "X", 0.0)) - float(center_tuple[0])
        dy = float(getattr(pos, "Y", 0.0)) - float(center_tuple[1])
        dz = float(getattr(pos, "Z", 0.0)) - float(center_tuple[2])
    except Exception:
        return float("inf")
    return dx * dx + dy * dy + dz * dz


def _segment_sort_key(pos: Any, path_points: List[Any]) -> Optional[float]:
    """Calcula una clave de orden estable para un punto relativo a un camino."""
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
    """Resuelve a qué camino pertenece un marker."""
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
    """Resuelve el orden de un marker dentro de su camino lógico."""
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
    """Traduce kind de marker al vocabulario lógico exportable."""
    kind = str(marker.get("kind", "") or "").strip().lower()
    if kind == "start":
        return "inicio"
    if kind == "end":
        return "final"
    return "intermedio_libre"


def _logical_tipo_from_free_point(point: dict) -> str:
    """Obtiene el tipo lógico exportable de un punto libre."""
    return str(point.get("flag", "") or "intermedio_libre").strip().lower()


def _normalize_node_tipo(raw_tipo: str) -> str:
    """Normaliza tipos lógicos al conjunto semántico del export."""
    if raw_tipo == "inicio":
        return "inicio"
    if raw_tipo == "final":
        return "final"
    if raw_tipo in ("bifurcacion", "bifurcación", "intermedio_libre"):
        return "union"
    if raw_tipo == "intermedio_ordenado":
        return "codo"
    return "union"


def _build_node_id(item: dict, path_index: int, counters: dict, node_tipo: str) -> str:
    """Genera IDs semánticos por camino, compatibles con otros exports del sistema."""
    data = item.get("data", {}) or {}
    common_node_id = data.get("common_node_id")
    if common_node_id:
        return str(common_node_id)
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
    """Agrupa los markers por camino lógico."""
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
                "path_key": path_key,
            }
        )
    return grouped


def _build_free_point_groups(
    free_placed_points: List[dict],
) -> Dict[str, List[dict]]:
    """
    Agrupa puntos libres siguiendo el mismo criterio secuencial del otro módulo.

    Si el punto ya trae `path_key`, se respeta. Si no, todos los puntos libres
    caen en un mismo camino lógico `default`, y su conectividad se resuelve por
    el campo `order`.
    """
    grouped: Dict[str, List[dict]] = defaultdict(list)
    for idx, point in enumerate(free_placed_points or [], start=1):
        path_key = str(point.get("path_key") or "default")
        grouped[path_key].append(
            {
                "source": "free_placed_point",
                "data": point,
                "tipo_logico": _logical_tipo_from_free_point(point),
                "sort_key": float(point.get("order", idx - 1) or 0.0),
                "path_idx": None,
                "path_key": path_key,
            }
        )
    return grouped


def _attach_common_node_metadata(
    node_entry: dict,
    common_nodes: List[dict],
    tolerance_mm: float,
) -> None:
    """
    Asocia a un nodo exportado el `common_node_id` más cercano si cae en un cruce.

    Se usa para que el export plano y el export por caminos puedan referenciar
    la misma topología de `common_points`.
    """
    pos = node_entry.get("pos")
    path_key = str(node_entry.get("path_key") or "")
    if pos is None or not common_nodes:
        return

    tol_sq = max(float(tolerance_mm), 0.0) ** 2
    best = None
    best_dist = None

    for common in common_nodes:
        path_keys = [str(k) for k in common.get("path_keys", [])]
        if path_key and path_keys and path_key not in path_keys:
            continue
        center = common.get("center")
        d2 = _distance_sq_to_center(pos, center)
        if d2 > tol_sq:
            continue
        if best_dist is None or d2 < best_dist:
            best_dist = d2
            best = common

    if not best:
        return

    common_node_id = str(best.get("id", ""))
    node_entry["common_node_id"] = common_node_id
    node_entry["es_punto_comun"] = True
    node_entry["common_path_keys"] = list(best.get("path_keys", []))
    node_entry["common_point_count"] = int(best.get("point_count", 0) or 0)


def _build_node_entry(
    node_id: str,
    item: dict,
    path_id: str,
    path_name: str,
    order_index: int,
    common_nodes: List[dict],
    tolerance_mm: float,
) -> dict:
    """Construye un nodo exportado enriquecido con metadatos de camino y cruce."""
    data = item.get("data", {}) or {}
    pos = data.get("pos")
    tipo = _normalize_node_tipo(str(item.get("tipo_logico", "") or ""))
    path_key = str(item.get("path_key") or "")

    node = {
        "id": node_id,
        "tipo": tipo,
        "coordenadas": _point_to_coords(pos),
        "anteriores": [],
        "siguientes": [],
        "anterior": None,
        "path_id": path_id,
        "path_name": path_name,
        "path_key": path_key,
        "path_idx": item.get("path_idx"),
        "element_type": data.get("element_type"),
        "source": item.get("source"),
        "order_index": int(order_index),
        "flag": data.get("flag"),
        "path_key_comun_con": data.get("path_key_comun_con"),
        "es_punto_comun": False,
        "common_node_id": None,
        "common_path_keys": [],
        "common_point_count": 0,
        "pos": pos,
    }
    _attach_common_node_metadata(node, common_nodes, tolerance_mm=tolerance_mm)
    return node


def _finalize_node_entry(node: dict) -> dict:
    """Limpia claves internas no deseadas en el contrato público."""
    node.pop("pos", None)
    return node


def build_nodos_export_data(
    element_markers: List[dict],
    saved_paths: Optional[List[List[Any]]] = None,
    free_placed_points: Optional[List[dict]] = None,
    common_points_topology: Optional[dict] = None,
    common_junctions: Optional[List[dict]] = None,
    tolerance_mm: float = 5.0,
) -> List[dict]:
    """
    Devuelve una lista plana de nodos enriquecidos.

    Cada nodo incluye:
    - `id`, `tipo`, `coordenadas`
    - `anteriores`, `siguientes`, `anterior`
    - metadatos de camino (`path_id`, `path_name`, `path_key`, `path_idx`)
    - metadatos de elemento (`element_type`, `source`, `kind`, `flag`)
    - vínculo con topología común (`common_node_id`, `es_punto_comun`)
    """
    saved_paths = saved_paths or []
    free_placed_points = free_placed_points or []
    common_points_topology = common_points_topology or {}
    common_junctions = common_junctions or []
    common_nodes = list(common_points_topology.get("nodes", []) or [])

    all_groups: Dict[str, List[dict]] = {}
    all_groups.update(_build_path_groups(element_markers or [], saved_paths))
    all_groups.update(_build_free_point_groups(free_placed_points or []))

    nodos: List[dict] = []
    ordered_path_keys = sorted(all_groups.keys())
    for path_index, path_key in enumerate(ordered_path_keys, start=1):
        group = sorted(
            all_groups[path_key],
            key=lambda item: (float(item.get("sort_key", 0.0)), path_key),
        )
        path_id = f"camino_{path_index}"
        path_name = f"Camino {path_index} ({path_key})"
        counters = {
            "inicio": 0,
            "final": 0,
            "codo": 0,
            "union": 0,
        }

        node_ids: List[str] = []
        for item in group:
            node_tipo = _normalize_node_tipo(str(item.get("tipo_logico", "") or ""))
            node_ids.append(_build_node_id(item, path_index, counters, node_tipo))

        path_nodes: List[dict] = []
        for idx, item in enumerate(group):
            node = _build_node_entry(
                node_id=node_ids[idx],
                item=item,
                path_id=path_id,
                path_name=path_name,
                order_index=idx,
                common_nodes=common_nodes,
                tolerance_mm=tolerance_mm,
            )
            if idx > 0:
                node["anteriores"] = [node_ids[idx - 1]]
                node["anterior"] = node_ids[idx - 1]
            if idx < len(node_ids) - 1:
                node["siguientes"] = [node_ids[idx + 1]]
            path_nodes.append(_finalize_node_entry(node))

        nodos.extend(path_nodes)

    if common_junctions:
        junction_by_id = {
            str(jn.get("node_id", "")): jn
            for jn in common_junctions
            if jn.get("node_id")
        }
        for nodo in nodos:
            common_node_id = nodo.get("common_node_id")
            junction = junction_by_id.get(str(common_node_id or ""))
            if not junction:
                continue
            nodo["junction"] = {
                "node_id": str(junction.get("node_id", "")),
                "path_keys": list(junction.get("path_keys", [])),
                "path_count": int(junction.get("path_count", 0) or 0),
                "tipos_punto": list(junction.get("tipos_punto", [])),
                "element_types": list(junction.get("element_types", [])),
                "suggested_element": junction.get("suggested_element"),
            }

    return nodos


def build_optimizer_graph_json(
    element_markers: List[dict],
    saved_paths: Optional[List[List[Any]]] = None,
    free_placed_points: Optional[List[dict]] = None,
    common_points_topology: Optional[dict] = None,
    common_junctions: Optional[List[dict]] = None,
    tolerance_mm: float = 5.0,
    graph_id: Optional[str] = None,
    graph_name: Optional[str] = None,
) -> dict:
    """
    Construye un contenedor tipo grafo para ElementosDefinidos.

    Salida:
    - `caminos`: lista de caminos con nodos y segmentos
    - `nodos`: lista plana equivalente al export simple
    - `common_points_topology` y `common_junctions`
    """
    nodos = build_nodos_export_data(
        element_markers=element_markers,
        saved_paths=saved_paths,
        free_placed_points=free_placed_points,
        common_points_topology=common_points_topology,
        common_junctions=common_junctions,
        tolerance_mm=tolerance_mm,
    )

    grouped: Dict[str, List[dict]] = defaultdict(list)
    for nodo in nodos:
        grouped[str(nodo.get("path_id") or "camino_indefinido")].append(nodo)

    caminos = []
    for path_id in sorted(grouped.keys()):
        path_nodes = sorted(
            grouped[path_id],
            key=lambda node: int(node.get("order_index", 0) or 0),
        )
        if not path_nodes:
            continue

        path_name = path_nodes[0].get("path_name") or path_id
        segmentos = []
        for seg_index in range(len(path_nodes) - 1):
            n1 = path_nodes[seg_index]
            n2 = path_nodes[seg_index + 1]
            segmentos.append(
                {
                    "id": seg_index + 1,
                    "n1_id": n1["id"],
                    "n2_id": n2["id"],
                }
            )

        caminos.append(
            {
                "id": path_id,
                "nombre": str(path_name),
                "path_key": path_nodes[0].get("path_key"),
                "path_idx": path_nodes[0].get("path_idx"),
                "nodos": path_nodes,
                "segmentos": segmentos,
            }
        )

    return {
        "id": graph_id or "elementos_definidos",
        "nombre": graph_name or "Elementos Definidos",
        "nodos": nodos,
        "caminos": caminos,
        "common_points_topology": common_points_topology or {},
        "common_junctions": common_junctions or [],
    }
