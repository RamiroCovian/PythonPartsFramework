# -*- coding: utf-8 -*-
"""
Detección de vértices (giros 90°, rectos, bifurcaciones) y cálculo de recortes
por segmento para codos y manguitos.
"""
from __future__ import annotations

import math
import os
from typing import AbstractSet, Any, Callable

import NemAll_Python_Geometry as AllplanGeo

from .trim_config import (
    ELBOW_TRIM_BY_DIAM,
    MANGUITO_TRIM_BY_DIAM,
    SPLIT_FECAL_25_110_LAST_REDUCER_EXTRA_X_MM,
    TE_TRIMS,
    manguito_asymmetric_trim_mm,
)


def _key_from_point(pt) -> tuple[float, float, float]:
    """Clave de vértice por coordenadas redondeadas."""
    return (round(pt.X, 3), round(pt.Y, 3), round(pt.Z, 3))


def is_90_deg_turn(p_prev, p_curr, p_next) -> bool:
    """
    True si el giro entre (p_prev → p_curr → p_next) es 90°,
    considerando tramos ortogonales en X, Y o Z (eje dominante).
    """
    if not (p_prev and p_curr and p_next):
        return False

    v1 = (
        p_curr.X - p_prev.X,
        p_curr.Y - p_prev.Y,
        p_curr.Z - p_prev.Z,
    )
    v2 = (
        p_next.X - p_curr.X,
        p_next.Y - p_curr.Y,
        p_next.Z - p_curr.Z,
    )
    eps = 1e-6

    if (abs(v1[0]) < eps and abs(v1[1]) < eps and abs(v1[2]) < eps) or (
        abs(v2[0]) < eps and abs(v2[1]) < eps and abs(v2[2]) < eps
    ):
        return False

    def dom_axis(v):
        ax = [abs(v[0]), abs(v[1]), abs(v[2])]
        m = max(ax)
        if m < eps:
            return None
        return ax.index(m)

    a1 = dom_axis(v1)
    a2 = dom_axis(v2)
    if a1 is None or a2 is None:
        return False
    return a1 != a2


def is_straight_turn(p_prev, p_curr, p_next, tol_deg: float = 1.0) -> bool:
    """True si el giro en planta (XY) es recto (0° o 180°)."""
    v1 = (p_curr.X - p_prev.X, p_curr.Y - p_prev.Y)
    v2 = (p_next.X - p_curr.X, p_next.Y - p_curr.Y)
    if abs(v1[0]) < 1e-9 and abs(v1[1]) < 1e-9:
        return False
    if abs(v2[0]) < 1e-9 and abs(v2[1]) < 1e-9:
        return False
    ang1 = math.degrees(math.atan2(v1[1], v1[0]))
    ang2 = math.degrees(math.atan2(v2[1], v2[0]))
    diff = abs((ang2 - ang1) % 360)
    if diff > 180:
        diff = 360 - diff
    return diff < tol_deg or abs(diff - 180) < tol_deg


def _get_diameter_from_segment(seg: Any, default: float = 20.0) -> float:
    """Extrae diámetro de un SegmentItem (.info.diameter o .info.diameter_in)."""
    try:
        info = getattr(seg, "info", None)
        if info is None:
            return default
        d = getattr(info, "diameter", None)
        if d is None:
            return default
        if isinstance(d, (list, tuple)) and d:
            return float(d[0])
        return float(d)
    except (TypeError, ValueError):
        return default


def compute_segment_cuts_for_path(
    segments: list,
    get_diameter: Callable[[int], float] | None = None,
) -> dict[int, dict[str, float]]:
    """
    Calcula recortes (start/end) por segmento para un único path.

    - segments: lista de segmentos con .data.start, .data.end (y opcional .info.diameter).
    - get_diameter: opcional seg_idx -> diámetro (mm). Si no se pasa, se usa .info.diameter.

    Returns:
        {seg_idx: {"start": mm, "end": mm}}
    """
    if get_diameter is None:
        get_diameter = lambda i: _get_diameter_from_segment(
            segments[i] if i < len(segments) else None
        )

    segment_cuts: dict[int, dict[str, float]] = {}
    n = len(segments)
    if n < 2:
        return segment_cuts

    for i in range(1, n):
        seg_prev = segments[i - 1]
        seg_curr = segments[i]
        p_prev = getattr(seg_prev.data, "start", None)
        p_curr = getattr(seg_prev.data, "end", None)
        p_next = getattr(seg_curr.data, "end", None)
        if not (p_prev and p_curr and p_next):
            continue

        d1 = get_diameter(i - 1)
        d2 = get_diameter(i)
        di1 = int(round(float(d1)))
        di2 = int(round(float(d2)))

        if is_90_deg_turn(p_prev, p_curr, p_next):
            # Codo: mismo diámetro en ambos lados; si difieren usamos el mayor
            elbow_diam = max(di1, di2)
            trim = ELBOW_TRIM_BY_DIAM.get(elbow_diam, 0.0)
            if trim > 0:
                key_left = i - 1
                key_right = i
                segment_cuts.setdefault(key_left, {"start": 0.0, "end": 0.0})["end"] += trim
                segment_cuts.setdefault(key_right, {"start": 0.0, "end": 0.0})["start"] += trim

        elif is_straight_turn(p_prev, p_curr, p_next):
            # Manguito (colineal, posible cambio de diámetro)
            t_prev = manguito_asymmetric_trim_mm(di1, di2, di1)
            t_next = manguito_asymmetric_trim_mm(di1, di2, di2)
            if t_prev is not None and t_next is not None:
                segment_cuts.setdefault(i - 1, {"start": 0.0, "end": 0.0})["end"] += float(
                    t_prev
                )
                segment_cuts.setdefault(i, {"start": 0.0, "end": 0.0})["start"] += float(
                    t_next
                )
            else:
                k_exact = (di1, di2)
                k_sorted = tuple(sorted((di1, di2)))
                trim = MANGUITO_TRIM_BY_DIAM.get(k_exact) or MANGUITO_TRIM_BY_DIAM.get(
                    k_sorted
                )
                if trim and trim > 0:
                    segment_cuts.setdefault(i - 1, {"start": 0.0, "end": 0.0})["end"] += float(
                        trim
                    )
                    segment_cuts.setdefault(i, {"start": 0.0, "end": 0.0})["start"] += float(
                        trim
                    )

    return segment_cuts


def get_trimmed_length_and_center(
    length_3d: float,
    cut_start: float,
    cut_end: float,
    start_point,
    end_point,
):
    """
    Dado un tramo con longitud, recortes y extremos, devuelve longitud efectiva
    y punto central del tramo recortado (para posicionar el tubo).

    Returns:
        (length_trimmed, center_point) o (0, None) si el tramo queda inválido.
    """
    total_cut = cut_start + cut_end
    length_trim = length_3d - total_cut
    if length_trim <= 1e-3:
        return 0.0, None

    dx = end_point.X - start_point.X
    dy = end_point.Y - start_point.Y
    dz = end_point.Z - start_point.Z
    if length_3d < 1e-6:
        return 0.0, None
    ux = dx / length_3d
    uy = dy / length_3d
    uz = dz / length_3d

    # Puntos recortados
    p_start = AllplanGeo.Point3D(
        start_point.X + ux * cut_start,
        start_point.Y + uy * cut_start,
        start_point.Z + uz * cut_start,
    )
    p_end = AllplanGeo.Point3D(
        end_point.X - ux * cut_end,
        end_point.Y - uy * cut_end,
        end_point.Z - uz * cut_end,
    )
    cx = (p_start.X + p_end.X) / 2.0
    cy = (p_start.Y + p_end.Y) / 2.0
    cz = (p_start.Z + p_end.Z) / 2.0
    center = AllplanGeo.Point3D(cx, cy, cz)
    return length_trim, center


# ---------------------------------------------------------------------------
# Bifurcaciones (TE): vertex_map con todos los paths y registro de recortes TE
# ---------------------------------------------------------------------------

def build_vertex_map_all_paths(
    segment_groups: list,
) -> tuple[dict[tuple[float, float, float], list[dict]], set]:
    """
    Construye el mapa de vértices con todos los paths y el set de vértices
    que son TE (3 segmentos en un punto).

    - segment_groups: lista de listas de segmentos (cada sublista es un path).
    - Cada conexión en vertex_map[key] tiene: path_idx, seg_idx, is_start (True = vértice en start del segmento).

    Returns:
        (vertex_map, te_vertices)
        vertex_map: clave (x,y,z) -> lista de {"path_idx", "seg_idx", "is_start"}
        te_vertices: set de claves con exactamente 3 conexiones.
    """
    vertex_map: dict[tuple[float, float, float], list[dict]] = {}

    for path_idx, segments in enumerate(segment_groups):
        if not segments:
            continue
        for seg_idx in range(len(segments)):
            seg = segments[seg_idx]
            data = getattr(seg, "data", None)
            if not data:
                continue
            p_start = getattr(data, "start", None)
            p_end = getattr(data, "end", None)
            if not p_start or not p_end:
                continue
            for is_start, pt in ((True, p_start), (False, p_end)):
                key = _key_from_point(pt)
                vertex_map.setdefault(key, []).append({
                    "path_idx": path_idx,
                    "seg_idx": seg_idx,
                    "is_start": is_start,
                })

    te_vertices = {k for k, conns in vertex_map.items() if len(conns) == 3}
    return vertex_map, te_vertices


def detect_bifurcations(segment_groups: list) -> tuple[dict[tuple[float, float, float], list[dict]], set]:
    """
    Detección de bifurcaciones (TE) al estilo fontaneria.py:
    - Construye un vertex_map global con todas las trayectorias (paths).
    - Considera bifurcación cualquier vértice con exactamente 3 conexiones.

    Returns:
        (vertex_map, te_vertices)
    """
    return build_vertex_map_all_paths(segment_groups)


def _seg_dir_from_conn(conn: dict, segment_groups: list) -> tuple[float, float, float]:
    """Dirección unitaria del segmento desde el vértice (hacia el otro extremo)."""
    path_idx = conn["path_idx"]
    seg_idx = conn["seg_idx"]
    is_start = conn.get("is_start", True)
    segments = segment_groups[path_idx]
    if seg_idx >= len(segments):
        return (0.0, 0.0, 0.0)
    seg = segments[seg_idx]
    data = getattr(seg, "data", None)
    if not data:
        return (0.0, 0.0, 0.0)
    start = getattr(data, "start", None)
    end = getattr(data, "end", None)
    if not start or not end:
        return (0.0, 0.0, 0.0)
    # Desde el vértice: si is_start el vértice es start, dirección hacia end; si no, hacia start
    if is_start:
        vx, vy, vz = end.X - start.X, end.Y - start.Y, end.Z - start.Z
    else:
        vx, vy, vz = start.X - end.X, start.Y - end.Y, start.Z - end.Z
    ln = math.sqrt(vx * vx + vy * vy + vz * vz)
    if ln < 1e-9:
        return (0.0, 0.0, 0.0)
    return (vx / ln, vy / ln, vz / ln)


def _other_endpoint_from_conn(conn: dict, segment_groups: list):
    """Devuelve el endpoint opuesto al nodo para una conexión del vertex_map."""
    path_idx = conn["path_idx"]
    seg_idx = conn["seg_idx"]
    is_start = conn.get("is_start", True)
    if path_idx >= len(segment_groups) or seg_idx >= len(segment_groups[path_idx]):
        return None
    seg = segment_groups[path_idx][seg_idx]
    data = getattr(seg, "data", None)
    if not data:
        return None
    start = getattr(data, "start", None)
    end = getattr(data, "end", None)
    if not start or not end:
        return None
    return end if is_start else start


def detect_cross_path_elbows(
    segment_groups: list,
    vertex_map: dict[tuple[float, float, float], list[dict]] | None = None,
    te_vertices: set | None = None,
    colinear_tol: float = 0.01,
) -> dict[tuple[int, int, bool], dict]:
    """
    Detecta nodos de codo entre paths distintos (grado=2 y no colineales).

    Returns:
        {
          (path_idx, seg_idx, is_start): {
              "node_key": (x, y, z),
              "other_point": Point3D,
          }
        }
    """
    if vertex_map is None:
        vertex_map, te_detected = build_vertex_map_all_paths(segment_groups)
    else:
        te_detected = set()
    te_set = set(te_vertices or te_detected or [])

    out: dict[tuple[int, int, bool], dict] = {}

    for vkey, conns in (vertex_map or {}).items():
        if vkey in te_set or len(conns) != 2:
            continue

        c1, c2 = conns[0], conns[1]
        # Solo nos interesa el caso partido en dos paths distintos
        if c1.get("path_idx") == c2.get("path_idx"):
            continue

        d1 = _seg_dir_from_conn(c1, segment_groups)
        d2 = _seg_dir_from_conn(c2, segment_groups)
        dot = d1[0] * d2[0] + d1[1] * d2[1] + d1[2] * d2[2]
        # Si son colineales, no es codo
        if abs(abs(dot) - 1.0) < float(colinear_tol):
            continue

        for own, other in ((c1, c2), (c2, c1)):
            other_pt = _other_endpoint_from_conn(other, segment_groups)
            if other_pt is None:
                continue
            key = (own["path_idx"], own["seg_idx"], bool(own.get("is_start", True)))
            out[key] = {
                "node_key": vkey,
                "other_point": other_pt,
                "other_path_idx": other.get("path_idx"),
                "other_seg_idx": other.get("seg_idx"),
            }

    return out


def detect_cross_path_manguitos(
    segment_groups: list,
    vertex_map: dict[tuple[float, float, float], list[dict]] | None = None,
    te_vertices: set | None = None,
    colinear_tol: float = 0.02,
) -> dict[tuple[int, int, bool], dict]:
    """
    Detecta nodos de manguito entre paths distintos (grado=2 y colineales).
    """
    if vertex_map is None:
        vertex_map, te_detected = build_vertex_map_all_paths(segment_groups)
    else:
        te_detected = set()
    te_set = set(te_vertices or te_detected or [])

    out: dict[tuple[int, int, bool], dict] = {}

    for vkey, conns in (vertex_map or {}).items():
        if vkey in te_set or len(conns) != 2:
            continue

        c1, c2 = conns[0], conns[1]
        if c1.get("path_idx") == c2.get("path_idx"):
            continue

        d1 = _seg_dir_from_conn(c1, segment_groups)
        d2 = _seg_dir_from_conn(c2, segment_groups)
        dot = d1[0] * d2[0] + d1[1] * d2[1] + d1[2] * d2[2]
        is_colinear = abs(abs(dot) - 1.0) < float(colinear_tol)
        if not is_colinear:
            continue

        for own, other in ((c1, c2), (c2, c1)):
            other_pt = _other_endpoint_from_conn(other, segment_groups)
            if other_pt is None:
                continue
            key = (own["path_idx"], own["seg_idx"], bool(own.get("is_start", True)))
            out[key] = {
                "node_key": vkey,
                "other_point": other_pt,
            }

    return out


def register_cross_path_elbow_cuts_into(
    segment_cuts: dict[tuple[int, int], dict[str, float]],
    segment_groups: list,
    vertex_map: dict[tuple[float, float, float], list[dict]] | None,
    te_vertices: set | None,
    get_diameter: Callable[[int, int], float],
) -> None:
    """
    Añade recortes de codo en nodos compartidos por 2 paths distintos.

    Caso objetivo: tras edición/borrado, un codo puede quedar representado por
    dos segmentos en paths diferentes. Se detecta el nodo común y se recorta
    el lado correspondiente de ambos segmentos.
    """
    cross_elbows = detect_cross_path_elbows(
        segment_groups=segment_groups,
        vertex_map=vertex_map,
        te_vertices=te_vertices,
    )
    if not cross_elbows:
        return

    # Agrupar por nodo para no aplicar dos veces el mismo recorte
    by_node: dict[tuple[float, float, float], list[tuple[int, int, bool]]] = {}
    for conn_key, info in cross_elbows.items():
        node_key = info.get("node_key")
        if not node_key:
            continue
        by_node.setdefault(node_key, []).append(conn_key)

    for _node_key, conn_keys in by_node.items():
        if len(conn_keys) < 2:
            continue

        # En grado 2 esperamos exactamente 2 conexiones. Si por ruido hay más,
        # usamos las dos primeras para recorte de codo.
        c1 = conn_keys[0]
        c2 = conn_keys[1]
        p1, s1, _is_start_1 = c1
        p2, s2, _is_start_2 = c2

        d1 = int(round(float(get_diameter(p1, s1))))
        d2 = int(round(float(get_diameter(p2, s2))))
        elbow_diam = max(d1, d2)
        trim = float(ELBOW_TRIM_BY_DIAM.get(elbow_diam, 0.0) or 0.0)
        if trim <= 0.0:
            continue

        for path_idx, seg_idx, is_start in (c1, c2):
            seg_key = (path_idx, seg_idx)
            cuts = segment_cuts.setdefault(seg_key, {"start": 0.0, "end": 0.0})
            side = "start" if is_start else "end"
            cuts[side] = float(cuts.get(side, 0.0)) + trim


def register_cross_path_manguito_cuts_into(
    segment_cuts: dict[tuple[int, int], dict[str, float]],
    segment_groups: list,
    vertex_map: dict[tuple[float, float, float], list[dict]] | None,
    te_vertices: set | None,
    get_diameter: Callable[[int, int], float],
) -> None:
    """
    Añade recortes de manguito en nodos compartidos por 2 paths distintos colineales.
    """
    cross_manguitos = detect_cross_path_manguitos(
        segment_groups=segment_groups,
        vertex_map=vertex_map,
        te_vertices=te_vertices,
    )
    if not cross_manguitos:
        return

    by_node: dict[tuple[float, float, float], list[tuple[int, int, bool]]] = {}
    for conn_key, info in cross_manguitos.items():
        node_key = info.get("node_key")
        if not node_key:
            continue
        by_node.setdefault(node_key, []).append(conn_key)

    for _node_key, conn_keys in by_node.items():
        if len(conn_keys) < 2:
            continue

        c1 = conn_keys[0]
        c2 = conn_keys[1]
        p1, s1, _ = c1
        p2, s2, _ = c2

        d1 = int(round(float(get_diameter(p1, s1))))
        d2 = int(round(float(get_diameter(p2, s2))))
        k_sorted = tuple(sorted((d1, d2)))

        asymmetric_pair = k_sorted in ((25, 40), (40, 110), (25, 110))
        if asymmetric_pair:
            try:
                from .trim_config import (
                    REDUCT_110_40_TRIM_IN_MM,
                    REDUCT_110_40_TRIM_OUT_MM,
                    SPLIT_FECAL_25_110_LAST_REDUCER_EXTRA_X_MM,
                    TAPRED_40_25_TRIM_IN_MM,
                    TAPRED_40_25_TRIM_OUT_MM,
                )
            except ImportError:
                asymmetric_pair = False

        if asymmetric_pair and k_sorted == (25, 40):
            trim_by_d = {
                25: float(TAPRED_40_25_TRIM_IN_MM),
                40: float(TAPRED_40_25_TRIM_OUT_MM),
            }
        elif asymmetric_pair and k_sorted == (40, 110):
            trim_by_d = {
                110: float(REDUCT_110_40_TRIM_IN_MM),
                40: float(REDUCT_110_40_TRIM_OUT_MM),
            }
        elif asymmetric_pair and k_sorted == (25, 110):
            trim_by_d = {
                25: float(TAPRED_40_25_TRIM_IN_MM),
                110: float(REDUCT_110_40_TRIM_IN_MM)
                + float(SPLIT_FECAL_25_110_LAST_REDUCER_EXTRA_X_MM),
            }
        else:
            trim_by_d = {}
            k_exact = (d1, d2)
            trim = MANGUITO_TRIM_BY_DIAM.get(k_exact) or MANGUITO_TRIM_BY_DIAM.get(
                k_sorted
            )
            if not trim or float(trim) <= 0.0:
                continue
            trim_val = float(trim)

        for path_idx, seg_idx, is_start in (c1, c2):
            seg_key = (path_idx, seg_idx)
            cuts = segment_cuts.setdefault(seg_key, {"start": 0.0, "end": 0.0})
            side = "start" if is_start else "end"
            d_seg = int(round(float(get_diameter(path_idx, seg_idx))))
            if trim_by_d:
                add_mm = trim_by_d.get(d_seg)
                if add_mm is None:
                    continue
            else:
                add_mm = trim_val
            cuts[side] = float(cuts.get(side, 0.0)) + add_mm


def _conn_segment_system_is_fecal(segment_groups: list, conn: dict) -> bool:
    try:
        seg = segment_groups[conn["path_idx"]][conn["seg_idx"]]
        info = getattr(seg, "info", None)
        s = str(getattr(info, "system", None) or "").strip().lower()
        return s.startswith("fecal")
    except Exception:
        return False


def register_te_cuts_into(
    segment_cuts: dict[tuple[int, int], dict[str, float]],
    vkey: tuple[float, float, float],
    vertex_map: dict,
    segment_groups: list,
    get_diameter: Callable[[int, int], float],
) -> None:
    """
    Registra recortes de TE en el vértice vkey y los suma a segment_cuts.
    segment_cuts se modifica in-place. Clave de segment_cuts: (path_idx, seg_idx).
    get_diameter(path_idx, seg_idx) -> diámetro en mm.
    """
    conns = vertex_map.get(vkey, [])
    if len(conns) < 3:
        return

    dirs = [(_seg_dir_from_conn(c, segment_groups), idx) for idx, c in enumerate(conns)]
    best_pair = None
    best_dot = -1.0
    for i in range(len(dirs)):
        for j in range(i + 1, len(dirs)):
            d1, idx1 = dirs[i]
            d2, idx2 = dirs[j]
            dot = abs(d1[0] * d2[0] + d1[1] * d2[1] + d1[2] * d2[2])
            if dot > best_dot:
                best_dot = dot
                best_pair = (idx1, idx2)

    if not best_pair:
        return
    main_i, main_j = best_pair
    branch_k = [k for k in range(len(conns)) if k not in (main_i, main_j)][0]
    main_a, main_b = conns[main_i], conns[main_j]
    branch = conns[branch_k]

    d_main_a = int(round(get_diameter(main_a["path_idx"], main_a["seg_idx"])))
    d_main_b = int(round(get_diameter(main_b["path_idx"], main_b["seg_idx"])))
    d_branch = int(round(get_diameter(branch["path_idx"], branch["seg_idx"])))

    main_in = max(d_main_a, d_main_b)
    main_out = min(d_main_a, d_main_b)
    key_te = (main_in, d_branch, main_out)
    trims = None
    # TE 40-40-40 (Y45 fecal): recortes editables en geo_handler.BIF_Y40_TE_TRIM_* .
    if main_in == 40 and main_out == 40 and d_branch == 40:
        try:
            from . import geo_handler as _gh_bif_y40

            trims = (
                float(_gh_bif_y40.BIF_Y40_TE_TRIM_MAIN_IN_MM),
                float(_gh_bif_y40.BIF_Y40_TE_TRIM_BRANCH_MM),
                float(_gh_bif_y40.BIF_Y40_TE_TRIM_MAIN_OUT_MM),
            )
        except Exception:
            trims = (71.0, 70.6, 30.0)
    elif main_in == 110 and main_out == 110 and d_branch == 110:
        # Mismo set de recortes para 110-110-110 en pluvial y fecal.
        try:
            from . import geo_handler as _gh_bif_y110p

            trims = (
                float(_gh_bif_y110p.BIF_Y110_PLUVIAL_TE_TRIM_MAIN_IN_MM),
                float(_gh_bif_y110p.BIF_Y110_PLUVIAL_TE_TRIM_BRANCH_MM),
                float(_gh_bif_y110p.BIF_Y110_PLUVIAL_TE_TRIM_MAIN_OUT_MM),
            )
        except Exception:
            trims = (140.0, 148.0, 47.0)
    elif main_in == 110 and main_out == 110 and d_branch == 40:
        try:
            from . import geo_handler as _gh_bif_y110_40

            trims = (
                float(_gh_bif_y110_40.BIF_Y110_40_TE_TRIM_MAIN_IN_MM),
                float(_gh_bif_y110_40.BIF_Y110_40_TE_TRIM_BRANCH_MM),
                float(_gh_bif_y110_40.BIF_Y110_40_TE_TRIM_MAIN_OUT_MM),
            )
        except Exception:
            trims = (50.0, 95.0, 147.0)
        if str(os.getenv("SANEAMIENTO_DEBUG_TE_Y110_40", "0")).strip().lower() in (
            "1",
            "true",
            "yes",
            "on",
        ):
            print(
                "[SANEAMIENTO][TE-Y110-40][DEBUG] register_te_cuts_into "
                f"vkey={vkey} trim_main_in={trims[0]} trim_branch={trims[1]} "
                f"trim_main_out={trims[2]} conns={len(conns)}"
            )
    if trims is None:
        trims = TE_TRIMS.get(key_te)
    if not trims:
        return
    trim_main_in, trim_branch, trim_main_out = trims

    if d_main_a >= d_main_b:
        conn_in, conn_out = main_a, main_b
    else:
        conn_in, conn_out = main_b, main_a

    # Troncal simétrico (misma Ø en ambos brazos): intercambio in/out de recortes según
    # la mano de la rama (110-110-110 y 110-110-40 con la misma geometría de decisión).
    if d_main_a == d_main_b:
        v_main_a = _seg_dir_from_conn(main_a, segment_groups)
        v_main_b = _seg_dir_from_conn(main_b, segment_groups)
        v_branch = _seg_dir_from_conn(branch, segment_groups)
        # Mismo criterio usado en te_orientation: elegir una dirección troncal base.
        base_main = v_main_a
        if (
            (v_main_a[0] * v_main_b[0] + v_main_a[1] * v_main_b[1] + v_main_a[2] * v_main_b[2])
            > 0.0
        ):
            base_main = (-base_main[0], -base_main[1], -base_main[2])
        branch_along_main = (
            v_branch[0] * base_main[0]
            + v_branch[1] * base_main[1]
            + v_branch[2] * base_main[2]
        )
        # Cuando la rama apunta "a favor" del troncal (dot>0), en los casos reportados
        # los trims in/out quedan invertidos para la TE orientada.
        # Misma regla para TE 110-110-40 (troncal simétrico, rama reducida).
        _trim_hand_te = d_branch == d_main_a or (
            d_main_a == 110 and d_main_b == 110 and int(d_branch) == 40
        )
        if _trim_hand_te and branch_along_main > 0.0:
            trim_main_in, trim_main_out = trim_main_out, trim_main_in

    def add_cut(conn: dict, trim_mm: float) -> None:
        seg_key = (conn["path_idx"], conn["seg_idx"])
        cuts = segment_cuts.setdefault(seg_key, {"start": 0.0, "end": 0.0})
        # Si este vértice es TE, eliminamos recortes previos de manguito en este mismo lado
        # y dejamos solo los trims propios de la TE.
        if conn.get("is_start"):
            cuts["start"] = 0.0
            cuts["start"] += float(trim_mm)
        else:
            cuts["end"] = 0.0
            cuts["end"] += float(trim_mm)

    add_cut(conn_in, trim_main_in)
    add_cut(branch, trim_branch)
    add_cut(conn_out, trim_main_out)


def compute_segment_cuts_for_all_paths(
    segment_groups: list,
    get_diameter: Callable[[int, int], float] | None = None,
    *,
    skip_te_vertices: AbstractSet[tuple[float, float, float]] | None = None,
) -> dict[tuple[int, int], dict[str, float]]:
    """
    Recortes por codo, manguito y TE para todos los paths.
    - segment_groups: lista de listas de segmentos.
    - get_diameter: (path_idx, seg_idx) -> diámetro mm. Si None, se usa .info.diameter del segmento.
    - skip_te_vertices: vértices (x,y,z) redondeados donde no debe aplicarse recorte de TE
      (sin pieza bifurcación en ese nodo).

    Returns:
        {(path_idx, seg_idx): {"start": mm, "end": mm}}
    """
    if get_diameter is None:
        def _default_diameter(path_idx: int, seg_idx: int) -> float:
            if path_idx < len(segment_groups) and seg_idx < len(segment_groups[path_idx]):
                return _get_diameter_from_segment(segment_groups[path_idx][seg_idx])
            return 20.0
        get_diameter = _default_diameter

    all_cuts: dict[tuple[int, int], dict[str, float]] = {}

    # 1) Codo y manguito por path
    for path_idx, segments in enumerate(segment_groups):
        path_get_diam = lambda i, pidx=path_idx: get_diameter(pidx, i)
        path_cuts = compute_segment_cuts_for_path(segments, get_diameter=path_get_diam)
        for seg_idx, cuts in path_cuts.items():
            all_cuts[(path_idx, seg_idx)] = dict(cuts)

    # 2) Vertex_map y TE
    vertex_map, te_vertices = build_vertex_map_all_paths(segment_groups)

    # 2.A) Codo entre paths distintos (grado=2 y no colineales)
    register_cross_path_elbow_cuts_into(
        all_cuts,
        segment_groups,
        vertex_map,
        te_vertices,
        get_diameter,
    )

    # 2.B) Manguito entre paths distintos (grado=2 y colineales)
    register_cross_path_manguito_cuts_into(
        all_cuts,
        segment_groups,
        vertex_map,
        te_vertices,
        get_diameter,
    )

    # 2.C) TE
    skip_te = skip_te_vertices or set()
    for vkey in te_vertices:
        if vkey in skip_te:
            continue
        register_te_cuts_into(all_cuts, vkey, vertex_map, segment_groups, get_diameter)

    return all_cuts
