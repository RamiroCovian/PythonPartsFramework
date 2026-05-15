# -*- coding: utf-8 -*-
"""Pluvial Ø110 mm — tubo tricapa con flecha propia (BRep)."""

import math

import NemAll_Python_Geometry as AllplanGeo
import NemAll_Python_AllplanSettings as AllplanSettings
import NemAll_Python_BasisElements as AllplanBasisElements

from BuildingElement import BuildingElement
from CreateElementResult import CreateElementResult
from BaseScriptObject import BaseScriptObject, BaseScriptObjectData

from .tub_pvc_tricapa_v_script import TuboPVCConFlecha

LAYER_IS_CON_SANE_FAB = 40148
FLECHA_COLOR = 27
FLECHA_FACTOR_LARGO = 0.7
FLECHA_OFFSET_Z = 0.5
FLECHA_DIST_ANILLO = 20.0


def check_allplan_version(_build_ele: BuildingElement, _version: str) -> bool:
    return True


def _build_arrow_110_brep(largo: float) -> AllplanGeo.BRep3D:
    diametro = 110.0
    largo_anillo = 60.0
    flecha_largo = diametro * FLECHA_FACTOR_LARGO
    z_flecha = diametro * 0.1 + FLECHA_OFFSET_Z
    largo_tubo = max(largo - largo_anillo, 0.0)

    # Misma lógica de flecha: anillo al inicio, flecha apunta hacia inicio.
    base_x = max(largo_tubo - flecha_largo - FLECHA_DIST_ANILLO, 0.0)
    sentido = -1.0
    y_centro, y_span = diametro * 0.5, diametro * 0.15
    punta_x = base_x + sentido * flecha_largo

    puntos = [
        AllplanGeo.Point3D(base_x, y_centro - y_span, z_flecha),
        AllplanGeo.Point3D(punta_x - sentido * y_span * 2, y_centro - y_span, z_flecha),
        AllplanGeo.Point3D(punta_x - sentido * y_span * 2, y_centro - y_span * 2, z_flecha),
        AllplanGeo.Point3D(punta_x, y_centro, z_flecha),
        AllplanGeo.Point3D(punta_x - sentido * y_span * 2, y_centro + y_span * 2, z_flecha),
        AllplanGeo.Point3D(punta_x - sentido * y_span * 2, y_centro + y_span, z_flecha),
        AllplanGeo.Point3D(base_x, y_centro + y_span, z_flecha),
        AllplanGeo.Point3D(base_x, y_centro - y_span, z_flecha),
    ]
    polygon = AllplanGeo.Polygon3D(puntos)
    area = AllplanGeo.PolygonalArea3D()
    area += polygon
    extruded = AllplanGeo.ExtrudedAreaSolid3D()
    extruded.SetDirection(AllplanGeo.Vector3D(0.0, 0.0, 1.0))
    extruded.SetExtrudedArea(area)
    err, polyhedron = AllplanGeo.CreatePolyhedron(extruded)
    if err != AllplanGeo.eGeometryErrorCode.eOK or polyhedron is None:
        raise RuntimeError("CreatePolyhedron flecha 110 falló")
    err, flecha_brep = AllplanGeo.CreateBRep3D(polyhedron)
    if err != AllplanGeo.eGeometryErrorCode.eOK or flecha_brep is None:
        raise RuntimeError("CreateBRep3D flecha 110 falló")

    # Misma rotación 180° en X que aplica el builder original para coherencia visual.
    rot_matrix = AllplanGeo.Matrix3D()
    rot_matrix.SetRotation(
        AllplanGeo.Line3D(0, 0, z_flecha, 1, 0, z_flecha),
        AllplanGeo.Angle(math.radians(180)),
    )
    flecha_brep = AllplanGeo.Transform(flecha_brep, rot_matrix)
    # Recentrar y reubicar en X por distancia al anillo para evitar flecha "lejana".
    err_v, verts = flecha_brep.GetVertices()
    if err_v == 0 and verts:
        cx = sum(v.X for v in verts) / len(verts)
        cy = sum(v.Y for v in verts) / len(verts)
        cz = sum(v.Z for v in verts) / len(verts)
        flecha_brep = AllplanGeo.Move(flecha_brep, AllplanGeo.Vector3D(-cx, -cy, -cz))

    x_pos = base_x - (largo_tubo * 0.5)
    mat_pos = AllplanGeo.Matrix3D()
    mat_pos.SetTranslation(AllplanGeo.Vector3D(x_pos, 0.0, 0.0))
    flecha_brep = AllplanGeo.Transform(flecha_brep, mat_pos)
    return flecha_brep


def _create_pluvial_110_with_own_arrow(
    doc, largo_total_mm: float | None = None
) -> CreateElementResult:
    raw = TuboPVCConFlecha(0, doc, largo_total_mm=largo_total_mm).create_result()
    elems = raw.elements
    if not elems:
        return raw
    tube = elems[0]
    largo = float(largo_total_mm) if largo_total_mm is not None else 1000.0
    flecha_brep = _build_arrow_110_brep(largo)

    flecha_props = AllplanSettings.AllplanGlobalSettings.GetCurrentCommonProperties()
    flecha_props.Color = FLECHA_COLOR
    flecha_props.ColorByLayer = False
    flecha_props.Layer = LAYER_IS_CON_SANE_FAB
    flecha_elem = AllplanBasisElements.ModelElement3D(flecha_props, flecha_brep)
    return CreateElementResult([tube, flecha_elem])


class TubPvcTricapaP110Script(BaseScriptObject):
    """PythonPart: Pluvial Ø110 con flecha propia BRep."""

    def __init__(
        self, build_ele: BuildingElement, script_object_data: BaseScriptObjectData
    ):
        super().__init__(script_object_data)
        self.build_ele = build_ele
        self.doc = self.coord_input.GetInputViewDocument()

    def get_attributes(self, *args, **kwargs):
        return []

    def execute(self, *args, **kwargs) -> CreateElementResult:
        lt = kwargs.get("LargoTramoMm")
        largo_total = None
        if lt is not None:
            try:
                largo_total = float(lt.value) if hasattr(lt, "value") else float(lt)
            except (TypeError, ValueError):
                largo_total = None
        return _create_pluvial_110_with_own_arrow(self.doc, largo_total_mm=largo_total)
