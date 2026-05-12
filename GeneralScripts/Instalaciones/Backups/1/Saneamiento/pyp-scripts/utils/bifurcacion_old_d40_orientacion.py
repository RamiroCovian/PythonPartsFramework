# -*- coding: utf-8 -*-
"""
Orientación + offset de bifurcaciones portadas desde Saneamiento_old:
- D40-D40: BIF40_* (Rx→Ry→Rz + offset rotado + traslación).
- D110-D110: mismas reglas (cross_z, vertical, base_rot_z) con BIFURCATION_* del viejo.

Solo se usa cuando el pipeline marca la TE en saneamiento; no sustituye fontanería/Agua.
"""
from __future__ import annotations

import math
from typing import Tuple

import NemAll_Python_Geometry as AllplanGeo

# ── Portado literal de Saneamiento_old (BIF40_*) ─────────────────────────────

BIF40_OFFSET_X_LEFT = 20.0
BIF40_OFFSET_Y_LEFT = 100.0
BIF40_OFFSET_Z_LEFT = -20.0

BIF40_ROT_X_LEFT = 180.0
BIF40_ROT_Y_LEFT = 0.0
BIF40_ROT_Z_LEFT = 90.0

BIF40_OFFSET_X_RIGHT = 20.0
BIF40_OFFSET_Y_RIGHT = 100.0
BIF40_OFFSET_Z_RIGHT = -20.0

BIF40_ROT_X_RIGHT = 0.0
BIF40_ROT_Y_RIGHT = 0.0
BIF40_ROT_Z_RIGHT = -90.0

BIF40_VERTICAL_ROT_X_LEFT = -270.0
BIF40_VERTICAL_ROT_Y_LEFT = 0.0
BIF40_VERTICAL_ROT_Z_LEFT = -180.0

BIF40_VERTICAL_ROT_X_RIGHT = 270.0
BIF40_VERTICAL_ROT_Y_RIGHT = 0.0
BIF40_VERTICAL_ROT_Z_RIGHT = 180.0

# ── Saneamiento_old: bifurcación D110-D110 (BIFURCATION_* en el script antiguo) ──

BIF110_D110_OFFSET_X_LEFT = 55.0
BIF110_D110_OFFSET_Y_LEFT = 170.0
BIF110_D110_OFFSET_Z_LEFT = -55.0

BIF110_D110_ROT_X_LEFT = 180.0
BIF110_D110_ROT_Y_LEFT = 0.0
BIF110_D110_ROT_Z_LEFT = 90.0

BIF110_D110_OFFSET_X_RIGHT = 55.0
BIF110_D110_OFFSET_Y_RIGHT = 170.0
BIF110_D110_OFFSET_Z_RIGHT = -55.0

BIF110_D110_ROT_X_RIGHT = 0.0
BIF110_D110_ROT_Y_RIGHT = 0.0
BIF110_D110_ROT_Z_RIGHT = -90.0

BIF110_D110_VERTICAL_ROT_X_LEFT = -270.0
BIF110_D110_VERTICAL_ROT_Y_LEFT = 0.0
BIF110_D110_VERTICAL_ROT_Z_LEFT = -180.0

BIF110_D110_VERTICAL_ROT_X_RIGHT = 270.0
BIF110_D110_VERTICAL_ROT_Y_RIGHT = 0.0
BIF110_D110_VERTICAL_ROT_Z_RIGHT = 180.0


def _norm3(
    v: Tuple[float, float, float],
) -> Tuple[float, float, float] | None:
    x, y, z = float(v[0]), float(v[1]), float(v[2])
    n = math.hypot(x, math.hypot(y, z))
    if n < 1e-9:
        return None
    return (x / n, y / n, z / n)


def _rotate_offset_like_old(
    rot_x_deg: float,
    rot_y_deg: float,
    rot_z_deg: float,
    offset_x: float,
    offset_y: float,
    offset_z: float,
) -> Tuple[float, float, float]:
    rx = math.radians(rot_x_deg)
    ry = math.radians(rot_y_deg)
    rz = math.radians(rot_z_deg)
    ox, oy, oz = offset_x, offset_y, offset_z

    c = math.cos(rx)
    s = math.sin(rx)
    oy, oz = (oy * c - oz * s), (oy * s + oz * c)

    c = math.cos(ry)
    s = math.sin(ry)
    ox, oz = (ox * c + oz * s), (-ox * s + oz * c)

    c = math.cos(rz)
    s = math.sin(rz)
    ox, oy = (ox * c - oy * s), (ox * s + oy * c)

    return ox, oy, oz


def compute_d40_d40_rotations_and_rotated_offset(
    main_vec: Tuple[float, float, float],
    branch_vec: Tuple[float, float, float],
) -> Tuple[float, float, float, float, float, float] | None:
    """
    Devuelve (rot_x°, rot_y°, rot_z°, ox, oy, oz) con (ox,oy,oz) el offset local
    ya rotado con la misma secuencia X→Y→Z que el sólido (como Saneamiento_old).
    """
    main = _norm3(main_vec)
    branch = _norm3(branch_vec)
    if main is None or branch is None:
        return None

    mx, my, mz = main
    bx, by, bz = branch

    dz_abs = abs(mz)
    dxy = math.hypot(mx, my)
    is_vertical = dz_abs > 0.707 and dxy < 0.707
    branch_going_up = bz > 0.0

    if is_vertical:
        cross_z = -bx
    else:
        cross_z = mx * by - my * bx

    angle_main = math.atan2(my, mx)
    base_rot_z = math.degrees(angle_main)

    if cross_z > 0:
        rot_x = BIF40_ROT_X_LEFT
        rot_y = BIF40_ROT_Y_LEFT
        rot_z = base_rot_z + BIF40_ROT_Z_LEFT
        if is_vertical:
            if branch_going_up:
                rot_x += BIF40_VERTICAL_ROT_X_LEFT
                rot_y += BIF40_VERTICAL_ROT_Y_LEFT
                rot_z += BIF40_VERTICAL_ROT_Z_LEFT
            else:
                rot_x += -BIF40_VERTICAL_ROT_X_LEFT
                rot_y += -BIF40_VERTICAL_ROT_Y_LEFT
                rot_z += -BIF40_VERTICAL_ROT_Z_LEFT
        offset_x = BIF40_OFFSET_X_LEFT
        offset_y = BIF40_OFFSET_Y_LEFT
        offset_z = BIF40_OFFSET_Z_LEFT
    else:
        rot_x = BIF40_ROT_X_RIGHT
        rot_y = BIF40_ROT_Y_RIGHT
        rot_z = base_rot_z + BIF40_ROT_Z_RIGHT
        if is_vertical:
            if branch_going_up:
                rot_x += BIF40_VERTICAL_ROT_X_RIGHT
                rot_y += BIF40_VERTICAL_ROT_Y_RIGHT
                rot_z += BIF40_VERTICAL_ROT_Z_RIGHT
            else:
                rot_x += -BIF40_VERTICAL_ROT_X_RIGHT
                rot_y += -BIF40_VERTICAL_ROT_Y_RIGHT
                rot_z += -BIF40_VERTICAL_ROT_Z_RIGHT
        offset_x = BIF40_OFFSET_X_RIGHT
        offset_y = BIF40_OFFSET_Y_RIGHT
        offset_z = BIF40_OFFSET_Z_RIGHT

    ox, oy, oz = _rotate_offset_like_old(rot_x, rot_y, rot_z, offset_x, offset_y, offset_z)
    return (rot_x, rot_y, rot_z, ox, oy, oz)


def try_apply_old_d40_bif_transform(
    brep,
    vertex_x: float,
    vertex_y: float,
    vertex_z: float,
    main_vec: Tuple[float, float, float],
    branch_vec: Tuple[float, float, float],
    extra_dx: float = 0.0,
    extra_dy: float = 0.0,
    extra_dz: float = 0.0,
):
    """
    Rota el BRep en el origen (Rx, Ry, Rz) y traslada a vértice + offset rotado
    + traslación extra en mm (ejes mundo), p. ej. desde geo_handler.BIF_Y40_PLACEMENT_OFFSET_*.
    Devuelve el BRep transformado o None si no aplica (vectores inválidos).
    """
    comp = compute_d40_d40_rotations_and_rotated_offset(main_vec, branch_vec)
    if comp is None:
        return None
    rot_x, rot_y, rot_z, ox, oy, oz = comp

    if abs(rot_x) > 1e-6:
        rot_matrix_x = AllplanGeo.Matrix3D()
        x_axis = AllplanGeo.Line3D(0, 0, 0, 1, 0, 0)
        rot_matrix_x.SetRotation(x_axis, AllplanGeo.Angle(math.radians(rot_x)))
        brep = AllplanGeo.Transform(brep, rot_matrix_x)

    if abs(rot_y) > 1e-6:
        rot_matrix_y = AllplanGeo.Matrix3D()
        y_axis = AllplanGeo.Line3D(0, 0, 0, 0, 1, 0)
        rot_matrix_y.SetRotation(y_axis, AllplanGeo.Angle(math.radians(rot_y)))
        brep = AllplanGeo.Transform(brep, rot_matrix_y)

    if abs(rot_z) > 1e-6:
        rot_matrix_z = AllplanGeo.Matrix3D()
        z_axis = AllplanGeo.Line3D(0, 0, 0, 0, 0, 1)
        rot_matrix_z.SetRotation(z_axis, AllplanGeo.Angle(math.radians(rot_z)))
        brep = AllplanGeo.Transform(brep, rot_matrix_z)

    trans_m = AllplanGeo.Matrix3D()
    trans_m.SetTranslation(
        AllplanGeo.Vector3D(
            vertex_x + ox + float(extra_dx),
            vertex_y + oy + float(extra_dy),
            vertex_z + oz + float(extra_dz),
        )
    )
    brep = AllplanGeo.Transform(brep, trans_m)
    return brep


def compute_d110_d110_rotations_and_rotated_offset(
    main_vec: Tuple[float, float, float],
    branch_vec: Tuple[float, float, float],
) -> Tuple[float, float, float, float, float, float] | None:
    """
    Igual que D40-D40 pero con constantes D110-D110 de Saneamiento_old
    (rama izq./der. por cross_z; extras si troncal vertical).
    """
    main = _norm3(main_vec)
    branch = _norm3(branch_vec)
    if main is None or branch is None:
        return None

    mx, my, mz = main
    bx, by, bz = branch

    dz_abs = abs(mz)
    dxy = math.hypot(mx, my)
    is_vertical = dz_abs > 0.707 and dxy < 0.707
    branch_going_up = bz > 0.0

    if is_vertical:
        cross_z = -bx
    else:
        cross_z = mx * by - my * bx

    angle_main = math.atan2(my, mx)
    base_rot_z = math.degrees(angle_main)

    if cross_z > 0:
        rot_x = BIF110_D110_ROT_X_LEFT
        rot_y = BIF110_D110_ROT_Y_LEFT
        rot_z = base_rot_z + BIF110_D110_ROT_Z_LEFT
        if is_vertical:
            if branch_going_up:
                rot_x += BIF110_D110_VERTICAL_ROT_X_LEFT
                rot_y += BIF110_D110_VERTICAL_ROT_Y_LEFT
                rot_z += BIF110_D110_VERTICAL_ROT_Z_LEFT
            else:
                rot_x += -BIF110_D110_VERTICAL_ROT_X_LEFT
                rot_y += -BIF110_D110_VERTICAL_ROT_Y_LEFT
                rot_z += -BIF110_D110_VERTICAL_ROT_Z_LEFT
        offset_x = BIF110_D110_OFFSET_X_LEFT
        offset_y = BIF110_D110_OFFSET_Y_LEFT
        offset_z = BIF110_D110_OFFSET_Z_LEFT
    else:
        rot_x = BIF110_D110_ROT_X_RIGHT
        rot_y = BIF110_D110_ROT_Y_RIGHT
        rot_z = base_rot_z + BIF110_D110_ROT_Z_RIGHT
        if is_vertical:
            if branch_going_up:
                rot_x += BIF110_D110_VERTICAL_ROT_X_RIGHT
                rot_y += BIF110_D110_VERTICAL_ROT_Y_RIGHT
                rot_z += BIF110_D110_VERTICAL_ROT_Z_RIGHT
            else:
                rot_x += -BIF110_D110_VERTICAL_ROT_X_RIGHT
                rot_y += -BIF110_D110_VERTICAL_ROT_Y_RIGHT
                rot_z += -BIF110_D110_VERTICAL_ROT_Z_RIGHT
        offset_x = BIF110_D110_OFFSET_X_RIGHT
        offset_y = BIF110_D110_OFFSET_Y_RIGHT
        offset_z = BIF110_D110_OFFSET_Z_RIGHT

    ox, oy, oz = _rotate_offset_like_old(rot_x, rot_y, rot_z, offset_x, offset_y, offset_z)
    return (rot_x, rot_y, rot_z, ox, oy, oz)


def try_apply_old_d110_d110_bif_transform(
    brep,
    vertex_x: float,
    vertex_y: float,
    vertex_z: float,
    main_vec: Tuple[float, float, float],
    branch_vec: Tuple[float, float, float],
    extra_dx: float = 0.0,
    extra_dy: float = 0.0,
    extra_dz: float = 0.0,
):
    comp = compute_d110_d110_rotations_and_rotated_offset(main_vec, branch_vec)
    if comp is None:
        return None
    rot_x, rot_y, rot_z, ox, oy, oz = comp

    if abs(rot_x) > 1e-6:
        rot_matrix_x = AllplanGeo.Matrix3D()
        x_axis = AllplanGeo.Line3D(0, 0, 0, 1, 0, 0)
        rot_matrix_x.SetRotation(x_axis, AllplanGeo.Angle(math.radians(rot_x)))
        brep = AllplanGeo.Transform(brep, rot_matrix_x)

    if abs(rot_y) > 1e-6:
        rot_matrix_y = AllplanGeo.Matrix3D()
        y_axis = AllplanGeo.Line3D(0, 0, 0, 0, 1, 0)
        rot_matrix_y.SetRotation(y_axis, AllplanGeo.Angle(math.radians(rot_y)))
        brep = AllplanGeo.Transform(brep, rot_matrix_y)

    if abs(rot_z) > 1e-6:
        rot_matrix_z = AllplanGeo.Matrix3D()
        z_axis = AllplanGeo.Line3D(0, 0, 0, 0, 0, 1)
        rot_matrix_z.SetRotation(z_axis, AllplanGeo.Angle(math.radians(rot_z)))
        brep = AllplanGeo.Transform(brep, rot_matrix_z)

    trans_m = AllplanGeo.Matrix3D()
    trans_m.SetTranslation(
        AllplanGeo.Vector3D(
            vertex_x + ox + float(extra_dx),
            vertex_y + oy + float(extra_dy),
            vertex_z + oz + float(extra_dz),
        )
    )
    brep = AllplanGeo.Transform(brep, trans_m)
    return brep
