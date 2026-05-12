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
import NemAll_Python_Utility as PythonUtility


def _norm2(x: float, y: float) -> float:
    return math.hypot(x, y)


# Debug TE: por defecto ON (hasta estabilizar orientación XZ/YZ)
DEBUG_TE = os.getenv("AGUA_DEBUG_TE", "1").strip() not in ("", "0", "false", "False")
_CABAL_WARNING_SHOWN_KEYS: set[tuple[tuple[float, float, float], int, int, int]] = set()
_INVALID_SANE_Y45_ANGLE_MSG_KEYS: set[tuple[float, float, float]] = set()


def _acute_angle_between_dirs_deg(
    dir_a: tuple[float, float, float], dir_b: tuple[float, float, float]
) -> float:
    """Ángulo agudo entre dos rectas dirigidas por vectores unitarios (0–90°)."""
    dotp = _dot3_early(dir_a, dir_b)
    dotp = max(-1.0, min(1.0, float(dotp)))
    theta = math.acos(dotp)
    acute = min(theta, math.pi - theta)
    return math.degrees(acute)


def _dot3_early(a: tuple[float, float, float], b: tuple[float, float, float]) -> float:
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def _saneamiento_y45_applies(di_in: int, di_out: int, di_branch: int) -> bool:
    """Combinaciones TE con modelo bifurcación Y45 en saneamiento (recortes en vertex_utils)."""
    if di_in == 110 and di_out == 110 and di_branch == 110:
        return True
    if di_in == 40 and di_out == 40 and di_branch == 40:
        return True
    if di_in == 110 and di_out == 110 and di_branch == 40:
        return True
    return False


def _key_from_point(pt) -> tuple[float, float, float]:
    return (round(pt.X, 3), round(pt.Y, 3), round(pt.Z, 3))


def _any_conn_fecal_system(segment_groups: list, conns: list) -> bool:
    """True si algún tramo conectado al nodo declara sistema fecal."""
    for c in conns:
        try:
            seg = segment_groups[c["path_idx"]][c["seg_idx"]]
            info = getattr(seg, "info", None)
            s = str(getattr(info, "system", None) or "").strip().lower()
            if s.startswith("fecal"):
                return True
        except Exception:
            continue
    return False


def _all_conn_fecal_system(segment_groups: list, conns: list) -> bool:
    """True si los tres tramos del nodo declaran sistema fecal."""
    if len(conns) != 3:
        return False
    for c in conns:
        try:
            seg = segment_groups[c["path_idx"]][c["seg_idx"]]
            info = getattr(seg, "info", None)
            s = str(getattr(info, "system", None) or "").strip().lower()
            if not s.startswith("fecal"):
                return False
        except Exception:
            return False
    return True


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
    *,
    saneamiento_enforce_y45_branch_geometry: bool = False,
    saneamiento_y45_tolerance_deg: float = 6.0,
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

    def get_distribution_type(path_idx: int, seg_idx: int) -> str:
        try:
            seg = segment_groups[path_idx][seg_idx]
            info = getattr(seg, "info", None)
            dist = getattr(info, "distribution_type", "IS") if info is not None else "IS"
            return "TD" if str(dist).upper() == "TD" else "IS"
        except Exception:
            return "IS"

    out: dict[tuple[float, float, float], dict] = {}

    def _reject_invalid_sane_y45(
        vkey_inner: tuple[float, float, float],
        base_main: tuple[float, float, float],
        v_br: tuple[float, float, float],
        din: int,
        dout: int,
        dbra: int,
    ) -> bool:
        """
        True si no se debe generar TE (geometría ≠ Y45 en troncal/rama).
        Muestra un único aviso por vértice en la sesión.
        """
        if not saneamiento_enforce_y45_branch_geometry:
            return False
        if not _saneamiento_y45_applies(din, dout, dbra):
            return False
        phi = _acute_angle_between_dirs_deg(base_main, v_br)
        if abs(phi - 45.0) <= float(saneamiento_y45_tolerance_deg):
            return False
        if vkey_inner not in _INVALID_SANE_Y45_ANGLE_MSG_KEYS:
            _INVALID_SANE_Y45_ANGLE_MSG_KEYS.add(vkey_inner)
            try:
                PythonUtility.ShowMessageBox(
                    "angulo no valido para bifurcación 45° Y",
                    PythonUtility.MB_OK,
                )
            except Exception:
                pass
        if DEBUG_TE:
            print(
                "[SANEAMIENTO][TE-Y45] TE omitida (ángulo troncal–rama). "
                f"vkey={vkey_inner} acute={phi:.1f}° "
                f"di_in={din} di_out={dout} di_branch={dbra}"
            )
        return True

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

        # Diámetros por conexión y asignación main_in/main_out (como fontaneria).
        d1 = float(get_diameter(main_infos[0]["path_idx"], main_infos[0]["seg_idx"]))
        d2 = float(get_diameter(main_infos[1]["path_idx"], main_infos[1]["seg_idx"]))
        d_branch = float(get_diameter(branch_info["path_idx"], branch_info["seg_idx"]))
        v1 = _norm_vec_3d_from_conn(segment_groups, center_pt, main_infos[0])
        v2 = _norm_vec_3d_from_conn(segment_groups, center_pt, main_infos[1])
        dot1 = _dot3(v1, base_main)
        dot2 = _dot3(v2, base_main)
        if dot1 > dot2:
            d_main_in, d_main_out = d1, d2
        else:
            d_main_in, d_main_out = d2, d1
        di_main_in = int(round(d_main_in))
        di_main_out = int(round(d_main_out))
        di_branch = int(round(d_branch))
        dist_candidates = [
            get_distribution_type(main_infos[0]["path_idx"], main_infos[0]["seg_idx"]),
            get_distribution_type(main_infos[1]["path_idx"], main_infos[1]["seg_idx"]),
            get_distribution_type(branch_info["path_idx"], branch_info["seg_idx"]),
        ]
        te_dist_type = "TD" if any(d == "TD" for d in dist_candidates) else "IS"

        if _reject_invalid_sane_y45(
            vkey,
            base_main,
            v_branch,
            di_main_in,
            di_main_out,
            di_branch,
        ):
            continue

        plane = _detect_plane_from_dir(base_main)
        mx3, my3, mz3 = base_main

        # Caso especial: troncal casi vertical (±Z). En fontaneria el "ang" y los mirrors X/Y
        # se calculan en el plano XY; para troncal vertical eso no es estable y puede invertir la rama.
        # Aquí delegamos la orientación al bloque 3D (SPECIAL_VERTICAL) y anulamos mirrors X/Y.
        if abs(mx3) < 0.05 and abs(my3) < 0.05 and abs(mz3) > 0.95:
            bx, by, bz = v_branch
            bif_y110_pluvial_only = (
                di_main_in == 110
                and di_main_out == 110
                and di_branch == 110
                and not _any_conn_fecal_system(segment_groups, conns)
            )
            y110_bif_script_variant = "pluvial"
            if di_main_in == 110 and di_main_out == 110 and di_branch == 110:
                if _all_conn_fecal_system(segment_groups, conns):
                    y110_bif_script_variant = "fecal"
            out[vkey] = {
                "center_pt": (cx, cy, cz),
                "distribution_type": te_dist_type,
                "d_main_in": di_main_in,
                "d_main_out": di_main_out,
                "d_branch": di_branch,
                "model_mirror_x": (di_main_in < di_main_out),
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
                "bif_y110_pluvial_only": bif_y110_pluvial_only,
                "y110_bif_script_variant": y110_bif_script_variant,
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
        branch_along_main = (bx * mx3) + (by * my3) + (bz * mz3)
        branch_side = 0.0

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

        # Ajuste de ang (fontaneria): si la rama en plano apunta al lado opuesto, rotar 180°.
        # Solo cuando el troncal NO es simétrico (entrada ≠ salida). Si el troncal es simétrico
        # (110-110-110, 110-110-40, etc.), la orientación en plano la fijan los mirrors locales
        # más abajo; aplicar también ang+=π duplica la corrección y desalinea la rama Ø40.
        symmetric_main_trunk = (
            branch_in_plane
            and not branch_elevated
            and di_main_in == di_main_out
        )
        if branch_in_plane and not symmetric_main_trunk:
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

        # Regla geométrica robusta para TE con troncal simétrico (misma Ø entrada/salida) y rama en plano:
        # mismo criterio lateral/arriba-abajo que 110-110-110, aplicable también a 110-110-40 (rama Ø40)
        # y otras Y con rama distinta al troncal — el modelo local (Bif_Reduc / Y Ø110) comparte convención.
        if branch_in_plane and not branch_elevated and di_main_in == di_main_out:
            # Para TE simétrica dividimos el "encaje" en:
            # - need_mirror_y_local: controla la convención arriba/abajo (según branch_along_main).
            # - need_mirror_x_local: controla el lado izquierda/derecha (según branch_side).
            # Eje lateral local: b = n x t, donde t es el troncal (main) y n es el normal del plano.
            # El signo de side = dot(branch, b) indica hacia qué lado cae la rama respecto al troncal.
            if plane == "XY":
                nx, ny, nz = 0.0, 0.0, 1.0
            elif plane == "XZ":
                nx, ny, nz = 0.0, 1.0, 0.0
            else:  # "YZ"
                nx, ny, nz = 1.0, 0.0, 0.0

            # t = (mx3,my3,mz3) ya está normalizado
            bxl = ny * mz3 - nz * my3
            byl = nz * mx3 - nx * mz3
            bzl = nx * my3 - ny * mx3
            blen = math.sqrt(bxl * bxl + byl * byl + bzl * bzl)
            if blen > 1e-9:
                bxl /= blen
                byl /= blen
                bzl /= blen
            else:
                # Fallback: troncal degenerado en el plano -> no definir lado fiable
                bxl, byl, bzl = 1.0, 0.0, 0.0

            branch_side = bx * bxl + by * byl + bz * bzl
            # Mirror horizontal (lado): branch_side>0 => mirror en X local.
            need_mirror_x_local = branch_side > 0.0
            # Mirror vertical/convención: branch_along_main<0 => mirror en Y local.
            need_mirror_y_local = branch_along_main < 0.0
            if need_mirror_y_local:
                warn_key = (vkey, di_main_in, di_main_out, di_branch)
                if warn_key not in _CABAL_WARNING_SHOWN_KEYS:
                    _CABAL_WARNING_SHOWN_KEYS.add(warn_key)
                    try:
                        PythonUtility.ShowMessageBox(
                            "caval sin sentido sera creado",
                            PythonUtility.MB_OK,
                        )
                    except Exception:
                        pass
            # (DEBUG) branch_along_main y branch_side ayudan a verificar estabilidad del mirror

        if DEBUG_TE:
            print(
                "[DBG TE] node=%s plane=%s ang=%.1f° main=(%.3f,%.3f,%.3f) branch=(%.3f,%.3f,%.3f) "
                "branch_in_plane=%s branch_elevated=%s branch_along_main=%.3f branch_side=%.3f "
                "mirrors(x=%s y=%s z=%s) type_te=%s di_in=%s di_out=%s di_branch=%s"
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
                    branch_along_main,
                    branch_side,
                    str(need_mirror_x_local),
                    str(need_mirror_y_local),
                    str(need_mirror_z_local),
                    str(type_te),
                    str(di_main_in),
                    str(di_main_out),
                    str(di_branch),
                )
            )

        bif_y110_pluvial_only = (
            di_main_in == 110
            and di_main_out == 110
            and di_branch == 110
            and not _any_conn_fecal_system(segment_groups, conns)
        )
        y110_bif_script_variant = "pluvial"
        if di_main_in == 110 and di_main_out == 110 and di_branch == 110:
            if _all_conn_fecal_system(segment_groups, conns):
                y110_bif_script_variant = "fecal"
        out[vkey] = {
            "center_pt": (cx, cy, cz),
            "distribution_type": te_dist_type,
            "d_main_in": di_main_in,
            "d_main_out": di_main_out,
            "d_branch": di_branch,
            "model_mirror_x": mirror_x,
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
            "bif_y110_pluvial_only": bif_y110_pluvial_only,
            "y110_bif_script_variant": y110_bif_script_variant,
        }

    return out
