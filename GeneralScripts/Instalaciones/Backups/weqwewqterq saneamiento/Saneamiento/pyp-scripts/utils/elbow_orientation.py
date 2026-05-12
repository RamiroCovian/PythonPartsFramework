# -*- coding: utf-8 -*-
"""
Orientación de codos 90° (IS/TD) replicando la lógica de fontaneria.py.

Esta utilidad se basa en 3 puntos: p_prev -> p_mid -> p_next, y opcionalmente
en reference_orientation_angle (rad) para los casos especiales (diagonales, etc.).
"""
from __future__ import annotations

import math
import NemAll_Python_Geometry as AllplanGeo


def apply_elbow_transform(
    brep,
    p_prev: AllplanGeo.Point3D,
    p_mid: AllplanGeo.Point3D,
    p_next: AllplanGeo.Point3D,
    reference_orientation_angle: float | None = None,
    elbow_kind: str | None = None,
) -> object:
    """
    Aplica a un BRep de codo las rotaciones necesarias para orientarlo siguiendo
    los tramos p_prev->p_mid (entrada) y p_mid->p_next (salida).

    Devuelve el brep transformado (sin traslación final al mundo; eso lo hace el caller).
    """
    _ = reference_orientation_angle  # Conservado por compatibilidad de firma.
    eps = 1e-6
    mat = AllplanGeo.Matrix3D()

    dx_prev = p_mid.X - p_prev.X
    dy_prev = p_mid.Y - p_prev.Y
    dz_prev = p_mid.Z - p_prev.Z

    dx_next = p_next.X - p_mid.X
    dy_next = p_next.Y - p_mid.Y
    dz_next = p_next.Z - p_mid.Z

    dist_xy_prev = (dx_prev * dx_prev + dy_prev * dy_prev) ** 0.5
    dist_xz_prev = (dx_prev * dx_prev + dz_prev * dz_prev) ** 0.5
    dist_yz_prev = (dy_prev * dy_prev + dz_prev * dz_prev) ** 0.5
    dist_xy_next = (dx_next * dx_next + dy_next * dy_next) ** 0.5
    dist_xz_next = (dx_next * dx_next + dz_next * dz_next) ** 0.5
    dist_yz_next = (dy_next * dy_next + dz_next * dz_next) ** 0.5

    in_xz_plane = (
        (abs(dy_prev) < eps or abs(dy_prev) < 0.1 * max(abs(dx_prev), abs(dz_prev), eps))
        and (abs(dy_next) < eps or abs(dy_next) < 0.1 * max(abs(dx_next), abs(dz_next), eps))
        and (dist_xz_prev > eps and dist_xz_next > eps)
    )
    in_yz_plane = (
        (abs(dx_prev) < eps or abs(dx_prev) < 0.1 * max(abs(dy_prev), abs(dz_prev), eps))
        and (abs(dx_next) < eps or abs(dx_next) < 0.1 * max(abs(dy_next), abs(dz_next), eps))
        and (dist_yz_prev > eps and dist_yz_next > eps)
    )

    if in_xz_plane:
        angle_prev = math.atan2(dz_prev, dx_prev)
        angle_next = math.atan2(dz_next, dx_next)
        cross = dx_prev * dz_next - dz_prev * dx_next
        needs_mirror = cross > 1e-6
        angle_rad = angle_prev + math.pi / 2.0
        while angle_rad > math.pi:
            angle_rad -= 2 * math.pi
        while angle_rad < -math.pi:
            angle_rad += 2 * math.pi

        axis_x = AllplanGeo.Line3D(AllplanGeo.Point3D(0, 0, 0), AllplanGeo.Point3D(1, 0, 0))
        axis_y = AllplanGeo.Line3D(AllplanGeo.Point3D(0, 0, 0), AllplanGeo.Point3D(0, 1, 0))
        axis_z = AllplanGeo.Line3D(AllplanGeo.Point3D(0, 0, 0), AllplanGeo.Point3D(0, 0, 1))

        rot_mat = AllplanGeo.Matrix3D()
        rot_mat.SetRotation(axis_y, AllplanGeo.Angle(angle_rad))
        mat = rot_mat

        if needs_mirror:
            mirror_mat = AllplanGeo.Matrix3D()
            mirror_mat.SetRotation(axis_y, AllplanGeo.Angle(math.pi))
            mat = mat * mirror_mat
        elif cross < -1e-6:
            mirror_z_mat = AllplanGeo.Matrix3D()
            mirror_z_mat.SetRotation(axis_z, AllplanGeo.Angle(math.pi))
            mat = mat * mirror_z_mat

        angle_prev_deg = math.degrees(angle_prev) % 360.0
        angle_next_deg = math.degrees(angle_next) % 360.0
        if needs_mirror:
            exit_after_transform_deg = (45.0 - angle_prev_deg) % 360.0
        else:
            exit_after_transform_deg = (225.0 - angle_prev_deg) % 360.0
        diff_deg = (angle_next_deg - exit_after_transform_deg) % 360.0
        if diff_deg > 180.0:
            diff_deg -= 360.0
        elif diff_deg <= -180.0:
            diff_deg += 360.0
        if abs(diff_deg) > 1e-3 and cross >= -1e-6:
            extra_y = AllplanGeo.Matrix3D()
            extra_y.SetRotation(axis_y, AllplanGeo.Angle(math.radians(-diff_deg)))
            mat = mat * extra_y

        # Caso solicitado:
        # En XZ y sentido horario (cross < 0) para codo 90°, NO aplicar corrección fija -45°.
        # El script del codo aplica -45° local; aquí lo anulamos con +45°.
        if (elbow_kind == "codo_90") and (cross < -1e-6):
            undo_local_corr = AllplanGeo.Matrix3D()
            undo_local_corr.SetRotation(axis_y, AllplanGeo.Angle(math.radians(45.0)))
            mat = mat * undo_local_corr

        mat_prep = AllplanGeo.Matrix3D()
        mat_prep.SetRotation(axis_x, AllplanGeo.Angle(-math.pi / 2.0))
        mat = mat_prep * mat

    elif in_yz_plane:
        angle_prev = math.atan2(dz_prev, dy_prev)
        angle_next = math.atan2(dz_next, dy_next)
        cross = dy_prev * dz_next - dz_prev * dy_next
        needs_mirror = cross > 1e-6
        angle_rad = angle_prev - math.pi / 2.0 + math.radians(+90.0)
        while angle_rad > math.pi:
            angle_rad -= 2 * math.pi
        while angle_rad < -math.pi:
            angle_rad += 2 * math.pi

        axis_x = AllplanGeo.Line3D(AllplanGeo.Point3D(0, 0, 0), AllplanGeo.Point3D(1, 0, 0))
        axis_y = AllplanGeo.Line3D(AllplanGeo.Point3D(0, 0, 0), AllplanGeo.Point3D(0, 1, 0))
        axis_z = AllplanGeo.Line3D(AllplanGeo.Point3D(0, 0, 0), AllplanGeo.Point3D(0, 0, 1))

        mat_tilt = AllplanGeo.Matrix3D()
        mat_tilt.SetRotation(axis_y, AllplanGeo.Angle(math.pi / 2.0))
        mat = mat_tilt

        rot_mat = AllplanGeo.Matrix3D()
        rot_mat.SetRotation(axis_x, AllplanGeo.Angle(angle_rad))
        mat = mat * rot_mat

        if needs_mirror:
            mirror_mat = AllplanGeo.Matrix3D()
            mirror_mat.SetRotation(axis_z, AllplanGeo.Angle(math.pi))
            mat = mat * mirror_mat

        angle_prev_deg = math.degrees(angle_prev) % 360.0
        angle_next_deg = math.degrees(angle_next) % 360.0
        if needs_mirror:
            exit_after_transform_deg = (225.0 - angle_prev_deg) % 360.0
        else:
            exit_after_transform_deg = (angle_prev_deg - 45.0) % 360.0
        diff_deg = (angle_next_deg - exit_after_transform_deg) % 360.0
        if diff_deg > 180.0:
            diff_deg -= 360.0
        elif diff_deg <= -180.0:
            diff_deg += 360.0
        if abs(diff_deg) > 1e-3:
            extra_x = AllplanGeo.Matrix3D()
            extra_x.SetRotation(axis_x, AllplanGeo.Angle(math.radians(diff_deg)))
            mat = mat * extra_x

    else:
        angle_prev = math.atan2(dy_prev, dx_prev)
        angle_next = math.atan2(dy_next, dx_next)
        cross = dx_prev * dy_next - dy_prev * dx_next
        angle_rad = angle_prev - math.pi / 2.0
        while angle_rad > math.pi:
            angle_rad -= 2 * math.pi
        while angle_rad < -math.pi:
            angle_rad += 2 * math.pi
        needs_mirror = cross > 1e-6

        axis_z = AllplanGeo.Line3D(AllplanGeo.Point3D(0, 0, 0), AllplanGeo.Point3D(0, 0, 1))
        rot_mat = AllplanGeo.Matrix3D()
        rot_mat.SetRotation(axis_z, AllplanGeo.Angle(angle_rad))
        mat = mat * rot_mat

        axis_y = AllplanGeo.Line3D(AllplanGeo.Point3D(0, 0, 0), AllplanGeo.Point3D(0, 1, 0))
        if needs_mirror:
            mirror_mat = AllplanGeo.Matrix3D()
            mirror_mat.SetRotation(axis_y, AllplanGeo.Angle(math.pi))
            mat = mat * mirror_mat

        angle_prev_deg = math.degrees(angle_prev) % 360.0
        angle_next_deg = math.degrees(angle_next) % 360.0
        if needs_mirror:
            exit_after_transform_deg = (225.0 - angle_prev_deg) % 360.0
        else:
            exit_after_transform_deg = (angle_prev_deg - 45.0) % 360.0
        diff_deg = (angle_next_deg - exit_after_transform_deg) % 360.0
        if diff_deg > 180.0:
            diff_deg -= 360.0
        elif diff_deg <= -180.0:
            diff_deg += 360.0
        if abs(diff_deg) > 1e-3:
            extra_z_rad = math.radians(diff_deg)
            extra_rot_mat = AllplanGeo.Matrix3D()
            extra_rot_mat.SetRotation(axis_z, AllplanGeo.Angle(extra_z_rad))
            mat = mat * extra_rot_mat

        dz_prev_abs = abs(dz_prev)
        dz_next_abs = abs(dz_next)
        plane_change_threshold = 0.3

        is_first_segment_vertical = (
            dz_prev_abs > plane_change_threshold * max(dist_xy_prev, eps)
            and dist_xy_prev < plane_change_threshold * max(dz_prev_abs, eps)
        )
        is_first_segment_vertical_minus_z = is_first_segment_vertical and dz_prev < 0
        is_second_segment_minus_y_plus_z = (
            dy_next < 0
            and dz_next > 0
            and abs(dx_next) < plane_change_threshold * max(abs(dy_next), abs(dz_next), eps)
        )
        is_second_segment_plus_y_plus_z = (
            dy_next > 0
            and dz_next > 0
            and abs(dx_next) < plane_change_threshold * max(abs(dy_next), abs(dz_next), eps)
        )
        is_second_segment_plus_y_minus_z = (
            dy_next > 0
            and dz_next < 0
            and abs(dx_next) < plane_change_threshold * max(abs(dy_next), abs(dz_next), eps)
        )
        is_second_segment_minus_y_minus_z = (
            dy_next < 0
            and dz_next < 0
            and abs(dx_next) < plane_change_threshold * max(abs(dy_next), abs(dz_next), eps)
        )

        is_first_segment_diagonal_yz = (
            abs(dx_prev) < plane_change_threshold * max(abs(dy_prev), abs(dz_prev), eps)
            and abs(dy_prev) > eps
            and abs(dz_prev) > eps
            and abs(abs(dy_prev) - abs(dz_prev)) < 0.5 * max(abs(dy_prev), abs(dz_prev))
        )
        is_second_segment_horizontal_y = (
            abs(dx_next) < plane_change_threshold * abs(dy_next)
            and abs(dz_next) < plane_change_threshold * abs(dy_next)
            and abs(dy_next) > eps
        )
        is_second_segment_vertical_z = (
            abs(dx_next) < plane_change_threshold * abs(dz_next)
            and abs(dy_next) < plane_change_threshold * abs(dz_next)
            and abs(dz_next) > eps
        )
        is_first_segment_diagonal_yz_plus_y_minus_z_mirror = (
            abs(dx_prev) < plane_change_threshold * max(abs(dy_prev), abs(dz_prev), eps)
            and abs(dy_prev) > eps
            and abs(dz_prev) > eps
            and abs(abs(dy_prev) - abs(dz_prev)) < 0.5 * max(abs(dy_prev), abs(dz_prev))
            and dy_prev > 0
            and dz_prev < 0
        )

        if is_first_segment_vertical and is_second_segment_minus_y_plus_z:
            axis_y_local = AllplanGeo.Line3D(AllplanGeo.Point3D(0, 0, 0), AllplanGeo.Point3D(0, 1, 0))
            rot_special = AllplanGeo.Matrix3D()
            rot_special.SetRotation(axis_y_local, AllplanGeo.Angle(-math.pi / 2.0))
            mat = mat * rot_special
        elif is_first_segment_vertical and is_second_segment_plus_y_plus_z:
            axis_y_local = AllplanGeo.Line3D(AllplanGeo.Point3D(0, 0, 0), AllplanGeo.Point3D(0, 1, 0))
            rot_special = AllplanGeo.Matrix3D()
            rot_special.SetRotation(axis_y_local, AllplanGeo.Angle(-math.pi / 2.0))
            mat = mat * rot_special
            axis_z_local = AllplanGeo.Line3D(AllplanGeo.Point3D(0, 0, 0), AllplanGeo.Point3D(0, 0, 1))
            mirror_z = AllplanGeo.Matrix3D()
            mirror_z.SetRotation(axis_z_local, AllplanGeo.Angle(math.pi))
            mat = mat * mirror_z
        elif is_first_segment_vertical_minus_z and is_second_segment_plus_y_minus_z:
            axis_y_local = AllplanGeo.Line3D(AllplanGeo.Point3D(0, 0, 0), AllplanGeo.Point3D(0, 1, 0))
            rot_special = AllplanGeo.Matrix3D()
            rot_special.SetRotation(axis_y_local, AllplanGeo.Angle(-math.pi / 2.0))
            mat = mat * rot_special
            axis_z_local = AllplanGeo.Line3D(AllplanGeo.Point3D(0, 0, 0), AllplanGeo.Point3D(0, 0, 1))
            mirror_z = AllplanGeo.Matrix3D()
            mirror_z.SetRotation(axis_z_local, AllplanGeo.Angle(math.pi))
            mat = mat * mirror_z
            axis_y_mirror = AllplanGeo.Line3D(AllplanGeo.Point3D(0, 0, 0), AllplanGeo.Point3D(0, 1, 0))
            mirror_y = AllplanGeo.Matrix3D()
            mirror_y.SetRotation(axis_y_mirror, AllplanGeo.Angle(math.pi))
            mat = mat * mirror_y
        elif is_first_segment_vertical_minus_z and is_second_segment_minus_y_minus_z:
            axis_y_90 = AllplanGeo.Line3D(AllplanGeo.Point3D(0, 0, 0), AllplanGeo.Point3D(0, 1, 0))
            rot_90_y = AllplanGeo.Matrix3D()
            rot_90_y.SetRotation(axis_y_90, AllplanGeo.Angle(math.pi / 2.0))
            mat = mat * rot_90_y
        elif is_first_segment_diagonal_yz and is_second_segment_horizontal_y:
            if dy_prev < 0 and dz_prev > 0 and dy_next < 0:
                axis_x_mid = AllplanGeo.Line3D(
                    AllplanGeo.Point3D(p_mid.X, p_mid.Y, p_mid.Z),
                    AllplanGeo.Point3D(p_mid.X + 1, p_mid.Y, p_mid.Z),
                )
                rot_x_135 = AllplanGeo.Matrix3D()
                rot_x_135.SetRotation(axis_x_mid, AllplanGeo.Angle(math.pi * 135.0 / 180.0))
                mat = mat * rot_x_135
                center_point = AllplanGeo.Point3D(p_mid.X, p_mid.Y, p_mid.Z)
                reflection_plane = AllplanGeo.Plane3D(center_point, AllplanGeo.Vector3D(1, 0, 0))
                mirror_reflection = AllplanGeo.Matrix3D()
                mirror_reflection.SetReflection(reflection_plane)
                mat = mat * mirror_reflection
                axis_x_rot = AllplanGeo.Line3D(
                    AllplanGeo.Point3D(p_mid.X, p_mid.Y, p_mid.Z),
                    AllplanGeo.Point3D(p_mid.X + 1, p_mid.Y, p_mid.Z),
                )
                rot_x_minus_180_plane = AllplanGeo.Matrix3D()
                rot_x_minus_180_plane.SetRotation(axis_x_rot, AllplanGeo.Angle(-math.pi))
                mat = mat * rot_x_minus_180_plane
            elif dy_prev > 0 and dz_prev > 0 and dy_next > 0:
                axis_x_mid = AllplanGeo.Line3D(
                    AllplanGeo.Point3D(p_mid.X, p_mid.Y, p_mid.Z),
                    AllplanGeo.Point3D(p_mid.X + 1, p_mid.Y, p_mid.Z),
                )
                rot_x_135 = AllplanGeo.Matrix3D()
                rot_x_135.SetRotation(axis_x_mid, AllplanGeo.Angle(math.pi * 135.0 / 180.0))
                mat = mat * rot_x_135
                center_point = AllplanGeo.Point3D(p_mid.X, p_mid.Y, p_mid.Z)
                reflection_plane = AllplanGeo.Plane3D(center_point, AllplanGeo.Vector3D(1, 0, 0))
                mirror_reflection = AllplanGeo.Matrix3D()
                mirror_reflection.SetReflection(reflection_plane)
                mat = mat * mirror_reflection
                axis_x_rot = AllplanGeo.Line3D(
                    AllplanGeo.Point3D(p_mid.X, p_mid.Y, p_mid.Z),
                    AllplanGeo.Point3D(p_mid.X + 1, p_mid.Y, p_mid.Z),
                )
                rot_x_minus_180_plane = AllplanGeo.Matrix3D()
                rot_x_minus_180_plane.SetRotation(axis_x_rot, AllplanGeo.Angle(-math.pi))
                mat = mat * rot_x_minus_180_plane
                reflection_plane_z = AllplanGeo.Plane3D(center_point, AllplanGeo.Vector3D(0, 0, 1))
                mirror_reflection_z = AllplanGeo.Matrix3D()
                mirror_reflection_z.SetReflection(reflection_plane_z)
                mat = mat * mirror_reflection_z
            elif dy_prev < 0 and dz_prev < 0 and dy_next < 0:
                axis_x_mid = AllplanGeo.Line3D(
                    AllplanGeo.Point3D(p_mid.X, p_mid.Y, p_mid.Z),
                    AllplanGeo.Point3D(p_mid.X + 1, p_mid.Y, p_mid.Z),
                )
                rot_x_135 = AllplanGeo.Matrix3D()
                rot_x_135.SetRotation(axis_x_mid, AllplanGeo.Angle(math.pi * -135.0 / 180.0))
                mat = mat * rot_x_135
                axis_x_rot = AllplanGeo.Line3D(
                    AllplanGeo.Point3D(p_mid.X, p_mid.Y, p_mid.Z),
                    AllplanGeo.Point3D(p_mid.X + 1, p_mid.Y, p_mid.Z),
                )
                rot_x_minus_180_plane = AllplanGeo.Matrix3D()
                rot_x_minus_180_plane.SetRotation(axis_x_rot, AllplanGeo.Angle(math.pi))
                mat = mat * rot_x_minus_180_plane
            elif dy_prev > 0 and dz_prev < 0 and dy_next > 0:
                axis_x_mid = AllplanGeo.Line3D(
                    AllplanGeo.Point3D(p_mid.X, p_mid.Y, p_mid.Z),
                    AllplanGeo.Point3D(p_mid.X + 1, p_mid.Y, p_mid.Z),
                )
                rot_x_135 = AllplanGeo.Matrix3D()
                rot_x_135.SetRotation(axis_x_mid, AllplanGeo.Angle(math.pi * 135.0 / 180.0))
                mat = mat * rot_x_135
                axis_x_rot = AllplanGeo.Line3D(
                    AllplanGeo.Point3D(p_mid.X, p_mid.Y, p_mid.Z),
                    AllplanGeo.Point3D(p_mid.X + 1, p_mid.Y, p_mid.Z),
                )
                rot_x_minus_180_plane = AllplanGeo.Matrix3D()
                rot_x_minus_180_plane.SetRotation(axis_x_rot, AllplanGeo.Angle(math.pi))
                mat = mat * rot_x_minus_180_plane
        elif is_first_segment_diagonal_yz and is_second_segment_vertical_z:
            axis_x_local = AllplanGeo.Line3D(AllplanGeo.Point3D(0, 0, 0), AllplanGeo.Point3D(1, 0, 0))
            rot_x_90 = AllplanGeo.Matrix3D()
            rot_x_90.SetRotation(axis_x_local, AllplanGeo.Angle(math.pi / 2.0))
            mat = mat * rot_x_90
            axis_y_mirror = AllplanGeo.Line3D(AllplanGeo.Point3D(0, 0, 0), AllplanGeo.Point3D(0, 1, 0))
            mirror_y = AllplanGeo.Matrix3D()
            mirror_y.SetRotation(axis_y_mirror, AllplanGeo.Angle(-math.pi / 4.0))
            mat = mat * mirror_y
            axis_z_local = AllplanGeo.Line3D(AllplanGeo.Point3D(0, 0, 0), AllplanGeo.Point3D(0, 0, 1))
            rot_z_minus_90 = AllplanGeo.Matrix3D()
            rot_z_minus_90.SetRotation(axis_z_local, AllplanGeo.Angle(-math.pi / 2.0))
            mat = mat * rot_z_minus_90
            if dy_prev > 0 and dz_prev < 0:
                axis_y_mirror_extra = AllplanGeo.Line3D(AllplanGeo.Point3D(0, 0, 0), AllplanGeo.Point3D(0, 1, 0))
                mirror_y_extra = AllplanGeo.Matrix3D()
                mirror_y_extra.SetRotation(axis_y_mirror_extra, AllplanGeo.Angle(math.pi))
                mat = mat * mirror_y_extra
            elif dy_prev < 0 and dz_prev > 0:
                axis_y_mirror_extra = AllplanGeo.Line3D(AllplanGeo.Point3D(0, 0, 0), AllplanGeo.Point3D(0, 1, 0))
                mirror_y_extra = AllplanGeo.Matrix3D()
                mirror_y_extra.SetRotation(axis_y_mirror_extra, AllplanGeo.Angle(math.pi))
                mat = mat * mirror_y_extra
        elif is_first_segment_diagonal_yz_plus_y_minus_z_mirror and is_second_segment_vertical_z:
            axis_y_mirror = AllplanGeo.Line3D(AllplanGeo.Point3D(0, 0, 0), AllplanGeo.Point3D(0, 1, 0))
            mirror_y = AllplanGeo.Matrix3D()
            mirror_y.SetRotation(axis_y_mirror, AllplanGeo.Angle(math.pi))
            mat = mat * mirror_y

        is_horizontal_to_vertical = (
            dz_prev_abs < plane_change_threshold * dist_xy_prev
            and dz_next_abs > plane_change_threshold * dist_xy_next
        )
        is_vertical_to_horizontal = (
            dz_prev_abs > plane_change_threshold * dist_xy_prev
            and dz_next_abs < plane_change_threshold * dist_xy_next
        )
        if is_horizontal_to_vertical or is_vertical_to_horizontal:
            len_prev = math.sqrt(dx_prev * dx_prev + dy_prev * dy_prev + dz_prev * dz_prev)
            if len_prev > eps:
                axis_first_segment = AllplanGeo.Line3D(
                    AllplanGeo.Point3D(0, 0, 0),
                    AllplanGeo.Point3D(dx_prev / len_prev, dy_prev / len_prev, dz_prev / len_prev),
                )
                if dy_next < 0 and dz_next < 0:
                    rotation_angle = math.pi
                elif dz_next < 0:
                    rotation_angle = math.pi / 2.0
                else:
                    rotation_angle = -math.pi / 2.0
                rot_plane_change = AllplanGeo.Matrix3D()
                rot_plane_change.SetRotation(axis_first_segment, AllplanGeo.Angle(rotation_angle))
                mat = mat * rot_plane_change
                if dy_next < 0 and dz_next < 0:
                    rot_additional = AllplanGeo.Matrix3D()
                    rot_additional.SetRotation(axis_first_segment, AllplanGeo.Angle(-math.pi / 2.0))
                    mat = mat * rot_additional

    return AllplanGeo.Transform(brep, mat)

