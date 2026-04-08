# -*- coding: utf-8 -*-
"""
Handlers para eventos de elementos definidos (1015, 1016, 1017, 1018) y lógica de clic.
Cualquier script (fontaneria, etc.) puede llamar a estas funciones pasando el
interactor y/o script_object en lugar de duplicar la lógica.
"""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any, Optional, List, Tuple

from . import catalogo
from . import palette
from .common_points import (
    build_common_junctions,
    build_common_points_topology,
    detect_common_point_groups,
)
from .optimizer_graph import (
    build_nodos_export_data,
    build_optimizer_graph_json,
)

try:
    import NemAll_Python_Geometry as AllplanGeo
    from NemAll_Python_Utility import PythonUtility
    from NemAll_Python_BasisElements import AllplanBasisElements
    from NemAll_Python_BaseElements import AllplanBaseElements
except Exception:
    AllplanGeo = None
    PythonUtility = None
    AllplanBasisElements = None
    AllplanBaseElements = None


def _get_build_ele(intr: Any) -> Any:
    """Devuelve el objeto build_ele asociado al interactor (vía script_object), o None si no existe."""
    return getattr(getattr(intr, "script_object", None), "build_ele", None)


def _get_element_markers(intr: Any) -> list:
    """Obtiene la lista de element_markers desde el interactor o su script_object; si no existe, devuelve []."""
    markers = getattr(intr, "element_markers", None)
    if markers is not None:
        return markers
    so = getattr(intr, "script_object", None)
    if so is not None:
        return getattr(so, "element_markers", []) or []
    return []


def _ensure_element_markers_list(intr: Any) -> list:
    """Asegura que intr (o su script_object) tenga una lista element_markers válida y la devuelve."""
    so = getattr(intr, "script_object", None)
    if so is not None:
        if not hasattr(so, "element_markers") or not isinstance(
            getattr(so, "element_markers", None), list
        ):
            so.element_markers = []
        intr.element_markers = so.element_markers
        return intr.element_markers
    if not hasattr(intr, "element_markers") or not isinstance(
        getattr(intr, "element_markers", None), list
    ):
        intr.element_markers = []
    return intr.element_markers


def _get_active_path_points(intr: Any) -> list:
    """Obtiene la polilínea activa del interactor (método interno, puntos del interactor o saved_paths)."""
    getter = getattr(intr, "_get_active_path_points", None)
    if callable(getter):
        return getter() or []
    pts = getattr(intr, "points", None) or []
    if pts and len(pts) >= 2:
        return pts
    so = getattr(intr, "script_object", None)
    if so and getattr(so, "saved_paths", None) and so.saved_paths:
        return so.saved_paths[0]
    return []


def _dist_sq_points(a: Any, b: Any) -> float:
    """Calcula la distancia euclídea al cuadrado entre dos puntos 3D con atributos X, Y, Z."""
    try:
        ax, ay, az = getattr(a, "X", 0.0), getattr(a, "Y", 0.0), getattr(a, "Z", 0.0)
        bx, by, bz = getattr(b, "X", 0.0), getattr(b, "Y", 0.0), getattr(b, "Z", 0.0)
    except Exception:
        return float("inf")
    dx, dy, dz = ax - bx, ay - by, az - bz
    return dx * dx + dy * dy + dz * dz


def _dist_sq_points_xy(a: Any, b: Any) -> float:
    """Calcula la distancia al cuadrado en planta entre dos puntos 3D."""
    try:
        ax, ay = getattr(a, "X", 0.0), getattr(a, "Y", 0.0)
        bx, by = getattr(b, "X", 0.0), getattr(b, "Y", 0.0)
    except Exception:
        return float("inf")
    dx, dy = ax - bx, ay - by
    return dx * dx + dy * dy


def _next_common_node_id(script_object: Any) -> str:
    """Genera un id incremental para nodos comunes de elementos definidos."""
    try:
        current = int(getattr(script_object, "_defined_elements_common_point_seq", 0))
    except Exception:
        current = 0
    current += 1
    setattr(script_object, "_defined_elements_common_point_seq", current)
    return f"CP-{current}"


def _ensure_anchor_common_node_id(script_object: Any, anchor: dict) -> str:
    """Asegura que el punto ancla tenga `common_node_id` y lo devuelve."""
    existing = anchor.get("common_node_id")
    if existing:
        return str(existing)
    node_id = _next_common_node_id(script_object)
    anchor["common_node_id"] = node_id
    anchor["es_punto_comun"] = True
    return node_id


def _find_common_anchor(
    puntos: List[dict],
    raw_pnt: Any,
    current_path_key: str,
    tolerance_mm: float,
) -> tuple[Optional[dict], Optional[float], Optional[str]]:
    """
    Busca un punto libre existente de otro camino dentro de tolerancia XY.

    Devuelve:
    - punto ancla o None
    - distancia XY al punto más cercano de otro camino
    - path_key del punto más cercano
    """
    if not puntos or raw_pnt is None:
        return None, None, None
    tol_sq = max(float(tolerance_mm), 0.0) ** 2
    best = None
    best_d2 = tol_sq + 1.0
    nearest_d2 = None
    nearest_path = None
    for point in puntos:
        pos = point.get("pos")
        if pos is None or not hasattr(pos, "X"):
            continue
        other_path = str(point.get("path_key") or "default")
        if other_path == str(current_path_key):
            continue
        d2 = _dist_sq_points_xy(raw_pnt, pos)
        if nearest_d2 is None or d2 < nearest_d2:
            nearest_d2 = d2
            nearest_path = other_path
        if d2 <= tol_sq and d2 < best_d2:
            best_d2 = d2
            best = point
    nearest_mm = (nearest_d2 ** 0.5) if nearest_d2 is not None else None
    return best, nearest_mm, nearest_path


def _next_free_path_key(script_object: Any) -> str:
    """Genera el siguiente `path_key` lógico para free_placed_points."""
    try:
        current = int(getattr(script_object, "_defined_elements_free_path_seq", 0))
    except Exception:
        current = 0
    current += 1
    setattr(script_object, "_defined_elements_free_path_seq", current)
    return f"defined_path_{current}"


def _resolve_free_point_path_key(script_object: Any, flag: str) -> str:
    """
    Resuelve el camino lógico del nuevo punto libre.

    - `inicio` abre un camino nuevo
    - el resto continúa el camino actual
    - si aún no hay camino activo, se crea uno
    """
    current = getattr(script_object, "_defined_elements_current_path_key", None)
    normalized_flag = str(flag or "").strip().lower()
    if normalized_flag == "inicio" or not current:
        current = _next_free_path_key(script_object)
        setattr(script_object, "_defined_elements_current_path_key", current)
    return str(current)


def _close_free_point_path_if_needed(script_object: Any, flag: str) -> None:
    """Cierra el camino activo cuando el punto agregado es un final lógico."""
    if str(flag or "").strip().lower() == "final":
        setattr(script_object, "_defined_elements_current_path_key", None)


def _detect_common_points_from_paths(
    paths: List[List[Any]],
    tolerance_mm: float = 1.0,
) -> List[dict]:
    """Detecta puntos comunes entre varias polilíneas, agrupando puntos cercanos según una tolerancia."""
    if not paths or tolerance_mm <= 0:
        return []
    flat: List[Tuple[int, int, Any]] = []
    for path_idx, pts in enumerate(paths):
        if not pts:
            continue
        for pt_idx, p in enumerate(pts):
            flat.append((path_idx, pt_idx, p))
    if len(flat) < 2:
        return []
    tol_sq = tolerance_mm * tolerance_mm
    used = [False] * len(flat)
    groups: List[dict] = []
    for i, (pi_path, pi_idx, pi_point) in enumerate(flat):
        if used[i]:
            continue
        group_indices = [i]
        used[i] = True
        for j in range(i + 1, len(flat)):
            if used[j]:
                continue
            pj_path, pj_idx, pj_point = flat[j]
            if _dist_sq_points(pi_point, pj_point) <= tol_sq:
                used[j] = True
                group_indices.append(j)
        if len(group_indices) < 2:
            continue
        path_ids = {flat[k][0] for k in group_indices}
        if len(path_ids) < 2:
            continue
        sx = sy = sz = 0.0
        members: List[dict] = []
        for k in group_indices:
            path_idx, pt_idx, p = flat[k]
            px, py, pz = (
                getattr(p, "X", 0.0),
                getattr(p, "Y", 0.0),
                getattr(p, "Z", 0.0),
            )
            sx += px
            sy += py
            sz += pz
            members.append({"path_idx": path_idx, "pt_idx": pt_idx, "point": p})
        n = float(len(group_indices))
        mx, my, mz = sx / n, sy / n, sz / n
        if AllplanGeo is not None:
            pos = AllplanGeo.Point3D(mx, my, mz)
        else:
            first_point = flat[group_indices[0]][2]
            try:
                pos = first_point.__class__(mx, my, mz)
            except Exception:
                pos = {"X": mx, "Y": my, "Z": mz}
        groups.append({"pos": pos, "members": members})
    return groups


def detect_common_user_points_between_paths(
    intr: Any,
    tolerance_mm: float = 1.0,
) -> List[dict]:
    """Detecta puntos comunes entre los paths guardados en intr.saved_paths, usando una tolerancia en mm."""
    paths = getattr(intr, "saved_paths", None) or []
    return _detect_common_points_from_paths(paths, tolerance_mm)


def _build_common_topology_from_free_points(
    free_placed_points: List[dict],
    tolerance_mm: float,
) -> dict:
    """Construye topología de puntos comunes a partir de `free_placed_points`."""
    nodes = []
    node_ids_seen = set()
    grouped_by_id = defaultdict(list)
    for point in free_placed_points or []:
        node_id = point.get("common_node_id")
        if node_id:
            grouped_by_id[str(node_id)].append(point)

    explicit_nodes = []
    for node_id, items in grouped_by_id.items():
        path_keys = sorted({str(it.get("path_key") or "default") for it in items})
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

    def _is_duplicate_of_explicit(group_paths: List[str], group_center: tuple) -> bool:
        tol_sq = max(float(tolerance_mm), 0.0) ** 2
        for explicit in explicit_nodes:
            if sorted(explicit.get("path_keys", [])) != sorted(group_paths):
                continue
            center = explicit.get("center", (0.0, 0.0, 0.0))
            dx = float(group_center[0]) - float(center[0])
            dy = float(group_center[1]) - float(center[1])
            dz = float(group_center[2]) - float(center[2])
            if (dx * dx + dy * dy + dz * dz) <= tol_sq:
                return True
        return False

    detect_input = [
        {
            "pos": point.get("pos"),
            "path_key": str(point.get("path_key") or "default"),
        }
        for point in (free_placed_points or [])
    ]
    groups = detect_common_point_groups(
        detect_input,
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

    edge_set = set()
    edges = []
    adjacency = defaultdict(set)
    for node in nodes:
        path_keys = list(node.get("path_keys", []))
        for i in range(len(path_keys)):
            for j in range(i + 1, len(path_keys)):
                a = str(path_keys[i])
                b = str(path_keys[j])
                key = tuple(sorted((a, b)) + [str(node.get("id"))])
                if key in edge_set:
                    continue
                edge_set.add(key)
                edges.append({"a": a, "b": b, "via_node": str(node.get("id"))})
                adjacency[a].add(b)
                adjacency[b].add(a)

    return {
        "node_count": len(nodes),
        "edge_count": len(edges),
        "nodes": nodes,
        "edges": edges,
        "adjacency": {k: sorted(list(v)) for k, v in adjacency.items()},
        "points": [
            {
                "path_key": str(point.get("path_key") or "default"),
                "common_node_id": point.get("common_node_id"),
                "es_punto_comun": bool(point.get("es_punto_comun", False)),
            }
            for point in (free_placed_points or [])
        ],
    }


def build_common_user_points_data(
    intr: Any,
    tolerance_mm: float = 1.0,
) -> dict:
    """
    Construye y guarda en el script/interactor la topología de puntos comunes y
    las junctions derivadas, igual que en ElementosNoDefinidos.
    """
    paths = getattr(intr, "saved_paths", None) or []
    script_object = getattr(intr, "script_object", None)
    free_placed_points = []
    if script_object is not None:
        free_placed_points = getattr(script_object, "free_placed_points", None) or []
    element_markers = getattr(intr, "element_markers", None)
    if element_markers is None and script_object is not None:
        element_markers = getattr(script_object, "element_markers", None)
    element_markers = element_markers or []

    if free_placed_points:
        topology = _build_common_topology_from_free_points(
            free_placed_points,
            tolerance_mm=tolerance_mm,
        )
        junctions = []
    else:
        topology = build_common_points_topology(
            saved_paths=paths,
            tolerance_mm=tolerance_mm,
        )
        junctions = build_common_junctions(
            saved_paths=paths,
            topology=topology,
            element_markers=element_markers,
            tolerance_mm=tolerance_mm,
        )

    if script_object is not None:
        script_object.common_points_topology = topology
        script_object.common_junctions = junctions

    intr.common_points_topology = topology
    intr.common_junctions = junctions

    return {
        "topology": topology,
        "junctions": junctions,
    }


def build_defined_elements_export_data(
    intr: Any,
    tolerance_mm: float = 1.0,
) -> dict:
    """
    Construye y guarda el export completo de ElementosDefinidos.

    El resultado incluye:
    - `nodos`: lista plana enriquecida
    - `caminos`: agrupación por camino con segmentos
    - `common_points_topology`
    - `common_junctions`
    """
    script_object = getattr(intr, "script_object", None)
    paths = getattr(script_object, "saved_paths", None) or getattr(intr, "saved_paths", None) or []
    element_markers = getattr(intr, "element_markers", None)
    if element_markers is None and script_object is not None:
        element_markers = getattr(script_object, "element_markers", None)
    element_markers = element_markers or []

    free_placed_points = []
    if script_object is not None:
        free_placed_points = getattr(script_object, "free_placed_points", None) or []

    common_data = build_common_user_points_data(intr, tolerance_mm=tolerance_mm)
    topology = common_data.get("topology", {}) or {}
    junctions = common_data.get("junctions", []) or []

    nodos = build_nodos_export_data(
        element_markers=element_markers,
        saved_paths=paths,
        free_placed_points=free_placed_points,
        common_points_topology=topology,
        common_junctions=junctions,
        tolerance_mm=tolerance_mm,
    )
    optimizer_graph = build_optimizer_graph_json(
        element_markers=element_markers,
        saved_paths=paths,
        free_placed_points=free_placed_points,
        common_points_topology=topology,
        common_junctions=junctions,
        tolerance_mm=tolerance_mm,
    )

    if script_object is not None:
        script_object.nodos_export_data = nodos
        script_object.optimizer_graph_data = optimizer_graph
        output_path = _write_optimizer_graph_json(script_object, optimizer_graph)
        if output_path:
            script_object.optimizer_graph_output_path = output_path
            print(f"[ED][OPTIMIZER GRAPH] JSON escrito en: {output_path}")

    intr.nodos_export_data = nodos
    intr.optimizer_graph_data = optimizer_graph

    return {
        "nodos": nodos,
        "optimizer_graph": optimizer_graph,
        "topology": topology,
        "junctions": junctions,
    }


def _write_optimizer_graph_json(script_object: Any, optimizer_graph: dict) -> Optional[str]:
    """
    Escribe el JSON de debug del export de ElementosDefinidos.

    Se guarda en `ElementosDefinidos/optimizer_output` para poder comparar la
    salida del módulo con otros exports del proyecto.
    """
    try:
        custom_output_dir = getattr(
            script_object,
            "defined_elements_optimizer_graph_output_dir",
            None,
        )
        if custom_output_dir:
            output_dir = Path(custom_output_dir)
        else:
            base_dir = Path(__file__).resolve().parent
            output_dir = base_dir / "optimizer_output"
        output_dir.mkdir(parents=True, exist_ok=True)

        file_name = getattr(
            script_object,
            "defined_elements_optimizer_graph_file_name",
            None,
        )
        if not file_name:
            file_name = "optimizer_graph_defined_elements.json"

        output_path = output_dir / str(file_name)
        with output_path.open("w", encoding="utf-8") as fh:
            json.dump(optimizer_graph, fh, ensure_ascii=False, indent=2)

        return str(output_path)
    except Exception as ex:
        print(f"[ED][OPTIMIZER GRAPH] Error escribiendo JSON: {ex}")
        return None


def _try_print_prompt(intr: Any) -> None:
    """Intenta llamar intr._print_prompt() para actualizar el mensaje al usuario, ignorando errores."""
    try:
        if hasattr(intr, "_print_prompt"):
            intr._print_prompt()
    except Exception:
        pass


def _try_save_state(intr: Any) -> None:
    """Intenta guardar el estado del script llamando a script_object._save_state_to_build_ele()."""
    try:
        so = getattr(intr, "script_object", None)
        if so is not None and hasattr(so, "_save_state_to_build_ele"):
            so._save_state_to_build_ele()
    except Exception:
        pass


def _try_save_state_script(script_object: Any) -> None:
    """Versión auxiliar que guarda el estado recibiendo directamente el script_object."""
    try:
        if script_object is not None and hasattr(
            script_object, "_save_state_to_build_ele"
        ):
            script_object._save_state_to_build_ele()
    except Exception:
        pass


def _try_refresh_palette(script_object: Any) -> None:
    """Intenta forzar la actualización visual de la paleta tras cambiar `build_ele`."""
    try:
        if script_object is None:
            return
        interactor = getattr(script_object, "script_object_interactor", None)
        if interactor is not None and hasattr(interactor, "_pending_palette_refresh"):
            interactor._pending_palette_refresh = True
        if (
            hasattr(script_object, "palette_service")
            and getattr(script_object, "palette_service", None)
            and hasattr(script_object, "build_ele")
        ):
            print("[ED] Refrescando paleta con palette_service.update_palette")
            script_object.palette_service.update_palette(
                script_object.build_ele,
                show_palette=True,
            )
            return

        if getattr(script_object, "_ed_palette_sync_in_progress", False):
            return

        build_ele = getattr(script_object, "build_ele", None)
        modify = getattr(script_object, "modify_element_property", None)
        ctrl_prop_util = getattr(
            script_object,
            "control_props_util",
            getattr(script_object, "ctrl_prop_util", None),
        )
        if build_ele is None or not callable(modify):
            return

        script_object._ed_palette_sync_in_progress = True
        try:
            print("[ED] Refrescando paleta con fallback modify_element_property")
            values_to_sync = []
            for name in ("RotX", "RotY", "RotZ", "ElementRotX", "ElementRotY", "ElementRotZ"):
                param = getattr(build_ele, name, None)
                if param is None:
                    continue
                value = getattr(param, "value", param)
                values_to_sync.append((name, value))
                try:
                    modify(name, value)
                except Exception:
                    pass

            # Fallback extra para entornos donde la paleta no repinta al tocar
            # únicamente build_ele/modify_element_property.
            if ctrl_prop_util is not None:
                pushed = False
                for method_name in (
                    "set_value",
                    "set_property_value",
                    "change_value",
                    "update_value",
                ):
                    method = getattr(ctrl_prop_util, method_name, None)
                    if not callable(method):
                        continue
                    try:
                        for name, value in values_to_sync:
                            method(name, value)
                        print(
                            f"[ED] Refrescando paleta con control_props_util.{method_name}"
                        )
                        pushed = True
                        break
                    except Exception:
                        continue

                if pushed:
                    for refresh_name in (
                        "update_palette",
                        "refresh_palette",
                        "update",
                        "refresh",
                    ):
                        refresh_method = getattr(ctrl_prop_util, refresh_name, None)
                        if not callable(refresh_method):
                            continue
                        try:
                            refresh_method()
                            print(
                                f"[ED] Ejecutando control_props_util.{refresh_name}()"
                            )
                            break
                        except Exception:
                            continue
                elif not getattr(script_object, "_ed_logged_ctrl_prop_methods", False):
                    try:
                        method_names = sorted(
                            name
                            for name in dir(ctrl_prop_util)
                            if callable(getattr(ctrl_prop_util, name, None))
                            and not name.startswith("_")
                        )
                        print(
                            "[ED] Métodos disponibles en control_props_util: "
                            + ", ".join(method_names[:40])
                        )
                        script_object._ed_logged_ctrl_prop_methods = True
                    except Exception:
                        pass
        finally:
            script_object._ed_palette_sync_in_progress = False
    except Exception as ex:
        print(f"[ED] No se pudo actualizar paleta: {ex}")


def _try_draw_preview_after_add(intr: Any, pos: Any) -> None:
    """Fuerza un redibujado de la previsualización después de añadir un elemento o marcador."""
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


def start_element_point_capture(intr: Any, instalacion: str = "AGUA") -> bool:
    """Activa/desactiva el modo de captura de punto para elementos definidos y muestra un mensaje de ayuda."""
    if getattr(intr, "element_point_capture_mode", False):
        intr.element_point_capture_mode = False
        _try_print_prompt(intr)
        return True
    intr.element_point_capture_mode = True
    if PythonUtility:
        PythonUtility.ShowMessageBox(
            "Haz clic en el dibujo sobre la polilínea donde quieres el elemento.\n"
            "Después pulsa 'Agregar elemento'.",
            PythonUtility.MB_OK,
        )
    return True


def handle_element_point_capture_click(
    intr: Any,
    mouse_msg: int,
    raw_pnt: Any,
) -> bool:
    """Maneja el clic del usuario en modo de captura de punto y guarda el punto seleccionado en el interactor."""
    if mouse_msg != 1:
        return False
    if AllplanGeo is not None:
        intr.element_selected_point = AllplanGeo.Point3D(
            raw_pnt.X, raw_pnt.Y, raw_pnt.Z
        )
    else:
        intr.element_selected_point = raw_pnt
    intr.element_point_capture_mode = False
    _try_print_prompt(intr)
    return True


def add_defined_element_marker(intr: Any, instalacion: str = "AGUA") -> bool:
    """Añade un marcador de elemento definido (inicio, final o libre) según la configuración de la paleta."""
    build_ele = _get_build_ele(intr)
    if build_ele is None and PythonUtility:
        PythonUtility.ShowMessageBox(
            "No hay paleta (build_ele) asociada.",
            PythonUtility.MB_OK,
        )
        return False
    mode = palette.get_element_point_mode(build_ele)
    kind = "start" if mode == 0 else ("end" if mode == 1 else "free")
    funcion_seleccionada = (
        "inicio" if mode == 0 else ("final" if mode == 1 else "intermedio_libre")
    )
    element_type, radius = palette.get_defined_element_settings(build_ele, instalacion)
    ok, msg = catalogo.validar_ubicacion_elemento(
        instalacion, element_type, funcion_seleccionada
    )
    if not ok and PythonUtility:
        PythonUtility.ShowMessageBox(msg or "Ubicación no válida.", PythonUtility.MB_OK)
        return False
    if kind == "free":
        if getattr(intr, "element_selected_point", None) is None:
            intr.next_click_adds_intermediate_element = True
            return True
        if AllplanGeo is not None:
            p = intr.element_selected_point
            pos = AllplanGeo.Point3D(p.X, p.Y, p.Z)
        else:
            pos = intr.element_selected_point
        path_idx, pt_idx = None, None
    else:
        pts = _get_active_path_points(intr)
        if not pts or len(pts) < 2:
            if PythonUtility:
                PythonUtility.ShowMessageBox(
                    "No hay polilínea válida guardada (al menos 2 puntos). Guarda la polilínea primero.",
                    PythonUtility.MB_OK,
                )
            return False
        if kind == "start":
            p0 = pts[0]
        else:
            p0 = pts[-1]
        pos = AllplanGeo.Point3D(p0.X, p0.Y, p0.Z) if AllplanGeo else p0
        path_idx = 0
        pt_idx = 0 if kind == "start" else (len(pts) - 1)
    z_abs = palette.get_element_z_abs(build_ele)
    marker = {
        "kind": kind,
        "pos": pos,
        "radius": radius,
        "element_type": element_type,
        "z_abs": z_abs,
        "path_idx": path_idx,
        "pt_idx": pt_idx,
    }
    element_markers = _ensure_element_markers_list(intr)
    element_markers.append(marker)
    intr.element_selected_point = None
    try:
        build_defined_elements_export_data(intr, tolerance_mm=5.0)
    except Exception as ex:
        print(f"[ED][EXPORT] Error actualizando export tras marker: {ex}")
    _try_save_state(intr)
    _try_draw_preview_after_add(intr, pos)
    return True


def add_intermediate_element_at_point(
    intr: Any,
    raw_pnt: Any,
    instalacion: str = "AGUA",
) -> None:
    """Añade un marcador de elemento definido de tipo intermedio_libre en la posición indicada por raw_pnt."""
    build_ele = _get_build_ele(intr)
    element_type, radius = palette.get_defined_element_settings(build_ele, instalacion)
    ok, msg = catalogo.validar_ubicacion_elemento(
        instalacion, element_type, "intermedio_libre"
    )
    if not ok and PythonUtility:
        PythonUtility.ShowMessageBox(
            msg or "Este elemento no puede situarse en puntos intermedios.",
            PythonUtility.MB_OK,
        )
        return
    if AllplanGeo is not None:
        pos = AllplanGeo.Point3D(raw_pnt.X, raw_pnt.Y, raw_pnt.Z)
    else:
        pos = raw_pnt
    marker = {
        "kind": "free",
        "pos": pos,
        "radius": radius,
        "element_type": element_type,
        "path_idx": None,
        "pt_idx": None,
    }
    element_markers = _ensure_element_markers_list(intr)
    element_markers.append(marker)
    try:
        build_defined_elements_export_data(intr, tolerance_mm=5.0)
    except Exception as ex:
        print(f"[ED][EXPORT] Error actualizando export tras intermedio: {ex}")


def on_anadir_punto_libre(
    script_object: Any,
    intr: Any,
    instalacion: str = "AGUA",
) -> bool:
    """Prepara el interactor y el script_object para iniciar el modo de colocación de puntos libres."""
    intr.next_click_adds_free_point = True
    intr.free_point_dragging = False
    intr.free_point_drag_index = None
    intr.script_object = script_object
    if not hasattr(script_object, "free_placed_points") or not isinstance(
        getattr(script_object, "free_placed_points", None), list
    ):
        script_object.free_placed_points = []
    else:
        script_object.free_placed_points = (
            getattr(script_object, "free_placed_points", []) or []
        )
    if not script_object.free_placed_points:
        setattr(script_object, "_defined_elements_current_path_key", None)
    _try_print_prompt(intr)
    _try_save_state_script(script_object)
    return True


def on_finalizar_puntos_libres(
    script_object: Any,
    intr: Optional[Any],
    create_callback: Any,
) -> bool:
    """Finaliza el modo de puntos libres, llama al callback de creación y actualiza la previsualización."""
    if intr:
        intr.free_point_dragging = False
        intr.free_point_drag_index = None
        intr.free_point_selected_index = None
        try:
            build_defined_elements_export_data(intr, tolerance_mm=5.0)
        except Exception as ex:
            print(f"[ED][EXPORT] Error generando export previo a crear puntos libres: {ex}")
    if callable(create_callback):
        create_callback(intr.coord_input if intr else None)
    setattr(script_object, "_defined_elements_current_path_key", None)
    _try_save_state_script(script_object)
    if intr and getattr(intr, "_draw_preview", None):
        try:
            cp = getattr(intr, "current_point", None)
            if (
                cp
                and getattr(intr, "coord_input", None)
                and getattr(intr.coord_input, "GetCurrentPoint", None)
            ):
                pt = intr.coord_input.GetCurrentPoint(cp)
                if pt and getattr(pt, "GetPoint", None):
                    intr._draw_preview(pt.GetPoint())
                else:
                    intr._draw_preview(None)
            else:
                intr._draw_preview(None)
        except Exception:
            pass
    return True


def handle_click_add_free_point(
    intr: Any,
    script_object: Any,
    raw_pnt: Any,
    instalacion: str = "AGUA",
) -> bool:
    """Gestiona cada clic al añadir un punto libre, validando la ubicación y guardando posición y rotación."""
    build_ele = getattr(script_object, "build_ele", None)
    flag = palette.get_free_point_type_flag(
        build_ele,
        instalacion,
    )
    element_type, _ = palette.get_defined_element_settings(
        build_ele,
        instalacion,
    )
    ok, msg = catalogo.validar_ubicacion_elemento(instalacion, element_type, flag)
    if not ok and PythonUtility:
        PythonUtility.ShowMessageBox(msg or "Ubicación no válida.", PythonUtility.MB_OK)
        _try_print_prompt(intr)
        return True
    free_list = getattr(script_object, "free_placed_points", None)
    if free_list is None:
        script_object.free_placed_points = []
        free_list = script_object.free_placed_points
    order = len(free_list)
    path_key = _resolve_free_point_path_key(script_object, flag)

    detection_enabled = bool(
        getattr(script_object, "defined_elements_common_points_enabled", True)
    )
    common_tol_mm = float(
        getattr(script_object, "defined_elements_common_points_tolerance_mm", 5.0)
        or 5.0
    )
    anchor = None
    nearest_mm = None
    nearest_path = None
    common_node_id = None
    if detection_enabled:
        anchor, nearest_mm, nearest_path = _find_common_anchor(
            puntos=free_list,
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
        print(
            "[ED][PUNTOS COMUNES] Snap aplicado: "
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
                "[ED][PUNTOS COMUNES] Sin snap: "
                f"path={path_key}, tolerancia={common_tol_mm}mm, puntos_previos={len(free_list)}, "
                f"mas_cercano={nearest_mm if nearest_mm is not None else 'n/a'}mm"
                f"{', path=' + str(nearest_path) if nearest_path else ''}"
            )

    # Rotación inicial del punto libre según la paleta (RotX, RotY, RotZ)
    rot_x = rot_y = rot_z = 0.0
    if build_ele is not None:
        try:
            for name, key in (("RotX", "rot_x"), ("RotY", "rot_y"), ("RotZ", "rot_z")):
                param = getattr(build_ele, name, None)
                if param is None:
                    continue
                raw_val = getattr(param, "value", param)
                try:
                    val = float(raw_val or 0.0)
                except Exception:
                    val = 0.0
                if key == "rot_x":
                    rot_x = val
                elif key == "rot_y":
                    rot_y = val
                elif key == "rot_z":
                    rot_z = val
        except Exception:
            rot_x = rot_y = rot_z = 0.0

    free_list.append(
        {
            "pos": pos,
            "flag": flag,
            "element_type": element_type,
            "order": order,
            "path_key": path_key,
            "es_punto_comun": anchor is not None,
            "common_node_id": common_node_id if anchor is not None else None,
            "path_key_comun_con": (
                str(anchor.get("path_key")) if anchor is not None else None
            ),
            "rot_x": rot_x,
            "rot_y": rot_y,
            "rot_z": rot_z,
        }
    )
    _close_free_point_path_if_needed(script_object, flag)
    _try_save_state_script(script_object)
    from .editing import get_index_to_select_after_add

    idx = get_index_to_select_after_add(free_list)
    if idx >= 0:
        intr.free_point_selected_index = idx
    try:
        build_defined_elements_export_data(intr, tolerance_mm=5.0)
    except Exception as ex:
        print(f"[ED][EXPORT] Error actualizando export tras punto libre: {ex}")
    return True


def apply_free_point_rotation_to_palette(script_object: Any, index: int) -> None:
    """
    Carga en la paleta (RotX, RotY, RotZ) la rotación almacenada en free_placed_points[index].
    Si no existe rotación guardada, usa 0.0.
    Pensado para ser llamado al seleccionar un punto libre (p. ej. en un interactor).
    """
    if script_object is None or index is None or index < 0:
        return
    free_list = getattr(script_object, "free_placed_points", None) or []
    if index >= len(free_list):
        return
    build_ele = getattr(script_object, "build_ele", None)
    if build_ele is None:
        return
    fp = free_list[index]

    def _set_angle_in_palette(name: str, value: float) -> None:
        try:
            param = getattr(build_ele, name, None)
            if param is None or not hasattr(param, "value"):
                return
            param.value = float(value)
        except Exception:
            pass

    rot_x = fp.get("rot_x", 0.0)
    rot_y = fp.get("rot_y", 0.0)
    rot_z = fp.get("rot_z", 0.0)
    _set_angle_in_palette("RotX", rot_x)
    _set_angle_in_palette("RotY", rot_y)
    _set_angle_in_palette("RotZ", rot_z)
    _try_refresh_palette(script_object)


def update_free_point_rotation_from_palette(script_object: Any, index: int) -> None:
    """
    Actualiza free_placed_points[index].rot_x/y/z leyendo los valores actuales de la paleta
    (RotX, RotY, RotZ). Pensado para ser llamado cuando el usuario modifica la rotación
    en la paleta para el punto libre actualmente seleccionado.
    """
    if script_object is None or index is None or index < 0:
        return
    free_list = getattr(script_object, "free_placed_points", None) or []
    if index >= len(free_list):
        return
    build_ele = getattr(script_object, "build_ele", None)
    if build_ele is None:
        return

    def _get_angle_from_palette(name: str) -> float:
        try:
            param = getattr(build_ele, name, None)
            if param is None:
                return 0.0
            raw = getattr(param, "value", param)
            return float(raw or 0.0)
        except Exception:
            return 0.0

    fp = free_list[index]
    fp["rot_x"] = _get_angle_from_palette("RotX")
    fp["rot_y"] = _get_angle_from_palette("RotY")
    fp["rot_z"] = _get_angle_from_palette("RotZ")
    free_list[index] = fp
    script_object.free_placed_points = free_list
    _try_save_state_script(script_object)


def create_free_point_rotation_label(
    script_object: Any,
    index: int,
    dx: float = -50.0,
    dy: float = 50.0,
) -> List[Any]:
    """
    Crea (y devuelve) una etiqueta de texto 2D sutil con la rotación del punto libre
    en free_placed_points[index]. No la dibuja; el interactor debe pasarla a DrawElementPreview.

    La etiqueta muestra: "RotX=.. RotY=.. RotZ=.." y se coloca cerca del punto con
    desplazamiento (dx, dy) en el plano XY.
    """
    if (
        AllplanGeo is None
        or AllplanBasisElements is None
        or AllplanBaseElements is None
        or script_object is None
        or index is None
        or index < 0
    ):
        return []

    free_list = getattr(script_object, "free_placed_points", None) or []
    if index >= len(free_list):
        return []

    fp = free_list[index]
    pos = fp.get("pos")
    if pos is None or not hasattr(pos, "X"):
        return []

    try:
        rx = float(fp.get("rot_x", 0.0) or 0.0)
        ry = float(fp.get("rot_y", 0.0) or 0.0)
        rz = float(fp.get("rot_z", 0.0) or 0.0)
        label_text = f"RotX={rx:.1f}  RotY={ry:.1f}  RotZ={rz:.1f}"

        text_com_prop = AllplanBaseElements.CommonProperties()
        # Texto como ayuda de construcción, color gris claro y trazo fino
        text_com_prop.Pen = 1
        text_com_prop.Color = 7  # gris claro
        text_com_prop.Construction = True

        text_prop = AllplanBasisElements.TextProperties()
        text_prop.Height = 0.10
        text_prop.Width = 0.10
        text_prop.IsScaleDependent = False

        loc = AllplanGeo.Point2D(
            float(getattr(pos, "X", 0.0) or 0.0) + dx,
            float(getattr(pos, "Y", 0.0) or 0.0) + dy,
        )

        return [
            AllplanBasisElements.TextElement(text_com_prop, text_prop, label_text, loc)
        ]
    except Exception as ex:
        print(f"[ED] create_free_point_rotation_label: error creando etiqueta: {ex}")
        return []


def start_macro_point_capture(intr: Any) -> bool:
    """Lanza el inicio de captura de punto para una macro, delegando en intr.start_macro_point_capture si existe."""
    fn = getattr(intr, "start_macro_point_capture", None)
    if callable(fn):
        try:
            return bool(fn())
        except Exception:
            return False
    return False


def add_macro_library_marker(intr: Any) -> bool:
    """Añade un marcador de macro de librería delegando en intr._add_macro_library_marker si está disponible."""
    fn = getattr(intr, "_add_macro_library_marker", None)
    if callable(fn):
        try:
            return bool(fn())
        except Exception:
            return False
    return False
