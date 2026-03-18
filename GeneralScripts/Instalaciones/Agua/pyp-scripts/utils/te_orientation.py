# -*- coding: utf-8 -*-
"""
Orientación de TE (bifurcaciones) portando la lógica de fontaneria.py.

En fontaneria.py la TE se orienta con:
- ang = atan2(my, mx) para alinear el troncal
- mirrors locales (X/Y/Z) para casos de 45°/135° y ramas elevadas
- rotación adicional para elevar la rama a +Z cuando branch_elevated

Aquí calculamos los parámetros geométricos a partir de segment_groups + vertex_map
y devolvemos te_params por nodo.
"""
from __future__ import annotations

import os
import math
from typing import Callable


def _norm2(x: float, y: float) -> float:
    return math.hypot(x, y)


# Debug TE: por defecto ON (hasta estabilizar orientación XZ/YZ)
DEBUG_TE = os.getenv("AGUA_DEBUG_TE", "1").strip() not in ("", "0", "false", "False")


def _key_from_point(pt) -> tuple[float, float, float]:
    return (round(pt.X, 3), round(pt.Y, 3), round(pt.Z, 3))


def _other_point(segment_groups: list, conn: dict):
    """Devuelve el punto 'other' desde el nodo, como en fontaneria (pt/other)."""
    seg_item = segment_groups[conn["path_idx"]][conn["seg_idx"]]
    data = seg_item.data
    start = data.start
    end = data.end
    if conn.get("is_start"):
        return end
    return start


def _norm_vec_2d_from_conn(
    segment_groups: list, center_pt, conn: dict
) -> tuple[float, float]:
    op = _other_point(segment_groups, conn)
    vx = op.X - center_pt.X
    vy = op.Y - center_pt.Y
    n = _norm2(vx, vy)
    if n < 1e-9:
        return (0.0, 0.0)
    return (vx / n, vy / n)


def _norm_vec_3d_from_conn(
    segment_groups: list, center_pt, conn: dict
) -> tuple[float, float, float]:
    op = _other_point(segment_groups, conn)
    vx = op.X - center_pt.X
    vy = op.Y - center_pt.Y
    vz = op.Z - center_pt.Z
    n = math.sqrt(vx * vx + vy * vy + vz * vz)
    if n < 1e-9:
        return (0.0, 0.0, 0.0)
    return (vx / n, vy / n, vz / n)


def build_te_params(
    segment_groups: list,
    vertex_map: dict[tuple[float, float, float], list[dict]],
    te_vertices: set,
    get_diameter: Callable[[int, int], float] | None = None,
) -> dict[tuple[float, float, float], dict]:
    """
    Calcula parámetros de orientación por nodo TE.

    Returns:
      { vkey: {
          "ang_rad": float,
          "need_mirror_x_local": bool,
          "need_mirror_y_local": bool,
          "branch_elevated": bool,
          "need_mirror_z_local": bool,
          "branch_points_down": bool,
        } }
    """
    if get_diameter is None:

        def get_diameter(path_idx: int, seg_idx: int) -> float:
            seg = segment_groups[path_idx][seg_idx]
            info = getattr(seg, "info", None)
            d = getattr(info, "diameter", 20.0) if info is not None else 20.0
            if isinstance(d, (list, tuple)) and d:
                return float(d[0])
            return float(d)

    out: dict[tuple[float, float, float], dict] = {}

    def _dot3(a: tuple[float, float, float], b: tuple[float, float, float]) -> float:
        return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]

    def _norm_ang_deg(ang_rad: float) -> float:
        ang_degrees = math.degrees(ang_rad)
        while ang_degrees > 180:
            ang_degrees -= 360
        while ang_degrees < -180:
            ang_degrees += 360
        return ang_degrees

    def _detect_plane_from_dir(v: tuple[float, float, float]) -> str:
        # Elegimos el plano según el componente "casi cero" del troncal.
        # Esto replica el enfoque de fontaneria (planos principales) y arregla XZ/YZ.
        x, y, z = v
        ax, ay, az = abs(x), abs(y), abs(z)
        # Allplan suele dar floats con ruido; subimos tolerancia para clasificar mejor YZ/XZ.
        eps = 5e-2
        if az < eps:
            return "XY"
        if ay < eps:
            return "XZ"
        if ax < eps:
            return "YZ"
        # Caso oblicuo 3D: mantenemos XY (se comporta como antes).
        return "XY"

    def _compute_mirrors_fontaneria_like(
        *,
        type_te: int,
        di_main_in: int,
        di_main_out: int,
        mirror_x: bool,
        branch_in_plane: bool,
        branch_elevated: bool,
        branch_points_up: bool,
        branch_points_down: bool,
        ang_rad: float,
    ) -> tuple[bool, bool, bool]:
        """
        Port literal (adaptado) del bloque fontaneria.py L4057-L4518.
        Devuelve (need_mirror_x_local, need_mirror_y_local, need_mirror_z_local).
        """
        need_mirror_x_local = False
        need_mirror_y_local = False
        need_mirror_z_local = False

        ang_degrees = _norm_ang_deg(ang_rad)

        if type_te > 3 or (type_te > 3 and branch_elevated):
            if di_main_in != di_main_out and di_main_in > di_main_out:
                # Lado grande en entrada
                if not mirror_x:
                    if abs(ang_degrees - 90) < 1:
                        need_mirror_y_local = True
                        need_mirror_x_local = True
                        if branch_elevated:
                            if branch_points_up:
                                need_mirror_z_local = False
                            elif branch_points_down:
                                need_mirror_z_local = True
                    elif abs(ang_degrees - (-90)) < 1 or abs(ang_degrees - 270) < 1:
                        need_mirror_x_local = True
                        need_mirror_y_local = True
                        if branch_elevated:
                            if branch_points_up:
                                need_mirror_z_local = False
                            elif branch_points_down:
                                need_mirror_z_local = True
                    elif abs(ang_degrees - 180) < 1 or abs(ang_degrees - (-180)) < 1:
                        need_mirror_y_local = True
                        if branch_elevated and branch_points_up:
                            need_mirror_z_local = True
                    elif abs(ang_degrees - 0) < 1 or abs(ang_degrees - 360) < 1:
                        need_mirror_y_local = True
                        if branch_elevated and branch_points_up:
                            need_mirror_z_local = True
                    else:
                        if branch_in_plane:
                            if (
                                abs(ang_degrees - 45.0) < 10.0
                                or abs(ang_degrees - 225.0) < 10.0
                                or abs(ang_degrees - (-135.0)) < 10.0
                            ):
                                need_mirror_x_local = True
                            elif (
                                abs(ang_degrees - 135.0) < 10.0
                                or abs(ang_degrees - 315.0) < 10.0
                                or abs(ang_degrees - (-45.0)) < 10.0
                            ):
                                need_mirror_y_local = True
                            else:
                                need_mirror_y_local = True
                        else:
                            need_mirror_y_local = True
                else:
                    # mirror_x=True: solo especiales 45/135 si rama en plano
                    if branch_in_plane:
                        if (
                            abs(ang_degrees - 45.0) < 10.0
                            or abs(ang_degrees - 225.0) < 10.0
                            or abs(ang_degrees - (-135.0)) < 10.0
                        ):
                            need_mirror_x_local = True
                        elif (
                            abs(ang_degrees - 135.0) < 10.0
                            or abs(ang_degrees - 315.0) < 10.0
                            or abs(ang_degrees - (-45.0)) < 10.0
                        ):
                            need_mirror_y_local = True

            elif di_main_in != di_main_out and di_main_in < di_main_out:
                if not mirror_x:
                    need_mirror_x_local = True
                elif abs(ang_degrees - 90) < 1:
                    need_mirror_y_local = False
                    if branch_elevated:
                        if branch_points_up:
                            need_mirror_z_local = False
                        elif branch_points_down:
                            need_mirror_z_local = True
                elif abs(ang_degrees - (-90)) < 1 or abs(ang_degrees - 270) < 1:
                    need_mirror_y_local = False
                    if branch_elevated:
                        if branch_points_up:
                            need_mirror_z_local = False
                        elif branch_points_down:
                            need_mirror_z_local = True
                elif abs(ang_degrees - 180) < 1 or abs(ang_degrees - (-180)) < 1:
                    need_mirror_x_local = True
                    if branch_elevated and branch_points_up:
                        need_mirror_z_local = True
                elif abs(ang_degrees - 0) < 1 or abs(ang_degrees - 360) < 1:
                    need_mirror_x_local = True
                    if branch_elevated and branch_points_up:
                        need_mirror_z_local = True
                elif branch_in_plane:
                    if (
                        abs(ang_degrees - 45.0) < 10.0
                        or abs(ang_degrees - 225.0) < 10.0
                        or abs(ang_degrees - (-135.0)) < 10.0
                    ):
                        need_mirror_x_local = True
                    elif (
                        abs(ang_degrees - 135.0) < 10.0
                        or abs(ang_degrees - 315.0) < 10.0
                        or abs(ang_degrees - (-45.0)) < 10.0
                    ):
                        need_mirror_y_local = True

        elif type_te <= 3 or (type_te <= 3 and branch_elevated):
            ang_degrees = _norm_ang_deg(ang_rad)

            if branch_in_plane:
                if (
                    abs(ang_degrees - 45.0) < 10.0
                    or abs(ang_degrees - 225.0) < 10.0
                    or abs(ang_degrees - (-135.0)) < 10.0
                ):
                    need_mirror_x_local = True
                elif (
                    abs(ang_degrees - 135.0) < 10.0
                    or abs(ang_degrees - 315.0) < 10.0
                    or abs(ang_degrees - (-45.0)) < 10.0
                ):
                    need_mirror_y_local = True
                elif (
                    abs(ang_degrees - 90) < 1
                    or abs(ang_degrees - (-90)) < 1
                    or abs(ang_degrees - 270) < 1
                ):
                    need_mirror_y_local = True
            elif (
                abs(ang_degrees - 90) < 1
                or abs(ang_degrees - (-90)) < 1
                or abs(ang_degrees - 270) < 1
            ):
                need_mirror_y_local = True
                if branch_elevated:
                    if branch_points_up:
                        need_mirror_z_local = False
                    elif branch_points_down:
                        need_mirror_z_local = True
            else:
                if branch_elevated:
                    if branch_points_up:
                        need_mirror_z_local = True
                    elif branch_points_down:
                        need_mirror_z_local = False

        return need_mirror_x_local, need_mirror_y_local, need_mirror_z_local

    for vkey in te_vertices:
        conns = vertex_map.get(vkey, [])
        if len(conns) != 3:
            continue

        cx, cy, cz = vkey

        # center_pt solo para vectores
        class _P:
            X = cx
            Y = cy
            Z = cz

        center_pt = _P()

        dirs_3d = [_norm_vec_3d_from_conn(segment_groups, center_pt, c) for c in conns]
        dot_01 = _dot3(dirs_3d[0], dirs_3d[1])
        dot_02 = _dot3(dirs_3d[0], dirs_3d[2])
        dot_12 = _dot3(dirs_3d[1], dirs_3d[2])

        best_pair = min(
            [(dot_01, 0, 1, 2), (dot_02, 0, 2, 1), (dot_12, 1, 2, 0)],
            key=lambda x: x[0],
        )
        dot_main, i, j, k = best_pair
        if dot_main > -0.5:
            continue

        main_infos = [conns[i], conns[j]]
        branch_info = conns[k]

        v_branch = _norm_vec_3d_from_conn(segment_groups, center_pt, branch_info)

        # Dirección troncal: tomamos la conexión i como base y elegimos su signo
        # para que el troncal apunte “hacia” la pareja opuesta (más estable).
        base_main = dirs_3d[i]
        # En teoría dirs_3d[j] ~ -base_main. Elegimos el signo que mejor alinee con -dirs_3d[j].
        if _dot3(base_main, dirs_3d[j]) > 0:
            base_main = (-base_main[0], -base_main[1], -base_main[2])

        plane = _detect_plane_from_dir(base_main)
        mx3, my3, mz3 = base_main

        # Caso especial: troncal casi vertical (±Z). En fontaneria el "ang" y los mirrors X/Y
        # se calculan en el plano XY; para troncal vertical eso no es estable y puede invertir la rama.
        # Aquí delegamos la orientación al bloque 3D (SPECIAL_VERTICAL) y anulamos mirrors X/Y.
        if abs(mx3) < 0.05 and abs(my3) < 0.05 and abs(mz3) > 0.95:
            bx, by, bz = v_branch
            out[vkey] = {
                "center_pt": (cx, cy, cz),
                "ang_rad": 0.0,
                "plane": "VERTICAL",
                "main_dir_3d": (mx3, my3, mz3),
                "branch_dir_3d": (bx, by, bz),
                "need_mirror_x_local": False,
                "need_mirror_y_local": False,
                "branch_elevated": False,
                "need_mirror_z_local": False,
                "branch_points_down": False,
                "type_te": 1,
            }
            if DEBUG_TE:
                print(
                    "[DBG TE] node=%s plane=VERTICAL main=(%.3f,%.3f,%.3f) branch=(%.3f,%.3f,%.3f) "
                    "mirrors(x=False y=False z=False) (forced vertical short-circuit)"
                    % (vkey, mx3, my3, mz3, bx, by, bz)
                )
            continue

        # Ángulo del troncal según el plano dominante (para rotación en geo_handler).
        if plane == "XY":
            ang = math.atan2(my3, mx3)
        elif plane == "XZ":
            ang = math.atan2(mz3, mx3)  # rotación alrededor de Y
        else:  # "YZ"
            ang = math.atan2(mz3, my3)  # rotación alrededor de X

        # Descomponer rama
        bx, by, bz = v_branch

        # Diámetros (para heurística type_te)
        d1 = float(get_diameter(main_infos[0]["path_idx"], main_infos[0]["seg_idx"]))
        d2 = float(get_diameter(main_infos[1]["path_idx"], main_infos[1]["seg_idx"]))
        d_branch = float(get_diameter(branch_info["path_idx"], branch_info["seg_idx"]))

        # Determinar main_in/out (siempre con el par de troncal, no afecta al plano)
        # Usamos el signo sobre base_main para decidir “in/out”.
        v1 = _norm_vec_3d_from_conn(segment_groups, center_pt, main_infos[0])
        v2 = _norm_vec_3d_from_conn(segment_groups, center_pt, main_infos[1])
        dot1 = _dot3(v1, base_main)
        dot2 = _dot3(v2, base_main)
        if dot1 > dot2:
            d_main_in, d_main_out = d1, d2
        else:
            d_main_in, d_main_out = d2, d1

        # Rama en el plano del troncal vs "elevada" fuera del plano (generalizado a XY/XZ/YZ).
        if plane == "XY":
            out_comp = bz
            branch_proj_a, branch_proj_b = bx, by  # X,Y
        elif plane == "XZ":
            out_comp = by
            branch_proj_a, branch_proj_b = bx, bz  # X,Z
        else:  # "YZ"
            out_comp = bx
            branch_proj_a, branch_proj_b = by, bz  # Y,Z

        branch_in_plane = abs(out_comp) < 0.1
        branch_elevated = not branch_in_plane
        branch_points_up = out_comp > 0.1
        branch_points_down = out_comp < -0.1

        # Ajuste de ang (fontaneria): si la rama en plano apunta al lado opuesto, rotar 180°
        if branch_in_plane:
            branch_dir_initial_a = math.sin(ang)
            branch_dir_initial_b = math.cos(ang)
            dot_branch_initial = (
                branch_dir_initial_a * branch_proj_a
                + branch_dir_initial_b * branch_proj_b
            )
            if dot_branch_initial < 0:
                ang += math.pi
        else:
            # Elevada: no se corrige con 180° en el plano
            pass

        # Heurística de type_te (para activar mirrors 45/135 de la sección type_te<=3)
        # Si hay mezcla de diámetros o rama elevada, tratamos como "mixta"
        di_main_in = int(round(d_main_in))
        di_main_out = int(round(d_main_out))
        di_branch = int(round(d_branch))
        mixed = (di_main_in != di_main_out) or (
            di_branch not in (di_main_in, di_main_out)
        )
        type_te = 4 if mixed else 1

        # En fontaneria mirror_x depende del modelo (invertido). En Agua usamos heurística equivalente.
        mirror_x = di_main_in < di_main_out

        need_mirror_x_local, need_mirror_y_local, need_mirror_z_local = (
            _compute_mirrors_fontaneria_like(
                type_te=type_te,
                di_main_in=di_main_in,
                di_main_out=di_main_out,
                mirror_x=mirror_x,
                branch_in_plane=branch_in_plane,
                branch_elevated=branch_elevated,
                branch_points_up=branch_points_up,
                branch_points_down=branch_points_down,
                ang_rad=ang,
            )
        )

        if DEBUG_TE:
            print(
                "[DBG TE] node=%s plane=%s ang=%.1f° main=(%.3f,%.3f,%.3f) branch=(%.3f,%.3f,%.3f) "
                "branch_in_plane=%s branch_elevated=%s mirrors(x=%s y=%s z=%s) type_te=%s di_in=%s di_out=%s"
                % (
                    vkey,
                    plane,
                    _norm_ang_deg(ang),
                    mx3,
                    my3,
                    mz3,
                    bx,
                    by,
                    bz,
                    str(branch_in_plane),
                    str(branch_elevated),
                    str(need_mirror_x_local),
                    str(need_mirror_y_local),
                    str(need_mirror_z_local),
                    str(type_te),
                    str(di_main_in),
                    str(di_main_out),
                )
            )

        out[vkey] = {
            "center_pt": (cx, cy, cz),
            "ang_rad": ang,
            "plane": plane,
            "main_dir_3d": (mx3, my3, mz3),
            "branch_dir_3d": (bx, by, bz),
            "need_mirror_x_local": need_mirror_x_local,
            "need_mirror_y_local": need_mirror_y_local,
            "branch_elevated": branch_elevated,
            "need_mirror_z_local": need_mirror_z_local,
            "branch_points_down": branch_points_down,
            "type_te": type_te,
        }

    return out
