# -*- coding: utf-8 -*-
"""Codo PVC 90 grados para saneamiento fecal Ø25."""

import math

import NemAll_Python_Geometry as AllplanGeo
import NemAll_Python_BaseElements as AllplanBaseElements
import NemAll_Python_BasisElements as AllplanBasisElements

from NemAll_Python_BaseElements import AttributeService, LayerService

from BaseScriptObject import BaseScriptObject, BaseScriptObjectData
from BuildingElement import BuildingElement
from CreateElementResult import CreateElementResult


PARAMS = {
    # Medidas del croquis de referencia (mm)
    "BASE_LEN": 32.50,          # 0.03250 m
    "LEFT_VERTICAL": 36.66,     # 0.03666 m
    "TOP_LEFT_DIAGONAL": 22.88, # 0.02288 m @45
    "TOP_HORIZONTAL": 42.12,    # 0.04212 m
    "RIGHT_VERTICAL": 32.50,    # 0.03250 m
    "MID_HORIZONTAL": 20.61,    # 0.02061 m
    "INNER_DIAGONAL": 7.36,     # 0.00736 m @45
    "INNER_VERTICAL": 15.13,    # 0.01513 m
    "HEIGHT": 32.50,            # "0.03250 m de alto"
    "COPY_HEIGHT": 40.00,       # copias superpuestas: 0.04000 m
    # Corrección de base local para encastrar con la lógica de rotación del pipeline.
    "LOCAL_ROT_Z_CORR_DEG": 45.0,
    "COLOR": 70,
    "LAYER_SHORT": "IS_CON_SANE_FAB",
    "ATTR01": "CS90ºØ25",
    "ATTR02": "Ø25",
    "ATTR07": "25",
    "6_CC_IS": "",
    "pmp_CARTICULO": "KN07_001_002",
    "pmp_diametre": "25",
    "pmp_nom": "CS90ºØ25",
    "pmp_seccio": "25",
    "pmp_pes_unitari": 0.0133,
}


def check_allplan_version(_build_ele, _version) -> bool:
    """Check the current Allplan version."""
    return True


class ColzeBasic25mF90:
    """Crea la geometría y atributos del codo 90° Ø25."""

    def __init__(self, build_ele, doc):
        self.build_ele = build_ele
        self.doc = doc
        self.param = PARAMS

        props = AllplanBaseElements.CommonProperties()
        props.GetGlobalProperties()
        props.ColorByLayer = False
        props.Color = int(self.param["COLOR"])

        short_name = self.param.get("LAYER_SHORT")
        if short_name and self.doc:
            layer_id = LayerService.GetIDByShortName(short_name, self.doc)
            if layer_id > 0:
                props.Layer = layer_id

        self.common_props = props

    def _get_parent_attribute_value(self):
        for name in ("ValorAtributos", "AtributoPadre", "AtributosPadre", "Atributo_Padre"):
            raw = getattr(self.build_ele, name, None)
            value = str(getattr(raw, "value", raw) or "").strip()
            if value:
                return value
        return None

    def _create_colze_brep(self, custom_height=None):
        base = float(self.param["BASE_LEN"])
        left_vertical = float(self.param["LEFT_VERTICAL"])
        top_left_diag = float(self.param["TOP_LEFT_DIAGONAL"])
        top_horizontal = float(self.param["TOP_HORIZONTAL"])
        right_vertical = float(self.param["RIGHT_VERTICAL"])
        mid_horizontal = float(self.param["MID_HORIZONTAL"])
        inner_diag = float(self.param["INNER_DIAGONAL"])
        inner_vertical = float(self.param["INNER_VERTICAL"])
        height = float(self.param["HEIGHT"] if custom_height is None else custom_height)

        # Perfil 2D en XY (mm) según el croquis enviado:
        # p0->p1 base, p1->p2 vertical interna, p2->p3 diagonal 45, p3->p4 horizontal media,
        # p4->p5 vertical derecha, p5->p6 horizontal superior, p6->p7 diagonal 45, p7->p0 vertical izquierda.
        p0 = AllplanGeo.Point3D(0.0, 0.0, 0.0)
        p1 = AllplanGeo.Point3D(base, 0.0, 0.0)
        p2 = AllplanGeo.Point3D(base, inner_vertical, 0.0)
        p3 = AllplanGeo.Point3D(
            p2.X + inner_diag * math.cos(math.radians(45.0)),
            p2.Y + inner_diag * math.sin(math.radians(45.0)),
            0.0,
        )
        p4 = AllplanGeo.Point3D(p3.X + mid_horizontal, p3.Y, 0.0)
        p5 = AllplanGeo.Point3D(p4.X, p4.Y + right_vertical, 0.0)
        p6 = AllplanGeo.Point3D(p5.X - top_horizontal, p5.Y, 0.0)
        p7 = AllplanGeo.Point3D(
            p6.X - top_left_diag * math.cos(math.radians(45.0)),
            p6.Y - top_left_diag * math.sin(math.radians(45.0)),
            0.0,
        )

        points = [p0, p1, p2, p3, p4, p5, p6, p7, p0]
        polygon = AllplanGeo.Polygon3D(points)

        path = AllplanGeo.Polyline3D()
        path += AllplanGeo.Point3D(0.0, 0.0, 0.0)
        path += AllplanGeo.Point3D(0.0, 0.0, height)

        err, polyhedron = AllplanGeo.CreatePolyhedron(polygon, path)
        if err != 0 or polyhedron is None or not polyhedron.IsValid():
            raise RuntimeError(f"CreatePolyhedron del codo falló (err={err})")

        err, brep = AllplanGeo.CreateBRep3D(polyhedron)
        if err != 0 or brep is None or not brep.IsValid():
            raise RuntimeError(f"CreateBRep3D del codo falló (err={err})")

        # Ajuste de orientación local: el algoritmo global de codos espera una
        # referencia distinta; con el nuevo perfil, sin esta corrección queda
        # desfasado ~45° en giros de 90°.
        corr_deg = float(self.param.get("LOCAL_ROT_Z_CORR_DEG", 0.0))
        if abs(corr_deg) > 1e-6:
            axis_z = AllplanGeo.Line3D(
                AllplanGeo.Point3D(0.0, 0.0, 0.0),
                AllplanGeo.Point3D(0.0, 0.0, 1.0),
            )
            mat_corr = AllplanGeo.Matrix3D()
            mat_corr.SetRotation(axis_z, AllplanGeo.Angle(math.radians(corr_deg)))
            brep = AllplanGeo.Transform(brep, mat_corr)

        return brep

    def _create_model(self):
        brep = self._create_colze_brep()
        model = AllplanBasisElements.ModelElement3D(self.common_props, brep)
        self._apply_attributes(model)
        return model

    def _create_copy_common_props(self):
        props = AllplanBaseElements.CommonProperties()
        props.GetGlobalProperties()
        props.ColorByLayer = False
        props.Color = 5
        short_name = self.param.get("LAYER_SHORT")
        if short_name and self.doc:
            layer_id = LayerService.GetIDByShortName(short_name, self.doc)
            if layer_id > 0:
                props.Layer = layer_id
        return props

    def _apply_copy_attributes(self, model_elem, include_material=False):
        if not self.doc:
            return
        attr_list = []
        try:
            attr_6_cc_is_id = AttributeService.GetAttributeID(self.doc, "6_CC_IS")
            if attr_6_cc_is_id and attr_6_cc_is_id > 0:
                attr_list.append(AllplanBaseElements.AttributeString(attr_6_cc_is_id, "IS"))

            if include_material:
                attr_material_id = AttributeService.GetAttributeID(self.doc, "Material")
                if attr_material_id and attr_material_id > 0:
                    attr_list.append(AllplanBaseElements.AttributeString(attr_material_id, "CAVITAT"))
        except Exception as ex:
            print(f"[ColzeBasic25mF90] Advertencia al agregar atributos copia: {ex}")

        if attr_list:
            attr_set = AllplanBaseElements.AttributeSet(attr_list)
            model_elem.SetAttributes(AllplanBaseElements.Attributes([attr_set]))

    def _apply_attributes(self, model_elem):
        parent_value = self._get_parent_attribute_value()
        value_to_apply = parent_value or self.param.get("6_CC_IS", "")

        attr_list = [
            AllplanBaseElements.AttributeString(1083, self.param["ATTR01"]),
            AllplanBaseElements.AttributeString(1084, self.param["ATTR02"]),
            AllplanBaseElements.AttributeString(1896, self.param["ATTR07"]),
        ]
        for attr_id in (1085, 1086, 1087, 1895):
            attr_list.append(AllplanBaseElements.AttributeString(attr_id, ""))

        if self.doc:
            try:
                def _get_attr_id(name):
                    return AttributeService.GetAttributeID(self.doc, name)

                def _add_string(name, value):
                    attr_id = _get_attr_id(name)
                    if attr_id and attr_id > 0:
                        attr_list.append(AllplanBaseElements.AttributeString(attr_id, value))

                def _add_int_or_string(name, value_int):
                    attr_id = _get_attr_id(name)
                    if not attr_id or attr_id <= 0:
                        return
                    try:
                        attr_list.append(AllplanBaseElements.AttributeInteger(attr_id, value_int))
                    except Exception:
                        attr_list.append(AllplanBaseElements.AttributeString(attr_id, str(value_int)))

                _add_string("6_CC_IS", value_to_apply)
                _add_string("pmp_CARTICULO", self.param["pmp_CARTICULO"])
                _add_string("pmp_nom", self.param["pmp_nom"])
                _add_string("pmp_pare", value_to_apply)

                attr_pmp_pes_unitari_id = _get_attr_id("pmp_pes_unitari")
                if attr_pmp_pes_unitari_id and attr_pmp_pes_unitari_id > 0:
                    attr_list.append(
                        AllplanBaseElements.AttributeDouble(
                            attr_pmp_pes_unitari_id, float(self.param["pmp_pes_unitari"])
                        )
                    )

                _add_int_or_string("pmp_diametre", 25)
                _add_int_or_string("pmp_seccio", 25)
            except Exception as ex:
                print(f"[ColzeBasic25mF90] Advertencia al agregar atributos: {ex}")

        attr_set = AllplanBaseElements.AttributeSet(attr_list)
        model_elem.SetAttributes(AllplanBaseElements.Attributes([attr_set]))

    def create_result(self) -> CreateElementResult:
        outer_model = self._create_model()
        copy_height = float(self.param["COPY_HEIGHT"])
        brep = self._create_colze_brep(custom_height=copy_height)
        copy_props = self._create_copy_common_props()

        copy_1 = AllplanBasisElements.ModelElement3D(copy_props, brep)
        self._apply_copy_attributes(copy_1, include_material=False)

        copy_2 = AllplanBasisElements.ModelElement3D(copy_props, brep)
        self._apply_copy_attributes(copy_2, include_material=True)

        return CreateElementResult([outer_model, copy_1, copy_2])


def _create_element(build_ele, doc) -> CreateElementResult:
    return ColzeBasic25mF90(build_ele, doc).create_result()


class ColzeBasic25mF90Script(BaseScriptObject):
    """PythonPart: Codo 90° Ø25 para saneamiento fecal."""

    def __init__(self, build_ele: BuildingElement, script_object_data: BaseScriptObjectData):
        super().__init__(script_object_data)
        self.build_ele = build_ele
        self.doc = self.coord_input.GetInputViewDocument()

    def get_attributes(self, *args, **kwargs):
        return []

    def execute(self, *args, **kwargs) -> CreateElementResult:
        return _create_element(self.build_ele, self.doc)
