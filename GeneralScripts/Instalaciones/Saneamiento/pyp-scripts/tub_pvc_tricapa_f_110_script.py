# -*- coding: utf-8 -*-
"""Fecal Ø110 mm — tubo recoloreado + flecha propia (BRep)."""

import math

import NemAll_Python_Geometry as AllplanGeo
import NemAll_Python_AllplanSettings as AllplanSettings
import NemAll_Python_BasisElements as AllplanBasisElements
import NemAll_Python_BaseElements as AllplanBaseElements

from BuildingElement import BuildingElement
from CreateElementResult import CreateElementResult
from BaseScriptObject import BaseScriptObject, BaseScriptObjectData

from .tub_pvc_tricapa_v_script import TuboPVCConFlecha

FECAL_110_COLOR = 4
LAYER_IS_CON_SANE_FAB = 40148
FLECHA_COLOR = 27
FLECHA_FACTOR_LARGO = 0.7
FLECHA_OFFSET_Z = 0.5
FLECHA_DIST_ANILLO = 30.0
MODEL_ROT_Z_DEG = 180.0


def check_allplan_version(_build_ele: BuildingElement, _version: str) -> bool:
    return True


def _rotate_z(geo):
    eje_z = AllplanGeo.Axis3D(AllplanGeo.Point3D(0, 0, 0), AllplanGeo.Vector3D(0, 0, 1))
    rotated = AllplanGeo.Rotate(geo, eje_z, AllplanGeo.Angle(math.radians(MODEL_ROT_Z_DEG)))
    if isinstance(rotated, tuple):
        err, geo_rot = rotated
        if err != 0:
            raise RuntimeError(f"Rotate Z falló (err={err})")
        return geo_rot
    return rotated


def _flip_flecha_sentido_tubo(flecha_brep):
    """Invierte el sentido de la flecha a lo largo del tubo (desde el anillo hacia el interior).

    Igual que en tub_pvc_tricapa_f_40_script: 180° en Y por el centroide.
    """
    err_v, verts = flecha_brep.GetVertices()
    if err_v != 0 or not verts:
        return flecha_brep
    cx = sum(v.X for v in verts) / len(verts)
    cy = sum(v.Y for v in verts) / len(verts)
    cz = sum(v.Z for v in verts) / len(verts)
    flecha_brep = AllplanGeo.Move(
        flecha_brep, AllplanGeo.Vector3D(-cx, -cy, -cz)
    )
    eje_y = AllplanGeo.Axis3D(
        AllplanGeo.Point3D(0, 0, 0), AllplanGeo.Vector3D(0, 1, 0)
    )
    r = AllplanGeo.Rotate(
        flecha_brep, eje_y, AllplanGeo.Angle(math.radians(180))
    )
    if isinstance(r, tuple):
        err, g = r
        if err != 0 or g is None:
            return AllplanGeo.Move(
                flecha_brep, AllplanGeo.Vector3D(cx, cy, cz)
            )
        flecha_brep = g
    else:
        flecha_brep = r
    return AllplanGeo.Move(flecha_brep, AllplanGeo.Vector3D(cx, cy, cz))


def _build_arrow_110_brep(largo: float) -> AllplanGeo.BRep3D:
    diametro = 110.0
    largo_anillo = 60.0
    flecha_largo = diametro * FLECHA_FACTOR_LARGO
    z_flecha = diametro * 0.1 + FLECHA_OFFSET_Z
    largo_tubo = max(largo - largo_anillo, 0.0)

    base_x = max(largo_tubo - flecha_largo - FLECHA_DIST_ANILLO, 0.0)
    sentido = 1.0
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
        raise RuntimeError("CreatePolyhedron flecha 110 fecal falló")
    err, flecha_brep = AllplanGeo.CreateBRep3D(polyhedron)
    if err != AllplanGeo.eGeometryErrorCode.eOK or flecha_brep is None:
        raise RuntimeError("CreateBRep3D flecha 110 fecal falló")

    rot_matrix = AllplanGeo.Matrix3D()
    rot_matrix.SetRotation(
        AllplanGeo.Line3D(0, 0, z_flecha, 1, 0, z_flecha),
        AllplanGeo.Angle(math.radians(180)),
    )
    flecha_brep = AllplanGeo.Transform(flecha_brep, rot_matrix)

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


def _apply_own_attributes_110(model_elem, doc) -> None:
    """Asigna atributos propios del TS-110 según ficha solicitada."""
    try:
        attr_list = [
            AllplanBaseElements.AttributeString(1083, "TS-110"),
            AllplanBaseElements.AttributeString(1084, "Ø110"),
            AllplanBaseElements.AttributeString(1085, ""),
            AllplanBaseElements.AttributeString(1086, ""),
            AllplanBaseElements.AttributeString(1087, ""),
            AllplanBaseElements.AttributeString(1895, ""),
            AllplanBaseElements.AttributeString(1896, "110"),
            AllplanBaseElements.AttributeString(1897, ""),
            AllplanBaseElements.AttributeString(1898, "12100"),
            AllplanBaseElements.AttributeString(1899, ""),
            AllplanBaseElements.AttributeString(1900, ""),
            AllplanBaseElements.AttributeString(1901, ""),
            AllplanBaseElements.AttributeString(1902, ""),
            AllplanBaseElements.AttributeString(1903, ""),
            AllplanBaseElements.AttributeString(1904, ""),
        ]

        if doc:
            get_id = AllplanBaseElements.AttributeService.GetAttributeID
            id_6ccis = get_id(doc, "6_CC_IS")
            id_cart = get_id(doc, "pmp_CARTICULO")
            id_nom = get_id(doc, "pmp_nom")
            id_area = get_id(doc, "pmp_area")
            id_dlin = get_id(doc, "pmp_densitat_lineal")
            id_diam = get_id(doc, "pmp_diametre")
            id_sec = get_id(doc, "pmp_seccio")

            if id_6ccis and id_6ccis > 0:
                attr_list.append(AllplanBaseElements.AttributeString(id_6ccis, "IS"))
            if id_cart and id_cart > 0:
                attr_list.append(AllplanBaseElements.AttributeString(id_cart, "KN07_005_003"))
            if id_nom and id_nom > 0:
                attr_list.append(AllplanBaseElements.AttributeString(id_nom, "TS-110"))
            if id_area and id_area > 0:
                attr_list.append(AllplanBaseElements.AttributeDouble(id_area, 12100.000000))
            if id_dlin and id_dlin > 0:
                attr_list.append(AllplanBaseElements.AttributeDouble(id_dlin, 0.2288))
            if id_diam and id_diam > 0:
                try:
                    attr_list.append(AllplanBaseElements.AttributeInteger(id_diam, 110))
                except Exception:
                    attr_list.append(AllplanBaseElements.AttributeString(id_diam, "110"))
            if id_sec and id_sec > 0:
                try:
                    attr_list.append(AllplanBaseElements.AttributeInteger(id_sec, 110))
                except Exception:
                    attr_list.append(AllplanBaseElements.AttributeString(id_sec, "110"))

        attr_set = AllplanBaseElements.AttributeSet(attr_list)
        model_elem.SetAttributes(AllplanBaseElements.Attributes([attr_set]))
    except Exception as ex:
        print(f"[TubPvcTricapaF110] Advertencia al asignar atributos propios: {ex}")


def _create_fecal_110_with_color(
    doc, largo_total_mm: float | None = None
) -> CreateElementResult:
    raw = TuboPVCConFlecha(0, doc, largo_total_mm=largo_total_mm).create_result()
    elems = raw.elements
    if not elems:
        return raw
    orig = elems[0]
    prop = orig.GetCommonProperties()
    prop.Color = FECAL_110_COLOR
    prop.ColorByLayer = False
    tube_geom = orig.GetGeometryObject()

    # Giro solicitado en modelo: 180° alrededor del eje Z.
    tube_geom = _rotate_z(tube_geom)
    tube = AllplanBasisElements.ModelElement3D(prop, tube_geom)
    _apply_own_attributes_110(tube, doc)

    largo = float(largo_total_mm) if largo_total_mm is not None else 1000.0
    flecha_brep = _build_arrow_110_brep(largo)
    flecha_brep = _flip_flecha_sentido_tubo(flecha_brep)
    flecha_brep = _rotate_z(flecha_brep)
    flecha_props = AllplanSettings.AllplanGlobalSettings.GetCurrentCommonProperties()
    flecha_props.Color = FLECHA_COLOR
    flecha_props.ColorByLayer = False
    flecha_props.Layer = LAYER_IS_CON_SANE_FAB
    flecha_elem = AllplanBasisElements.ModelElement3D(flecha_props, flecha_brep)
    return CreateElementResult([tube, flecha_elem])


class TubPvcTricapaF110Script(BaseScriptObject):
    """PythonPart: Fecal Ø110 (geometría tipo 0, tubo recoloreado)."""

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
        return _create_fecal_110_with_color(self.doc, largo_total_mm=largo_total)
