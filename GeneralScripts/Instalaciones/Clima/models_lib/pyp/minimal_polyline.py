# -*- coding: utf-8 -*-
"""Ejemplo mínimo de polilínea usando polyline_base_lib.

- Dibujar polilínea
- Botones Guardar / Finalizar
- Crea una caja hueca (ducto mock) por segmento
"""
from __future__ import annotations
import os
import sys
import math

try:
    import NemAll_Python_Geometry as AllplanGeo
    import NemAll_Python_BaseElements as AllplanBaseElements
    import NemAll_Python_BasisElements as AllplanBasisElements
    ALLPLAN_AVAILABLE = True
except Exception:
    ALLPLAN_AVAILABLE = False

def _add_libreria_py_to_sys_path():
    """Añade Instalaciones/Libreria al sys.path (ruta común para instalaciones)."""
    if not __file__:
        return
    current = os.path.abspath(os.path.dirname(__file__))
    while True:
        if os.path.basename(current).lower() == "instalaciones":
            libreria_root = os.path.join(current, "Libreria")
            if os.path.isdir(libreria_root) and libreria_root not in sys.path:
                sys.path.insert(0, libreria_root)
            break
        parent = os.path.dirname(current)
        if parent == current:
            break
        current = parent

def _add_local_models_lib_py():
    """Fallback local para desarrollo (Clima/models_lib/py)."""
    if not __file__:
        return
    script_dir = os.path.dirname(__file__)
    lib_py_dir = os.path.abspath(os.path.join(script_dir, "..", "py"))
    if lib_py_dir not in sys.path:
        sys.path.insert(0, lib_py_dir)

# Preferir Libreria global; fallback local si no existe
_add_libreria_py_to_sys_path()
_add_local_models_lib_py()

import polyline_base_lib as PBL

CONFIG = PBL.PolylineBaseConfig(
    limit_angles=False,
    drawing_mode=PBL.DRAWING_MODE_2D,
    enable_z_coordinate=False,
    allow_insert_point_mode=False,
    enable_capture_mode=False,
)


def check_allplan_version(_build_ele, _version):
    return True


def create_script_object(build_ele, script_object_data):
    script_object = PBL.initialize_script_object(build_ele, script_object_data, CONFIG)
    script_object.element_creation_hook = lambda seg_meta, common_prop: _create_hollow_box_elements(
        seg_meta, common_prop, build_ele
    )
    PBL.enable_transactional_finalize(script_object)
    return script_object


def _create_hollow_box_elements(seg_meta, _common_prop, _build_ele=None):
    """Crea una caja hueca (ducto mock) a lo largo del segmento."""
    if not ALLPLAN_AVAILABLE:
        return []

    pts = list(seg_meta.points)
    if len(pts) < 2:
        return []

    start = pts[0]
    end = pts[-1]
    dx = end.X - start.X
    dy = end.Y - start.Y
    dz = end.Z - start.Z
    length = math.sqrt(dx * dx + dy * dy + dz * dz)
    if length < 1e-3:
        return []

    # Dimensiones del ducto (mm)
    width = 200.0
    height = 100.0
    thickness = 10.0

    # Construir paredes de la caja en coordenadas locales (eje X = dirección del segmento)
    walls = []
    x0, x1 = 0.0, length
    y0, y1 = -width / 2.0, width / 2.0
    z0, z1 = -height / 2.0, height / 2.0

    # Base
    walls.append(AllplanGeo.Polyhedron3D.CreateCuboid(
        AllplanGeo.Point3D(x0, y0, z0),
        AllplanGeo.Point3D(x1, y1, z0 + thickness)
    ))
    # Tapa
    walls.append(AllplanGeo.Polyhedron3D.CreateCuboid(
        AllplanGeo.Point3D(x0, y0, z1 - thickness),
        AllplanGeo.Point3D(x1, y1, z1)
    ))
    # Lateral izquierdo
    walls.append(AllplanGeo.Polyhedron3D.CreateCuboid(
        AllplanGeo.Point3D(x0, y0, z0 + thickness),
        AllplanGeo.Point3D(x1, y0 + thickness, z1 - thickness)
    ))
    # Lateral derecho
    walls.append(AllplanGeo.Polyhedron3D.CreateCuboid(
        AllplanGeo.Point3D(x0, y1 - thickness, z0 + thickness),
        AllplanGeo.Point3D(x1, y1, z1 - thickness)
    ))

    # Matriz de rotación para alinear +X con la dirección del segmento
    matrix = AllplanGeo.Matrix3D()
    if abs(dx) < 1e-6 and abs(dy) < 1e-6:
        # Segmento vertical: rotar X->Z
        matrix.SetRotation(
            AllplanGeo.Line3D(0, 0, 0, 0, 1, 0),
            AllplanGeo.Angle(math.radians(90.0))
        )
    else:
        angle_z = math.atan2(dy, dx)
        rot_z = AllplanGeo.Matrix3D()
        rot_z.SetRotation(
            AllplanGeo.Line3D(0, 0, 0, 0, 0, 1),
            AllplanGeo.Angle(angle_z)
        )
        if abs(dz) > 1e-6:
            horizontal_dist = math.sqrt(dx * dx + dy * dy)
            angle_y = math.atan2(dz, horizontal_dist)
            rot_y = AllplanGeo.Matrix3D()
            rot_y.SetRotation(
                AllplanGeo.Line3D(0, 0, 0, 0, 1, 0),
                AllplanGeo.Angle(angle_y)
            )
            matrix = rot_y * rot_z
        else:
            matrix = rot_z

    # Trasladar al punto inicial
    trans = AllplanGeo.Matrix3D()
    trans.SetTranslation(AllplanGeo.Vector3D(start))
    matrix = matrix * trans

    # Crear elementos
    elements = []
    props = AllplanBaseElements.CommonProperties()
    props.GetGlobalProperties()
    props.Color = 3

    for wall in walls:
        wall = AllplanGeo.Transform(wall, matrix)
        elements.append(AllplanBasisElements.ModelElement3D(props, wall))

    return elements
