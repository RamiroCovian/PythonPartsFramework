# -*- coding: utf-8 -*-
"""
Adapter between polyline_base_lib JSON format and Caminos_Optimos_Lib format.

Translates:
  - Our export (CaminoModel) --> optimizer input JSON
  - Optimizer output (grafo JSON) --> polyline paths for import
"""

from typing import Any, Dict, List, Optional

from .models import SubtipoConducto

# Our export tipo --> Caminos_Optimos_Lib nodo tipo
# _EXPORT_TO_OPTIMIZER = {
#     "inicio": "inicio",
#     "intermedio_obligado": "orden_obligatorio",
#     "intermedio_libre": "orden_libre",
#     "bifurcacion": "orden_obligatorio",
#     "convergencia": "orden_obligatorio",
#     "final": "fin",
# }

_EXPORT_TO_OPTIMIZER = {
    "inicio": "inicio",
    "orden_obligatorio": "orden_obligatorio",
    "orden_libre": "orden_libre",
    "fin": "fin",
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
    """Traduce el dict de ``_build_camino_dict`` al formato de entrada del optimizador.

    Args:
        camino_dict: Dict con clave ``"caminos"`` (lista de caminos), cada uno
            con ``"id"``, ``"tipo"`` y ``"nodos"``. Generado por
            ``PolylineOptimizer._build_camino_dict``.
        mock_config: Overrides opcionales para ``techo``, ``obstaculos``,
            ``configuracion``, etc.

    Returns:
        Dict listo para serializar como JSON de entrada al optimizador.
    """
    if mock_config is None:
        mock_config = {}

    caminos_entrada = camino_dict.get("caminos", [])
    optimizer_caminos: List[Dict[str, Any]] = []
    all_nodos_out: List[Dict[str, Any]] = []   # para calcular techo global

    for camino in caminos_entrada:
        nodos_in = camino.get("nodos", [])
        nodos_out: List[Dict[str, Any]] = []

        for nodo in nodos_in:
            src_tipo = nodo.get("tipo", None)
            dst_tipo = _EXPORT_TO_OPTIMIZER.get(src_tipo, src_tipo)

            coords = nodo.get("coordenadas", [0, 0, 0])
            if isinstance(coords, (list, tuple)) and len(coords) >= 3:
                coords_obj = {"x": coords[0], "y": coords[1], "z": coords[2]}
            elif isinstance(coords, dict):
                coords_obj = coords
            else:
                coords_obj = {"x": 0, "y": 0, "z": 0}

            nodos_out.append({
                "id":          nodo.get("id", ""),
                "tipo":        dst_tipo,
                "coordenadas": coords_obj,
                "anteriores":  nodo.get("anteriores", []),
                "siguientes":  nodo.get("siguientes", []),
            })

        all_nodos_out.extend(nodos_out)
        cam_id = camino.get("id", f"camino-{len(optimizer_caminos)}")
        optimizer_camino: Dict[str, Any] = {
            "id":     cam_id,
            "nombre": cam_id,
            "nodos":  nodos_out,
        }
        cam_config = mock_config.get("configuracion", None)
        if cam_config:
            optimizer_camino["configuracion"] = cam_config
        optimizer_caminos.append(optimizer_camino)

    print(f"[Adapter] build_optimizer_input: {len(optimizer_caminos)} camino(s)")

    techo = mock_config.get("techo", None)
    if not techo:
        techo = _auto_techo_from_nodos(all_nodos_out)

    proyecto_id = camino_dict.get("id", "proyecto")
    return {
        "id":               proyecto_id,
        "nombre":           proyecto_id,
        "techo":            techo,
        "subdivisiones_is": mock_config.get("subdivisiones_is", []),
        "tubos_is":         mock_config.get("tubos_is", []),
        "caminos":          optimizer_caminos,
        "obstaculos":       mock_config.get("obstaculos", []),
        "configuracion": {
            "subtipo_tuberia":     SubtipoConducto.from_tipo_instalacion(camino_dict.get("tipo", "")).value,
            "estrategia_colision": mock_config.get("estrategia_colision", ["saltar"]),
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

    Usa directamente la altura Z de los nodos sin aplicar ningún offset.
    Adds a generous margin in XY around the polyline so the optimizer has room
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
    z_val = min(zs)  - 150 if zs else 2650

    return [{
        "id": "techo_auto",
        "vertices": [
            {"x": x_min, "y": y_min, "z": z_val},
            {"x": x_max, "y": y_min, "z": z_val},
            {"x": x_max, "y": y_max, "z": z_val},
            {"x": x_min, "y": y_max, "z": z_val},
        ],
    }]
