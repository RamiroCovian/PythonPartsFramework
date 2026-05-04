# -*- coding: utf-8 -*-
"""
Orientación de codos 90° (IS/TD) replicando la lógica de fontaneria.py.

Esta utilidad se basa en 3 puntos: p_prev -> p_mid -> p_next, y opcionalmente
en reference_orientation_angle (rad) para los casos especiales (diagonales, etc.).
"""
from __future__ import annotations

import math
import NemAll_Python_Geometry as AllplanGeo


def _normalize_angle_rad_pi(angle_rad: float) -> float:
    while angle_rad > math.pi:
        angle_rad -= 2.0 * math.pi
    while angle_rad < -math.pi:
        angle_rad += 2.0 * math.pi
    return angle_rad


def _normalize_angle_deg_180(angle_deg: float) -> float:
    while angle_deg > 180.0:
        angle_deg -= 360.0
    while angle_deg < -180.0:
        angle_deg += 360.0
    return angle_deg


def _is_close_angle_deg(angle_deg: float, target_deg: float, tol_deg: float = 10.0) -> bool:
    delta = (angle_deg - target_deg + 180.0) % 360.0 - 180.0
    return abs(delta) <= tol_deg


def _dir_from_delta(dx: float, dy: float, eps: float = 1e-6) -> str:
    """Devuelve 'E','W','N','S' según dx/dy (tramos ortogonales o dominantes)."""
    if abs(dx) > abs(dy):
        return "E" if dx > eps else "W"
    return "N" if dy > eps else "S"


def _normalize_reference_angle_deg(angle_deg: float) -> float:
    """
    Normaliza ángulos equivalentes para la lógica de diagonales:
    -45° (315°) -> 135° para que sigan la misma rama de decisión.
    """
    if angle_deg > 180.0:
        angle_deg -= 360.0
    if angle_deg < -180.0:
        angle_deg += 360.0
    if -55.0 <= angle_deg <= -35.0:
        return 135.0
    return angle_deg


def _compute_reference_yaw_for_vertical_elbow(
    *,
    seg1_vert: bool,
    seg2_vert: bool,
    h_dir: str,
    hx: float,
    hy: float,
    reference_orientation_angle: float,
) -> float:
    """
    Port de la excepción de rotación adicional de fontaneria.py (L2337+).
    Devuelve el yaw adicional a aplicar en Z para codos verticales.
    """
    prev_angle_xy = float(reference_orientation_angle)
    h_angle = math.atan2(hy, hx)
    h_angle_deg = math.degrees(h_angle)
    ref_deg_raw = math.degrees(reference_orientation_angle)

    if seg1_vert and not seg2_vert:
        adjustment_angle = 0.0
        if h_dir == "W":
            ref_deg_cmp = _normalize_angle_deg_180(ref_deg_raw)
            # 225/-135 se comparan como 45 para usar la misma rama.
            if _is_close_angle_deg(ref_deg_cmp, 225.0) or _is_close_angle_deg(ref_deg_cmp, -135.0):
                ref_deg_cmp = 45.0
            h_deg_norm = _normalize_angle_deg_180(h_angle_deg)
            if _is_close_angle_deg(ref_deg_cmp, 45.0) and _is_close_angle_deg(h_deg_norm, -135.0):
                adjustment_angle = 0.0
            elif abs(h_angle_deg) > 135.0 and abs(h_angle_deg) <= 180.0:
                adjustment_angle = math.pi
        elif h_dir == "N":
            ref_norm = _normalize_reference_angle_deg(ref_deg_raw)
            h_norm = _normalize_reference_angle_deg(h_angle_deg)
            if _is_close_angle_deg(ref_norm, 135.0) or _is_close_angle_deg(h_norm, 135.0):
                adjustment_angle = -math.pi / 2.0
            else:
                adjustment_angle = math.pi
        elif h_dir == "S":
            ref_norm = _normalize_reference_angle_deg(ref_deg_raw)
            h_norm = _normalize_reference_angle_deg(h_angle_deg)
            if _is_close_angle_deg(ref_norm, 135.0) and _is_close_angle_deg(h_norm, 135.0):
                adjustment_angle = -math.pi / 2.0
            elif _is_close_angle_deg(h_norm, 135.0):
                adjustment_angle = math.pi / 2.0
            else:
                adjustment_angle = math.pi

        if abs(adjustment_angle) > 1e-6:
            prev_angle_xy = _normalize_angle_rad_pi(prev_angle_xy + adjustment_angle)

        # Ajuste adicional de +180° para referencias ~315/-45 y ~225/-135.
        if _is_close_angle_deg(ref_deg_raw, 315.0) or _is_close_angle_deg(ref_deg_raw, -45.0):
            prev_angle_xy = _normalize_angle_rad_pi(prev_angle_xy + math.pi)
        elif _is_close_angle_deg(ref_deg_raw, 225.0) or _is_close_angle_deg(ref_deg_raw, -135.0):
            prev_angle_xy = _normalize_angle_rad_pi(prev_angle_xy + math.pi)

    elif seg2_vert and not seg1_vert:
        if h_dir == "N":
            ref_norm = _normalize_reference_angle_deg(ref_deg_raw)
            h_norm = _normalize_reference_angle_deg(h_angle_deg)
            if _is_close_angle_deg(ref_norm, 135.0) or _is_close_angle_deg(h_norm, 135.0):
                prev_angle_xy = _normalize_angle_rad_pi(prev_angle_xy - (math.pi / 2.0))
        elif h_dir == "S":
            prev_angle_xy = _normalize_angle_rad_pi(prev_angle_xy - (math.pi / 2.0))

        if _is_close_angle_deg(ref_deg_raw, 315.0) or _is_close_angle_deg(ref_deg_raw, -45.0):
            prev_angle_xy = _normalize_angle_rad_pi(prev_angle_xy + math.pi)
        elif _is_close_angle_deg(ref_deg_raw, 225.0) or _is_close_angle_deg(ref_deg_raw, -135.0):
            prev_angle_xy = _normalize_angle_rad_pi(prev_angle_xy + math.pi)

    return prev_angle_xy


def apply_elbow_transform(
    brep,
    p_prev: AllplanGeo.Point3D,
    p_mid: AllplanGeo.Point3D,
    p_next: AllplanGeo.Point3D,
    reference_orientation_angle: float | None = None,
) -> object:
    """
    Aplica a un BRep de codo las rotaciones necesarias para orientarlo siguiendo
    los tramos p_prev->p_mid (entrada) y p_mid->p_next (salida).

    Devuelve el brep transformado (sin traslación final al mundo; eso lo hace el caller).
    """
    eps = 1e-6

    # deltas salida (mid->next)
    dx = p_next.X - p_mid.X
    dy = p_next.Y - p_mid.Y
    dz = p_next.Z - p_mid.Z

    # deltas entrada (prev->mid)
    px = p_mid.X - p_prev.X
    py = p_mid.Y - p_prev.Y
    pz = p_mid.Z - p_prev.Z

    seg1_vert = abs(px) < eps and abs(py) < eps and abs(pz) > eps
    seg2_vert = abs(dx) < eps and abs(dy) < eps and abs(dz) > eps

    # ------------------------------------------------------------------
    # CASO 1: Giro vertical (un tramo horizontal + uno vertical)
    # Portado del enfoque de fontaneria: mapa explícito por dirección.
    # ------------------------------------------------------------------
    if seg1_vert or seg2_vert:
        # normalizar: hx/hy del tramo horizontal, v_dz del vertical
        if seg2_vert:
            v_dz = dz
            hx, hy = px, py
        else:
            v_dz = pz
            hx, hy = dx, dy

        h_len = math.hypot(hx, hy)
        if h_len < eps:
            return brep
        hx /= h_len
        hy /= h_len

        h_dir = _dir_from_delta(hx, hy, eps)
        v_dir = "U" if v_dz > 0 else "D"

        # (axis_code, yaw_Z_rad, rot_vert_rad)
        # Mapeo equivalente al de fontaneria.py para codos verticales.
        vertical_map: dict[tuple[str, str], tuple[str, float, float]] = {
            ("E", "U"): ("X", -math.pi / 2.0, math.pi / 2.0),
            ("E", "D"): ("X", -math.pi / 2.0, -math.pi / 2.0),
            ("W", "U"): ("X", math.pi / 2.0, -math.pi / 2.0),
            ("W", "D"): ("X", math.pi / 2.0, math.pi / 2.0),
            ("N", "U"): ("Y", 0.0, -math.pi / 2.0),
            ("N", "D"): ("Y", 0.0, math.pi / 2.0),
            ("S", "U"): ("Y", math.pi, math.pi / 2.0),
            ("S", "D"): ("Y", math.pi, -math.pi / 2.0),
        }

        axis_code, ang_h, ang_v = vertical_map.get(
            (h_dir, v_dir),
            ("X", math.atan2(hy, hx) - math.pi / 2.0, math.pi / 2.0 if v_dz > 0 else -math.pi / 2.0),
        )

        print(
            f"[ELBOW][V] h_dir={h_dir} v_dir={v_dir} "
            f"axis={axis_code} ang_h={math.degrees(ang_h):.2f}° ang_v={math.degrees(ang_v):.2f}° "
            f"seg1_vert={seg1_vert} seg2_vert={seg2_vert}"
        )

        # Igual que en fontaneria (base): cuando el vertical es el primero
        # se suma 180° en planta.
        if seg1_vert and not seg2_vert:
            ang_h += math.pi

        # Rotación Z adicional (prev_angle_xy), como en fontaneria.py:
        # se aplica ANTES de la vertical y horizontal.
        prev_angle_xy = 0.0
        if reference_orientation_angle is not None:
            prev_angle_xy = _compute_reference_yaw_for_vertical_elbow(
                seg1_vert=seg1_vert,
                seg2_vert=seg2_vert,
                h_dir=h_dir,
                hx=hx,
                hy=hy,
                reference_orientation_angle=reference_orientation_angle,
            )
        elif seg2_vert:
            # Fallback: usar el ángulo del tramo horizontal que llega al codo.
            prev_angle_xy = _normalize_angle_rad_pi(math.atan2(hy, hx))
        elif seg1_vert:
            # Fallback: usar el ángulo del tramo horizontal que sale del codo.
            prev_angle_xy = _normalize_angle_rad_pi(math.atan2(hy, hx))

        # Port parcial de fontaneria: para direcciones cardinales, NO aplicar
        # rotación Z adicional (evita sobre-rotar el codo en V<->H ortogonales).
        prev_angle_deg = abs(math.degrees(prev_angle_xy))
        is_cardinal = (
            abs(prev_angle_deg - 0.0) < 5.0
            or abs(prev_angle_deg - 90.0) < 5.0
            or abs(prev_angle_deg - 180.0) < 5.0
        )
        if is_cardinal:
            prev_angle_xy = 0.0

        # Rz adicional (si aplica)
        mat_z_rot = None
        if abs(prev_angle_xy) > 1e-6:
            axis_z_prev = AllplanGeo.Line3D(
                AllplanGeo.Point3D(0, 0, 0),
                AllplanGeo.Point3D(0, 0, 1),
            )
            mat_z_rot = AllplanGeo.Matrix3D()
            mat_z_rot.SetRotation(axis_z_prev, AllplanGeo.Angle(prev_angle_xy))

        # Rotación vertical alrededor de X o Y (mismo criterio de fontaneria.py)
        if axis_code == "Y":
            axis_vert = AllplanGeo.Line3D(
                AllplanGeo.Point3D(0, 0, 0), AllplanGeo.Point3D(0, 1, 0)
            )
        else:
            axis_vert = AllplanGeo.Line3D(
                AllplanGeo.Point3D(0, 0, 0), AllplanGeo.Point3D(-1, 0, 0)
            )
        mat_v = AllplanGeo.Matrix3D()
        mat_v.SetRotation(axis_vert, AllplanGeo.Angle(ang_v))

        # Rotación horizontal en planta
        axis_z = AllplanGeo.Line3D(
            AllplanGeo.Point3D(0, 0, 0), AllplanGeo.Point3D(0, 0, 1)
        )
        mat_h = AllplanGeo.Matrix3D()
        mat_h.SetRotation(axis_z, AllplanGeo.Angle(ang_h))

        # Composición igual que fontaneria:
        # mat_h * mat_v * mat_z_rot => aplica primero mat_z_rot, luego mat_v, luego mat_h.
        mat = mat_h * mat_v * mat_z_rot if mat_z_rot is not None else mat_h * mat_v
        brep = AllplanGeo.Transform(brep, mat)

        return brep

    # ------------------------------------------------------------------
    # CASO 2 — Giro horizontal (XY, XZ o YZ, independiente del sentido)
    # Portado 1:1 de fontaneria.py (_create_elbow, CASO 2A/2B/2C)
    # ------------------------------------------------------------------
    d_prev_x = p_mid.X - p_prev.X
    d_prev_y = p_mid.Y - p_prev.Y
    d_prev_z = p_mid.Z - p_prev.Z
    d_next_x = p_next.X - p_mid.X
    d_next_y = p_next.Y - p_mid.Y
    d_next_z = p_next.Z - p_mid.Z

    prev_y_magnitude = abs(d_prev_y)
    next_y_magnitude = abs(d_next_y)
    prev_x_magnitude = abs(d_prev_x)
    next_x_magnitude = abs(d_next_x)

    in_xz_plane = (prev_y_magnitude < eps and next_y_magnitude < eps) or (
        prev_y_magnitude < 0.1 * max(abs(d_prev_x), abs(d_prev_z), eps)
        and next_y_magnitude < 0.1 * max(abs(d_next_x), abs(d_next_z), eps)
    )

    in_yz_plane = (prev_x_magnitude < eps and next_x_magnitude < eps) or (
        prev_x_magnitude < 0.1 * max(abs(d_prev_y), abs(d_prev_z), eps)
        and next_x_magnitude < 0.1 * max(abs(d_next_y), abs(d_next_z), eps)
    )

    mat = AllplanGeo.Matrix3D()

    if in_xz_plane:
        # CASO 2A — Giro en el plano XZ
        angle_prev = math.atan2(d_prev_z, d_prev_x)
        angle_next = math.atan2(d_next_z, d_next_x)
        cross = d_prev_x * d_next_z - d_prev_z * d_next_x

        if abs(cross) < 1e-6:
            angle = angle_next
            needs_mirror = False
        elif cross < 0:
            angle = angle_next
            needs_mirror = False
        else:
            angle = angle_prev
            needs_mirror = True

        while angle < 0:
            angle += 2 * math.pi
        while angle >= 2 * math.pi:
            angle -= 2 * math.pi

        print(
            f"[ELBOW] plano=XZ d_prev=({d_prev_x:.3f},{d_prev_z:.3f}) "
            f"d_next=({d_next_x:.3f},{d_next_z:.3f})"
        )
        print(
            f"[ELBOW] XZ angle_prev={math.degrees(angle_prev):.2f}° "
            f"angle_next={math.degrees(angle_next):.2f}° "
            f"cross={cross:.6f} final={math.degrees(angle):.2f}° mirror={needs_mirror}"
        )

        # Preparación XY->XZ: rotación alrededor de X
        axis_x = AllplanGeo.Line3D(AllplanGeo.Point3D(0, 0, 0), AllplanGeo.Point3D(1, 0, 0))
        mat_prep = AllplanGeo.Matrix3D()
        mat_prep.SetRotation(axis_x, AllplanGeo.Angle(-math.pi / 2.0))

        # Orientación alrededor de Y
        axis_y = AllplanGeo.Line3D(AllplanGeo.Point3D(0, 0, 0), AllplanGeo.Point3D(0, 1, 0))
        mat_rot = AllplanGeo.Matrix3D()
        mat_rot.SetRotation(axis_y, AllplanGeo.Angle(angle))

        mat = mat_rot * mat_prep
        if needs_mirror:
            mirror_mat = AllplanGeo.Matrix3D()
            mirror_mat.SetRotation(axis_y, AllplanGeo.Angle(math.pi))
            mat = mat * mirror_mat

    elif in_yz_plane:
        # CASO 2B — Giro en el plano YZ
        angle_prev = math.atan2(d_prev_z, d_prev_y)
        angle_next = math.atan2(d_next_z, d_next_y)
        cross = d_prev_y * d_next_z - d_prev_z * d_next_y

        if abs(cross) < 1e-6:
            angle = angle_next
            needs_mirror = False
        elif cross < 0:
            angle = angle_next
            needs_mirror = False
        else:
            angle = angle_prev
            needs_mirror = True

        while angle < 0:
            angle += 2 * math.pi
        while angle >= 2 * math.pi:
            angle -= 2 * math.pi

        print(
            f"[ELBOW] plano=YZ d_prev=({d_prev_y:.3f},{d_prev_z:.3f}) "
            f"d_next=({d_next_y:.3f},{d_next_z:.3f})"
        )
        print(
            f"[ELBOW] YZ angle_prev={math.degrees(angle_prev):.2f}° "
            f"angle_next={math.degrees(angle_next):.2f}° "
            f"cross={cross:.6f} final={math.degrees(angle):.2f}° mirror={needs_mirror}"
        )

        # Preparación XY->YZ: rotación alrededor de Z
        axis_z = AllplanGeo.Line3D(AllplanGeo.Point3D(0, 0, 0), AllplanGeo.Point3D(0, 0, 1))
        mat_prep = AllplanGeo.Matrix3D()
        mat_prep.SetRotation(axis_z, AllplanGeo.Angle(math.pi / 2.0))

        # Orientación alrededor de X
        axis_x = AllplanGeo.Line3D(AllplanGeo.Point3D(0, 0, 0), AllplanGeo.Point3D(1, 0, 0))
        mat_rot = AllplanGeo.Matrix3D()
        mat_rot.SetRotation(axis_x, AllplanGeo.Angle(angle))

        mat = mat_rot * mat_prep
        if needs_mirror:
            mirror_mat = AllplanGeo.Matrix3D()
            mirror_mat.SetRotation(axis_x, AllplanGeo.Angle(math.pi))
            mat = mat * mirror_mat

    else:
        # CASO 2C — Giro en el plano XY (caso original)
        angle_prev = math.atan2(d_prev_y, d_prev_x)
        angle_next = math.atan2(d_next_y, d_next_x)
        cross = d_prev_x * d_next_y - d_prev_y * d_next_x

        if abs(cross) < 1e-6:
            angle = angle_next
            needs_mirror = False
        elif cross < 0:
            angle = angle_next
            needs_mirror = False
        else:
            angle = angle_prev
            needs_mirror = True

        while angle < 0:
            angle += 2 * math.pi
        while angle >= 2 * math.pi:
            angle -= 2 * math.pi

        print(
            f"[ELBOW] plano=XY d_prev=({d_prev_x:.3f},{d_prev_y:.3f}) "
            f"d_next=({d_next_x:.3f},{d_next_y:.3f})"
        )
        print(
            f"[ELBOW] XY angle_prev={math.degrees(angle_prev):.2f}° "
            f"angle_next={math.degrees(angle_next):.2f}° "
            f"cross={cross:.6f} final={math.degrees(angle):.2f}° mirror={needs_mirror}"
        )

        axis_z = AllplanGeo.Line3D(AllplanGeo.Point3D(0, 0, 0), AllplanGeo.Point3D(0, 0, 1))
        mat.SetRotation(axis_z, AllplanGeo.Angle(angle))

        if needs_mirror:
            mirror_mat = AllplanGeo.Matrix3D()
            mirror_mat.SetRotation(axis_z, AllplanGeo.Angle(math.pi))
            mat = mat * mirror_mat

    brep = AllplanGeo.Transform(brep, mat)
    return brep

