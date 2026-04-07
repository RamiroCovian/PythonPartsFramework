# -*- coding: utf-8 -*-
"""
Handlers para puntos indicativos sin objetos definidos.
Eventos: añadir punto (1019), finalizar (1020).
Al finalizar (1020), los puntos se pueden convertir en polilíneas guardadas
(saved_paths + saved_segments) para el flujo normal de fontaneria.
"""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any, Optional

from . import palette
from .common_points import detect_common_point_groups
from .optimizer_graph import (
    _build_node_id,
    _normalize_node_tipo,
    build_optimizer_graph_json,
)

try:
    import NemAll_Python_Geometry as AllplanGeo
    from NemAll_Python_Utility import PythonUtility
except Exception:
    AllplanGeo = None
    PythonUtility = None


def _get_build_ele(intr: Any) -> Any:
    """Devuelve build_ele asociado al interactor."""
    return getattr(getattr(intr, "script_object", None), "build_ele", None)


def _ensure_puntos_no_definidos(intr: Any) -> list:
    """Asegura que script_object tenga puntos_no_definidos y lo devuelve."""
    so = getattr(intr, "script_object", None)
    if so is not None:
        if not hasattr(so, "puntos_no_definidos") or not isinstance(
            getattr(so, "puntos_no_definidos", None), list
        ):
            so.puntos_no_definidos = []
        return so.puntos_no_definidos
    return []


def _try_save_state(intr: Any) -> None:
    """Intenta guardar el estado del script."""
    try:
        so = getattr(intr, "script_object", None)
        if so is not None and hasattr(so, "_save_state_to_build_ele"):
            so._save_state_to_build_ele()
    except Exception:
        pass


def _try_print_prompt(intr: Any) -> None:
    """Intenta actualizar el mensaje al usuario."""
    try:
        if hasattr(intr, "_print_prompt"):
            intr._print_prompt()
    except Exception:
        pass


def _try_draw_preview(intr: Any, pos: Any = None) -> None:
    """Fuerza redibujado de la previsualización."""
    try:
        coord_input = getattr(intr, "coord_input", None)
        current_point = getattr(intr, "current_point", None)
        if (
            coord_input
            and current_point is not None
            and getattr(coord_input, "GetCurrentPoint", None)
        ):
            cp = coord_input.GetCurrentPoint(current_point)
            if cp is not None and getattr(cp, "GetPoint", None):
                intr._draw_preview(cp.GetPoint())
                return
        intr._draw_preview(pos)
    except Exception:
        pass


def _write_optimizer_graph_json(script_object: Any, optimizer_graph: dict) -> Optional[str]:
    """Escribe el JSON de optimización dentro de ElementosNoDefinidos."""
    try:
        base_dir = Path(__file__).resolve().parent
        output_dir = base_dir / "optimizer_output"
        output_dir.mkdir(parents=True, exist_ok=True)

        file_name = getattr(script_object, "optimizer_graph_file_name", None)
        if not file_name:
            file_name = "optimizer_graph.json"

        output_path = output_dir / str(file_name)
        with output_path.open("w", encoding="utf-8") as fh:
            json.dump(optimizer_graph, fh, ensure_ascii=False, indent=2)

        return str(output_path)
    except Exception as ex:
        print(f"[OPTIMIZER GRAPH] Error escribiendo JSON: {ex}")
        return None


def _distance_sq(a: Any, b: Any) -> float:
    """Distancia cuadrada entre dos puntos con X/Y/Z."""
    try:
        dx = float(getattr(a, "X", 0.0)) - float(getattr(b, "X", 0.0))
        dy = float(getattr(a, "Y", 0.0)) - float(getattr(b, "Y", 0.0))
        dz = float(getattr(a, "Z", 0.0)) - float(getattr(b, "Z", 0.0))
        return dx * dx + dy * dy + dz * dz
    except Exception:
        return float("inf")


def _distance_sq_xy(a: Any, b: Any) -> float:
    """Distancia cuadrada en XY (ignora Z para detección en planta)."""
    try:
        dx = float(getattr(a, "X", 0.0)) - float(getattr(b, "X", 0.0))
        dy = float(getattr(a, "Y", 0.0)) - float(getattr(b, "Y", 0.0))
        return dx * dx + dy * dy
    except Exception:
        return float("inf")


def _find_common_anchor(
    puntos: list,
    raw_pnt: Any,
    current_path_key: str,
    tolerance_mm: float,
) -> tuple[Optional[dict], Optional[float], Optional[str]]:
    """
    Busca un punto existente de OTRO camino dentro de tolerancia para anclar.
    Devuelve:
    - punto ancla elegido o None,
    - distancia XY (mm) al punto más cercano de otro camino (si existe),
    - path_key del más cercano (si existe).
    """
    if not puntos or raw_pnt is None:
        return None, None, None
    tol_sq = max(float(tolerance_mm), 0.0) ** 2
    best = None
    best_d2 = tol_sq + 1.0
    nearest_d2 = None
    nearest_path = None
    for p in puntos:
        pos = p.get("pos")
        if pos is None or not hasattr(pos, "X"):
            continue
        other_path = str(p.get("path_key", "default"))
        if other_path == str(current_path_key):
            continue
        d2 = _distance_sq_xy(raw_pnt, pos)
        if nearest_d2 is None or d2 < nearest_d2:
            nearest_d2 = d2
            nearest_path = other_path
        if d2 <= tol_sq and d2 < best_d2:
            best_d2 = d2
            best = p
    nearest_mm = (nearest_d2**0.5) if nearest_d2 is not None else None
    return best, nearest_mm, nearest_path


def _next_common_node_id(script_object: Any) -> str:
    """Genera un id incremental para nodo común (CP-*)."""
    try:
        current = int(getattr(script_object, "_common_point_seq", 0))
    except Exception:
        current = 0
    current += 1
    setattr(script_object, "_common_point_seq", current)
    return f"CP-{current}"


def _ensure_anchor_common_node_id(script_object: Any, anchor: dict) -> str:
    """Asegura que el punto ancla tenga common_node_id y lo devuelve."""
    existing = anchor.get("common_node_id")
    if existing:
        return str(existing)
    node_id = _next_common_node_id(script_object)
    anchor["common_node_id"] = node_id
    anchor["es_punto_comun"] = True
    return node_id


def _build_common_topology(
    puntos: list,
    tolerance_mm: float,
) -> dict:
    """
    Construye topología de puntos comunes:
    - nodes: [{id, path_keys, point_count}]
    - edges: [{a, b, via_node}]
    """
    nodes = []
    node_ids_seen = set()

    # 1) Nodos explícitos por common_node_id (cuando hubo snap)
    grouped_by_id = {}
    for p in puntos:
        node_id = p.get("common_node_id")
        if not node_id:
            continue
        node_id = str(node_id)
        grouped_by_id.setdefault(node_id, []).append(p)

    explicit_nodes = []
    for node_id, items in grouped_by_id.items():
        path_keys = sorted({str(it.get("path_key", "default")) for it in items})
        if len(path_keys) < 2:
            continue
        xs = [float(getattr(it.get("pos"), "X", 0.0)) for it in items if it.get("pos")]
        ys = [float(getattr(it.get("pos"), "Y", 0.0)) for it in items if it.get("pos")]
        zs = [float(getattr(it.get("pos"), "Z", 0.0)) for it in items if it.get("pos")]
        center = (
            (sum(xs) / len(xs)) if xs else 0.0,
            (sum(ys) / len(ys)) if ys else 0.0,
            (sum(zs) / len(zs)) if zs else 0.0,
        )
        node = {
            "id": node_id,
            "path_keys": path_keys,
            "point_count": len(items),
            "center": center,
        }
        nodes.append(node)
        explicit_nodes.append(node)
        node_ids_seen.add(node_id)

    # Utilidad para evitar duplicar nodos AUTO que representan el mismo cruce
    def _is_duplicate_of_explicit(group_paths: list, group_center: tuple) -> bool:
        for en in explicit_nodes:
            en_paths = en.get("path_keys", [])
            if sorted(en_paths) != sorted(group_paths):
                continue
            en_center = en.get("center", (0.0, 0.0, 0.0))
            dx = float(group_center[0]) - float(en_center[0])
            dy = float(group_center[1]) - float(en_center[1])
            dz = float(group_center[2]) - float(en_center[2])
            if (dx * dx + dy * dy + dz * dz) <= (float(tolerance_mm) ** 2):
                return True
        return False

    # 2) Fallback por proximidad para cruces no capturados por snap explícito
    groups = detect_common_point_groups(
        puntos,
        tolerance_mm=tolerance_mm,
        min_distinct_paths=2,
    )
    for idx, group in enumerate(groups, start=1):
        group_paths = list(group.get("path_keys", []))
        group_center = tuple(group.get("center", (0.0, 0.0, 0.0)))
        if _is_duplicate_of_explicit(group_paths, group_center):
            continue
        node_id = f"CP-AUTO-{idx}"
        if node_id in node_ids_seen:
            continue
        node_ids_seen.add(node_id)
        nodes.append(
            {
                "id": node_id,
                "path_keys": group_paths,
                "point_count": len(group.get("indices", [])),
                "center": group_center,
            }
        )

    # 3) Aristas entre caminos por nodo común
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
                edges.append(
                    {
                        "a": a,
                        "b": b,
                        "via_node": str(node.get("id")),
                    }
                )

    # 4) Adyacencia por camino (lectura rápida para fases siguientes)
    adjacency = {}
    for edge in edges:
        a = str(edge.get("a"))
        b = str(edge.get("b"))
        adjacency.setdefault(a, set()).add(b)
        adjacency.setdefault(b, set()).add(a)
    adjacency_sorted = {
        k: sorted(list(v))
        for k, v in adjacency.items()
    }

    return {
        "node_count": len(nodes),
        "edge_count": len(edges),
        "nodes": nodes,
        "edges": edges,
        "adjacency": adjacency_sorted,
    }


def _build_common_junctions(
    puntos: list,
    topo: dict,
) -> list:
    """
    Genera lista de junctions consumibles directamente por el generador de Agua.

    Cada junction es un dict con:
    - node_id: str (CP-1, CP-2, ...)
    - x, y, z: coordenadas del nodo común
    - path_keys: caminos que se cruzan ahí
    - path_count: número de caminos
    - tipos_punto: tipos de punto involucrados (inicio, final, bifurcación, etc.)
    - suggested_element: sugerencia de elemento a generar (t_sortida, colze, paso, etc.)
    """
    junctions = []
    nodes = topo.get("nodes", [])

    node_to_puntos = {}
    for p in puntos:
        nid = p.get("common_node_id")
        if nid:
            node_to_puntos.setdefault(str(nid), []).append(p)

    for node in nodes:
        node_id = str(node.get("id", ""))
        path_keys = list(node.get("path_keys", []))
        center = node.get("center", (0.0, 0.0, 0.0))

        related = node_to_puntos.get(node_id, [])
        tipos_punto = sorted(
            {str(p.get("tipo", "")) for p in related if p.get("tipo")}
        )

        path_count = len(path_keys)
        suggested = _suggest_element(path_count, tipos_punto)

        junctions.append(
            {
                "node_id": node_id,
                "x": float(center[0]) if len(center) > 0 else 0.0,
                "y": float(center[1]) if len(center) > 1 else 0.0,
                "z": float(center[2]) if len(center) > 2 else 0.0,
                "path_keys": path_keys,
                "path_count": path_count,
                "tipos_punto": tipos_punto,
                "suggested_element": suggested,
            }
        )

    return junctions


def build_nodos_export_data(puntos: list) -> list:
    """
    Convierte ``puntos_no_definidos`` al formato exportado consumible por otros módulos.

    Salida por nodo:
    - id
    - tipo
    - coordenadas {X, Y, Z}
    - anteriores
    - siguientes
    - orden
    - tipo_camino
    - color_id
    - path_key
    - es_punto_comun
    - common_node_id
    - path_key_comun_con
    """
    if not puntos:
        return []

    by_key: dict[str, list] = defaultdict(list)
    for p in puntos:
        path_key = str(p.get("path_key") or "default")
        by_key[path_key].append(p)

    nodos = []
    for path_index, path_key in enumerate(sorted(by_key.keys()), start=1):
        group = by_key[path_key]
        group.sort(key=lambda item: int(item.get("orden", 0)))

        counters = {
            "inicio": 0,
            "final": 0,
            "codo": 0,
            "union": 0,
        }
        ids_grupo = []
        for punto in group:
            node_tipo = _normalize_node_tipo(punto)
            ids_grupo.append(_build_node_id(punto, path_index, counters, node_tipo))

        for idx, punto in enumerate(group):
            pos = punto.get("pos")
            coords = {
                "X": float(getattr(pos, "X", 0.0)) if pos is not None else 0.0,
                "Y": float(getattr(pos, "Y", 0.0)) if pos is not None else 0.0,
                "Z": float(getattr(pos, "Z", 0.0)) if pos is not None else 0.0,
            }
            nodos.append(
                {
                    "id": ids_grupo[idx],
                    "tipo": punto.get("tipo"),
                    "coordenadas": coords,
                    "anteriores": [ids_grupo[idx - 1]] if idx > 0 else [],
                    "siguientes": (
                        [ids_grupo[idx + 1]] if idx < len(ids_grupo) - 1 else []
                    ),
                    "orden": int(punto.get("orden", 0)),
                    "tipo_camino": punto.get("tipo_camino"),
                    "color_id": punto.get("color_id"),
                    "path_key": punto.get("path_key"),
                    "es_punto_comun": bool(punto.get("es_punto_comun", False)),
                    "common_node_id": punto.get("common_node_id"),
                    "path_key_comun_con": punto.get("path_key_comun_con"),
                }
            )

    return nodos


def _suggest_element(path_count: int, tipos_punto: list) -> str:
    """
    Sugiere qué tipo de elemento generar en un nodo común.
    Heurística basada en cuántos caminos se cruzan y qué tipos de punto hay.
    """
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


def _pos_to_point3d(pos: Any) -> Any:
    if pos is None:
        return None
    try:
        if hasattr(pos, "X") and hasattr(pos, "Y") and hasattr(pos, "Z"):
            if AllplanGeo is None:
                return pos
            return AllplanGeo.Point3D(
                float(getattr(pos, "X", 0.0)),
                float(getattr(pos, "Y", 0.0)),
                float(getattr(pos, "Z", 0.0)),
            )
        if isinstance(pos, dict):
            if AllplanGeo is None:
                return pos
            return AllplanGeo.Point3D(
                float(pos.get("X", pos.get("x", 0.0))),
                float(pos.get("Y", pos.get("y", 0.0))),
                float(pos.get("Z", pos.get("z", 0.0))),
            )
    except Exception:
        return None
    return None


def materialize_puntos_no_definidos_to_saved_paths(
    script_object: Any,
    intr: Any,
) -> int:
    """
    Agrupa puntos_no_definidos por path_key, ordena por 'orden' y añade cada grupo
    con al menos 2 vértices a script_object.saved_paths, creando segmentos por
    defecto vía PolylineInteractor._create_default_segments_for_new_path.

    Vacía puntos_no_definidos si se añadió al menos una polilínea.

    Returns:
        Número de polilíneas nuevas añadidas.
    """
    print(
        "[PUNTOS NO DEFINIDOS] Volcando indicativos a saved_paths (evento 1020)..."
    )
    puntos = getattr(script_object, "puntos_no_definidos", None) or []
    if not puntos:
        print("[PUNTOS NO DEFINIDOS] No hay puntos para volcar.")
        return 0

    if not hasattr(script_object, "saved_paths") or not isinstance(
        getattr(script_object, "saved_paths", None), list
    ):
        script_object.saved_paths = []
    if not hasattr(script_object, "saved_segments") or not isinstance(
        getattr(script_object, "saved_segments", None), list
    ):
        script_object.saved_segments = []

    interactor = intr
    if interactor is None:
        interactor = getattr(script_object, "script_object_interactor", None)

    by_key: dict[str, list] = defaultdict(list)
    for p in puntos:
        key = str(p.get("path_key") or "")
        by_key[key].append(p)

    added = 0
    for path_key in sorted(by_key.keys()):
        group = by_key[path_key]
        group.sort(key=lambda x: int(x.get("orden", 0)))
        verts = []
        for item in group:
            pt = _pos_to_point3d(item.get("pos"))
            if pt is not None:
                verts.append(pt)
        if len(verts) < 2:
            print(
                f"[PUNTOS NO DEFINIDOS] path_key={path_key!r}: "
                f"{len(verts)} vértice(s) válidos; se necesitan ≥2 para polilínea — omitido."
            )
            continue

        script_object.saved_paths.append(verts)
        path_idx = len(script_object.saved_paths) - 1
        crea_seg = getattr(interactor, "_create_default_segments_for_new_path", None)
        if callable(crea_seg):
            try:
                crea_seg(path_idx)
            except Exception as ex:
                print(
                    f"[PUNTOS NO DEFINIDOS] Error creando segmentos para path_idx={path_idx}: {ex}"
                )
        else:
            print(
                "[PUNTOS NO DEFINIDOS] Interactor sin _create_default_segments_for_new_path; "
                "solo se añadieron vértices a saved_paths."
            )

        added += 1
        print(
            f"[PUNTOS NO DEFINIDOS] Polilínea #{path_idx} desde puntos no definidos: "
            f"path_key={path_key!r}, vértices={len(verts)}"
        )

    if added:
        script_object.puntos_no_definidos = []
        print(
            f"[PUNTOS NO DEFINIDOS] Materialización: {added} polilínea(s) añadida(s) a "
            "saved_paths; lista de puntos indicativos vaciada."
        )
        try:
            n_saved = len(getattr(script_object, "saved_paths", []) or [])
            if PythonUtility is not None:
                PythonUtility.ShowMessageBox(
                    f"Se generaron {added} polilínea(s) desde puntos no definidos.\n\n"
                    f"Total de polilíneas guardadas en sesión: {n_saved}.\n\n"
                    "Pulse «Crear en documento» (evento 1003) para crear tubos en el proyecto.",
                    PythonUtility.MB_OK,
                )
        except Exception:
            pass

    return added


def on_anadir_punto_no_definido(
    script_object: Any,
    intr: Any,
) -> bool:
    """
    Activa modo continuo para añadir puntos no definidos.
    Evento 1019.
    """
    intr.next_click_adds_punto_no_definido = True
    intr.script_object = script_object
    if not hasattr(script_object, "puntos_no_definidos") or not isinstance(
        getattr(script_object, "puntos_no_definidos", None), list
    ):
        script_object.puntos_no_definidos = []
    _try_print_prompt(intr)
    _try_save_state(intr)
    print("[PUNTOS NO DEFINIDOS] Modo añadir activo (1019). Clics sucesivos añaden puntos hasta 1020.")
    return True


def on_finalizar_puntos_no_definidos(
    script_object: Any,
    intr: Optional[Any],
) -> bool:
    """
    Finaliza el modo de añadir puntos no definidos (evento 1020).

    Genera topología de puntos comunes y junctions. El volcado a ``saved_paths``
    lo ejecuta ``fontaneria._on_finalizar_puntos_no_definidos`` (materialización).
    """
    if intr:
        intr.next_click_adds_punto_no_definido = False
    print("[PUNTOS NO DEFINIDOS] Modo añadir finalizado (1020).")
    try:
        puntos = getattr(script_object, "puntos_no_definidos", None) or []
        build_ele = getattr(script_object, "build_ele", None)
        common_tol_mm = palette.get_common_points_tolerance_mm(
            build_ele, default=5.0
        )
        topo = _build_common_topology(puntos, tolerance_mm=common_tol_mm)
        script_object.common_points_topology = topo
        print(
            "[PUNTOS COMUNES] Topología generada: "
            f"nodos={topo.get('node_count', 0)}, conexiones={topo.get('edge_count', 0)}"
        )
        for node in topo.get("nodes", []):
            print(
                "[PUNTOS COMUNES] Nodo "
                f"{node.get('id')}: paths={node.get('path_keys', [])}, "
                f"points={node.get('point_count', 0)}"
            )
        adjacency = topo.get("adjacency", {}) or {}
        for path_key in sorted(adjacency.keys()):
            print(
                "[PUNTOS COMUNES] Camino "
                f"{path_key} conecta con {adjacency.get(path_key, [])}"
            )

        junctions = _build_common_junctions(puntos, topo)
        script_object.common_junctions = junctions
        print(
            f"[PUNTOS COMUNES] Junctions generadas: {len(junctions)}"
        )
        for jn in junctions:
            print(
                f"[JUNCTION] {jn.get('node_id')}: "
                f"pos=({jn.get('x', 0):.1f}, {jn.get('y', 0):.1f}, {jn.get('z', 0):.1f}), "
                f"caminos={jn.get('path_keys', [])}, "
                f"tipos={jn.get('tipos_punto', [])}"
            )
        script_object.nodos_export_data = build_nodos_export_data(puntos)
    except Exception as ex:
        print(f"[PUNTOS COMUNES] Error generando topología: {ex}")
    _try_save_state(intr)
    if intr and getattr(intr, "_draw_preview", None):
        try:
            intr._draw_preview(None)
        except Exception:
            pass
    return True


def handle_click_add_punto_no_definido(
    intr: Any,
    script_object: Any,
    raw_pnt: Any,
) -> bool:
    """
    Gestiona el clic para añadir un punto no definido.
    Lee tipo de punto y color desde la paleta.
    """
    build_ele = getattr(script_object, "build_ele", None)
    tipo_punto = palette.get_tipo_punto_orden(build_ele)
    tipo_camino = palette.get_tipo_camino(build_ele)
    color_id = palette.get_color_puntos(build_ele, default=6)
    path_key = palette.get_path_key_puntos(
        build_ele,
        color_id=color_id,
        tipo_camino=tipo_camino,
    )

    puntos = getattr(script_object, "puntos_no_definidos", None)
    if puntos is None:
        script_object.puntos_no_definidos = []
        puntos = script_object.puntos_no_definidos

    detection_enabled = palette.get_common_points_detection_enabled(
        build_ele, default=True
    )
    common_tol_mm = palette.get_common_points_tolerance_mm(build_ele, default=5.0)

    anchor = None
    nearest_mm = None
    nearest_path = None
    if detection_enabled:
        anchor, nearest_mm, nearest_path = _find_common_anchor(
            puntos=puntos,
            raw_pnt=raw_pnt,
            current_path_key=path_key,
            tolerance_mm=common_tol_mm,
        )

    if anchor is not None:
        anchor_pos = anchor.get("pos")
        common_node_id = _ensure_anchor_common_node_id(script_object, anchor)
        if AllplanGeo is not None and anchor_pos is not None:
            pos = AllplanGeo.Point3D(anchor_pos.X, anchor_pos.Y, anchor_pos.Z)
        else:
            pos = anchor_pos
        if PythonUtility is not None:
            PythonUtility.Log(
                f"[PUNTOS COMUNES] Anclado a punto existente de camino "
                f"{anchor.get('path_key', 'unknown')}"
            )
        print(
            "[PUNTOS COMUNES] Snap aplicado: "
            f"nuevo_path={path_key} -> anclado_con={anchor.get('path_key', 'unknown')}, "
            f"node_id={common_node_id}"
        )
    else:
        if AllplanGeo is not None:
            pos = AllplanGeo.Point3D(raw_pnt.X, raw_pnt.Y, raw_pnt.Z)
        else:
            pos = raw_pnt
        if detection_enabled:
            print(
                "[PUNTOS COMUNES] Sin snap: "
                f"path={path_key}, tolerancia={common_tol_mm}mm, puntos_previos={len(puntos)}, "
                f"mas_cercano={nearest_mm if nearest_mm is not None else 'n/a'}mm"
                f"{', path=' + str(nearest_path) if nearest_path else ''}"
            )
        else:
            print(
                "[PUNTOS COMUNES] Detección desactivada en paleta. "
                f"Path actual={path_key}"
            )

    puntos.append(
        {
            "pos": pos,
            "tipo": tipo_punto,
            "color_id": color_id,
            "path_key": path_key,
            "tipo_camino": int(tipo_camino),
            "es_punto_comun": anchor is not None,
            "common_node_id": (
                common_node_id if anchor is not None else None
            ),
            "path_key_comun_con": (
                str(anchor.get("path_key")) if anchor is not None else None
            ),
            "orden": len(puntos),
        }
    )
    print(
        "[PUNTOS NO DEFINIDOS] Punto añadido: "
        f"tipo={tipo_punto}, color_id={color_id}, path_key={path_key}, total={len(puntos)}"
    )
    _try_save_state(intr)
    _try_draw_preview(intr, raw_pnt)
    return True
