# -*- coding: utf-8 -*-
"""
Adaptador desde puntos no definidos al formato de entrada de Caminos_Optimos_Lib.

Este módulo NO genera el JSON final de optimización completo. Su objetivo es
preparar la estructura parcial de caminos/nodos que luego podrá integrarse con:

- techo
- subdivisiones_is
- tubos_is
- obstaculos
- configuracion
"""
from __future__ import annotations

from collections import defaultdict
from typing import Any, Dict, List, Optional


def _point_to_coords(pos: Any) -> Dict[str, float]:
    if pos is None:
        return {"x": 0.0, "y": 0.0, "z": 0.0}
    if isinstance(pos, dict):
        return {
            "x": float(pos.get("x", pos.get("X", 0.0))),
            "y": float(pos.get("y", pos.get("Y", 0.0))),
            "z": float(pos.get("z", pos.get("Z", 0.0))),
        }
    return {
        "x": float(getattr(pos, "X", 0.0)),
        "y": float(getattr(pos, "Y", 0.0)),
        "z": float(getattr(pos, "Z", 0.0)),
    }


def _map_tipo(tipo_original: str) -> str:
    tipo = str(tipo_original or "").strip().lower()
    if tipo == "inicio":
        return "inicio"
    if tipo == "final":
        return "fin"
    if tipo == "intermedio_libre":
        return "orden_libre"
    if tipo in ("intermedio_ordenado", "bifurcación", "bifurcacion"):
        return "orden_obligatorio"
    return "orden_libre"


def _build_node_id(path_index: int, tipo: str, counters: dict) -> str:
    if tipo == "inicio":
        return f"A{path_index}"
    if tipo == "fin":
        return f"B{path_index}"
    if tipo == "orden_obligatorio":
        counters["obligatorio"] += 1
        return f"O{path_index}_{counters['obligatorio']}"

    counters["libre"] += 1
    return f"L{path_index}_{counters['libre']}"


def build_caminos_optimos_caminos_data(puntos: List[dict]) -> List[dict]:
    """
    Convierte ``puntos_no_definidos`` a la estructura parcial que espera
    Caminos_Optimos_Lib en modo multi-camino:

    [
      {
        "id": "camino_1",
        "nombre": "...",
        "nodos": [...]
      }
    ]
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
            "obligatorio": 0,
            "libre": 0,
        }
        nodos = []
        obligatorios_ids = []
        inicio_id = None
        fin_id = None

        for point in group:
            tipo_original = str(point.get("tipo", "") or "")
            tipo = _map_tipo(tipo_original)
            node_id = _build_node_id(path_index, tipo, counters)

            if tipo == "inicio":
                inicio_id = node_id
            elif tipo == "fin":
                fin_id = node_id
            elif tipo == "orden_obligatorio":
                obligatorios_ids.append(node_id)

            nodos.append(
                {
                    "id": node_id,
                    "tipo": tipo,
                    "coordenadas": _point_to_coords(point.get("pos")),
                    "anteriores": [],
                    "siguientes": [],
                    "tipo_original": tipo_original,
                    "path_key": path_key,
                    "color_id": point.get("color_id"),
                    "common_node_id": point.get("common_node_id"),
                }
            )

        # Encadenar solo inicio -> obligatorios -> fin.
        chain_ids = []
        if inicio_id:
            chain_ids.append(inicio_id)
        chain_ids.extend(obligatorios_ids)
        if fin_id:
            chain_ids.append(fin_id)

        nodes_by_id = {n["id"]: n for n in nodos}
        for idx, node_id in enumerate(chain_ids):
            node = nodes_by_id.get(node_id)
            if node is None:
                continue
            if idx > 0:
                node["anteriores"] = [chain_ids[idx - 1]]
            if idx < len(chain_ids) - 1:
                node["siguientes"] = [chain_ids[idx + 1]]

        caminos.append(
            {
                "id": f"camino_{path_index}",
                "nombre": f"Camino {path_index} ({path_key})",
                "nodos": nodos,
            }
        )

    return caminos


def build_caminos_optimos_partial_input(
    puntos: List[dict],
    project_id: Optional[str] = None,
    project_name: Optional[str] = None,
) -> dict:
    """
    Retorna una estructura parcial lista para ser completada por el generador
    de JSON de Caminos_Optimos_Lib.
    """
    return {
        "id": project_id or "elementos_no_definidos",
        "nombre": project_name or "Elementos No Definidos",
        "caminos": build_caminos_optimos_caminos_data(puntos),
    }
