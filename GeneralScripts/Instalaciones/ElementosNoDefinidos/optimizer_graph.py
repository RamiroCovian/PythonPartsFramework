# -*- coding: utf-8 -*-
"""
Construcción de JSON tipo grafo para optimización a partir de puntos no definidos.

Contrato objetivo:
{
  "id": "...",
  "nombre": "...",
  "caminos": [
    {
      "id": "...",
      "nombre": "...",
      "nodos": [...],
      "segmentos": [...]
    }
  ]
}
"""
from __future__ import annotations

from collections import defaultdict
from typing import Any, Dict, List, Optional


def _point_to_coords(pos: Any) -> Dict[str, float]:
    if pos is None:
        return {"x": 0.0, "y": 0.0, "z": 0.0}
    return {
        "x": float(getattr(pos, "X", 0.0)),
        "y": float(getattr(pos, "Y", 0.0)),
        "z": float(getattr(pos, "Z", 0.0)),
    }


def _extract_is(point: dict, path_key: str) -> Optional[str]:
    for key in ("IS", "is", "instalacion_id", "installation_id"):
        value = point.get(key)
        if value not in (None, ""):
            return str(value)
    return str(path_key) if path_key else None


def _normalize_node_tipo(point: dict) -> str:
    raw_tipo = str(point.get("tipo", "") or "").strip().lower()
    if raw_tipo == "inicio":
        return "inicio"
    if raw_tipo == "final":
        return "final"
    if point.get("common_node_id") or point.get("es_punto_comun"):
        return "union"
    if raw_tipo in ("bifurcación", "bifurcacion"):
        return "union"
    if raw_tipo == "intermedio_ordenado":
        return "codo"
    if raw_tipo == "intermedio_libre":
        return "union"
    return "union"


def _build_node_id(
    point: dict,
    path_index: int,
    counters: dict,
    node_tipo: str,
) -> str:
    common_node_id = point.get("common_node_id")
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


def build_optimizer_graph_json(
    puntos: List[dict],
    graph_id: Optional[str] = None,
    graph_name: Optional[str] = None,
) -> dict:
    """
    Convierte ``puntos_no_definidos`` en un JSON tipo grafo como el ejemplo
    ``test_output_grafo.json``.

    Supuestos actuales:
    - cada ``path_key`` define un camino;
    - el orden del camino es ``orden`` ascendente;
    - ``IS`` se toma del punto si existe; si no, se reutiliza ``path_key``.
    """
    grouped: dict[str, list] = defaultdict(list)
    for point in puntos or []:
        path_key = str(point.get("path_key") or "default")
        grouped[path_key].append(point)

    caminos = []
    for path_index, path_key in enumerate(sorted(grouped.keys()), start=1):
        group = sorted(grouped[path_key], key=lambda item: int(item.get("orden", 0)))
        if len(group) < 2:
            continue

        counters = {
            "inicio": 0,
            "final": 0,
            "codo": 0,
            "union": 0,
        }
        nodos = []
        node_ids = []

        for point in group:
            node_tipo = _normalize_node_tipo(point)
            node_id = _build_node_id(point, path_index, counters, node_tipo)
            node_ids.append(node_id)
            nodos.append(
                {
                    "id": node_id,
                    "tipo": node_tipo,
                    "coordenadas": _point_to_coords(point.get("pos")),
                    "IS": _extract_is(point, path_key),
                    "anteriores": [],
                    "siguientes": [],
                }
            )

        for idx, nodo in enumerate(nodos):
            if idx > 0:
                nodo["anteriores"] = [node_ids[idx - 1]]
            if idx < len(nodos) - 1:
                nodo["siguientes"] = [node_ids[idx + 1]]

        segmentos = []
        for seg_index in range(len(nodos) - 1):
            n1 = nodos[seg_index]
            n2 = nodos[seg_index + 1]
            segment_is = n1.get("IS") if n1.get("IS") == n2.get("IS") else None
            segmentos.append(
                {
                    "id": seg_index + 1,
                    "n1_id": n1["id"],
                    "n2_id": n2["id"],
                    "IS": segment_is,
                }
            )

        caminos.append(
            {
                "id": f"camino_{path_index}",
                "nombre": f"Camino {path_index} ({path_key})",
                "nodos": nodos,
                "segmentos": segmentos,
            }
        )

    return {
        "id": graph_id or "elementos_no_definidos",
        "nombre": graph_name or "Elementos No Definidos",
        "caminos": caminos,
    }
