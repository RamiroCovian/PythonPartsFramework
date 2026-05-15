# -*- coding: utf-8 -*-
"""
Adapter between polyline_base_lib JSON format and Caminos_Optimos_Lib format.

Translates:
  - Our export (CaminoModel) --> optimizer input JSON
  - Optimizer output (grafo JSON) --> polyline paths for import
"""

from typing import Any, Dict, List, Optional

# Our export tipo --> Caminos_Optimos_Lib nodo tipo
_EXPORT_TO_OPTIMIZER = {
    "inicio": "inicio",
    "intermedio_obligado": "orden_obligatorio",
    "intermedio_libre": "orden_libre",
    "bifurcacion": "orden_obligatorio",
    "convergencia": "orden_obligatorio",
    "final": "fin",
}

# Caminos_Optimos_Lib grafo output tipo --> our import tipo
_GRAFO_TO_IMPORT = {
    "inicio": "inicio",
    "final": "final",
    "obligatorio": "intermedio_obligado",
    "libre": "intermedio_libre",
    "codo": "intermedio_libre",
    "union": "intermedio_libre",
    "conector": "intermedio_libre",
}


def build_optimizer_input(
    camino_dict: Dict[str, Any],
    mock_config: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Translate our export CaminoModel dict into the optimizer's input format.

    Args:
        camino_dict: Result of ``CaminoModel.to_dict()`` -- has ``id``, ``tipo``,
            ``nodos`` where each nodo has ``coordenadas`` as ``[x, y, z]``.
        mock_config: Optional overrides for ``techo``, ``obstaculos``,
            ``configuracion``, etc.  When *None*, defaults are derived from
            the polyline bounding box.

    Returns:
        A dict ready to be serialized as the optimizer input JSON.
    """
    if mock_config is None:
        mock_config = {}

    nodos_in = camino_dict.get("nodos", [])
    nodos_out = []

    for nodo in nodos_in:
        src_tipo = nodo.get("tipo", "intermedio_obligado")
        dst_tipo = _EXPORT_TO_OPTIMIZER.get(src_tipo, "orden_obligatorio")

        coords = nodo.get("coordenadas", [0, 0, 0])
        if isinstance(coords, (list, tuple)) and len(coords) >= 3:
            coords_obj = {"x": coords[0], "y": coords[1], "z": coords[2]}
        elif isinstance(coords, dict):
            coords_obj = coords
        else:
            coords_obj = {"x": 0, "y": 0, "z": 0}

        nodos_out.append({
            "id": nodo.get("id", ""),
            "tipo": dst_tipo,
            "coordenadas": coords_obj,
            "anteriores": nodo.get("anteriores", []),
            "siguientes": nodo.get("siguientes", []),
        })

    techo = mock_config.get("techo")
    if not techo:
        techo = _auto_techo_from_nodos(nodos_out)

    optimizer_camino = {
        "id": camino_dict.get("id", "camino_0"),
        "nombre": camino_dict.get("id", "camino_0"),
        "nodos": nodos_out,
    }

    cam_config = mock_config.get("configuracion")
    if cam_config:
        optimizer_camino["configuracion"] = cam_config

    return {
        "id": camino_dict.get("id", "proyecto"),
        "nombre": camino_dict.get("id", "proyecto"),
        "techo": techo,
        "subdivisiones_is": mock_config.get("subdivisiones_is", []),
        "tubos_is": mock_config.get("tubos_is", []),
        "caminos": [optimizer_camino],
        "obstaculos": mock_config.get("obstaculos", []),
        "configuracion": cam_config or {
            "subtipo_tuberia": "extraccion_impulsion",
            "estrategia_colision": ["saltar"],
        },
    }


def parse_optimizer_output(grafo: Dict[str, Any]) -> List[List[List[float]]]:
    """Extract polyline paths from the optimizer's grafo JSON output.

    The grafo has ``caminos[].nodos[]`` where each nodo has
    ``coordenadas: {x, y, z}`` and they are already in traversal order
    (linked via anteriores/siguientes).

    Returns:
        List of paths, each path a list of ``[x, y, z]`` points.
    """
    paths: List[List[List[float]]] = []

    for camino in grafo.get("caminos", []):
        nodos = camino.get("nodos", [])
        if not nodos:
            continue

        points: List[List[float]] = []
        for nodo in nodos:
            coords = nodo.get("coordenadas", {})
            if isinstance(coords, dict):
                x = float(coords.get("x", 0))
                y = float(coords.get("y", 0))
                z = float(coords.get("z", 0))
            elif isinstance(coords, (list, tuple)) and len(coords) >= 3:
                x, y, z = float(coords[0]), float(coords[1]), float(coords[2])
            else:
                continue
            points.append([x, y, z])

        if len(points) >= 2:
            paths.append(points)

    return paths


def _auto_techo_from_nodos(nodos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Derive a flat rectangular techo from the bounding box of nodo coordinates.

    Adds a generous margin around the polyline so the optimizer has room
    to manoeuvre.
    """
    xs, ys, zs = [], [], []
    for n in nodos:
        c = n.get("coordenadas", {})
        if isinstance(c, dict):
            xs.append(c.get("x", 0))
            ys.append(c.get("y", 0))
            zs.append(c.get("z", 0))

    if not xs:
        return [{"id": "techo_mock", "vertices": [
            {"x": 0, "y": 0, "z": 2800},
            {"x": 10000, "y": 0, "z": 2800},
            {"x": 10000, "y": 6000, "z": 2800},
            {"x": 0, "y": 6000, "z": 2800},
        ]}]

    margin = 2000
    x_min = min(xs) - margin
    x_max = max(xs) + margin
    y_min = min(ys) - margin
    y_max = max(ys) + margin
    z_val = min(zs) - 150 if zs else 2800

    return [{
        "id": "techo_auto",
        "vertices": [
            {"x": x_min, "y": y_min, "z": z_val},
            {"x": x_max, "y": y_min, "z": z_val},
            {"x": x_max, "y": y_max, "z": z_val},
            {"x": x_min, "y": y_max, "z": z_val},
        ],
    }]
