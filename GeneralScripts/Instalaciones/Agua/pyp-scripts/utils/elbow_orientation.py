# -*- coding: utf-8 -*-
"""
Orientación de codos 90° (IS/TD) replicando la lógica de fontaneria.py.

Esta utilidad se basa en 3 puntos: p_prev -> p_mid -> p_next, y opcionalmente
en reference_orientation_angle (rad) para los casos especiales (diagonales, etc.).
"""
from __future__ import annotations

import math
import NemAll_Python_Geometry as AllplanGeo


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

        # Ajuste: si el vertical es el PRIMERO, sumar 180° en planta (como fontaneria)
        if seg1_vert and not seg2_vert:
            ang_h += math.pi

        # Rotación adicional por reference_orientation_angle (diagonales y casos especiales)
        if reference_orientation_angle is not None:
            ref_deg = math.degrees(reference_orientation_angle)
            ref_deg_norm = _normalize_reference_angle_deg(ref_deg)
            # Para 315/-45 y 225/-135 aplicar +180° adicional (portado de fontaneria)
            if abs(ref_deg + 45.0) < 10.0 or abs(ref_deg - 315.0) < 10.0:
                reference_orientation_angle += math.pi
            if abs(ref_deg - 225.0) < 10.0 or abs(ref_deg + 135.0) < 10.0:
                reference_orientation_angle += math.pi
            # En vertical, aplicamos esta referencia como yaw adicional
            ang_h += reference_orientation_angle

        # 1) Yaw en Z
        m = AllplanGeo.Matrix3D()
        m.Rotation(
            AllplanGeo.Line3D(0, 0, 0, 0, 0, 1),
            AllplanGeo.Angle(ang_h),
        )
        brep = AllplanGeo.Transform(brep, m)

        # 2) Rotación vertical alrededor del eje X o Y global (aprox consistente con fontaneria)
        axis = AllplanGeo.Line3D(0, 0, 0, 1, 0, 0) if axis_code == "X" else AllplanGeo.Line3D(0, 0, 0, 0, 1, 0)
        m = AllplanGeo.Matrix3D()
        m.Rotation(axis, AllplanGeo.Angle(ang_v))
        brep = AllplanGeo.Transform(brep, m)

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

        axis_z = AllplanGeo.Line3D(AllplanGeo.Point3D(0, 0, 0), AllplanGeo.Point3D(0, 0, 1))
        mat.SetRotation(axis_z, AllplanGeo.Angle(angle))

        if needs_mirror:
            mirror_mat = AllplanGeo.Matrix3D()
            mirror_mat.SetRotation(axis_z, AllplanGeo.Angle(math.pi))
            mat = mat * mirror_mat

    brep = AllplanGeo.Transform(brep, mat)
    return brep

