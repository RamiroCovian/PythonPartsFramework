# -*- coding: utf-8 -*-
"""Codo PVC 45 grados para saneamiento fecal Ø25."""

import math

import NemAll_Python_Geometry as AllplanGeo
import NemAll_Python_BaseElements as AllplanBaseElements
import NemAll_Python_BasisElements as AllplanBasisElements

from NemAll_Python_BaseElements import AttributeService, LayerService

from BaseScriptObject import BaseScriptObject, BaseScriptObjectData
from BuildingElement import BuildingElement
from CreateElementResult import CreateElementResult


PARAMS = {
    # Medidas del croquis (mm)
    "BASE_LEN": 32.5,           
    "LEFT_VERTICAL": 40.0,      
    "LEFT_DIAGONAL": 33.46,     
    "TOP_DIAGONAL": 32.5,      
    "RIGHT_DIAGONAL": 20.00,   
    "RIGHT_VERTICAL": 33.46,   
    "HEIGHT": 32.5,            
    "COLOR": 70,
    "LAYER_SHORT": "IS_CON_SANE_FAB",
    "ATTR01": "CS45ºØ25",
    "ATTR02": "Ø25",
    "ATTR07": "25",
    "6_CC_IS": "",
    "pmp_CARTICULO": "KN07_001_001",
    "pmp_diametre": "25",
    "pmp_nom": "CS45ºØ25",
    "pmp_seccio": "25",
    "pmp_pes_unitari": 0.0133,
}


def check_allplan_version(_build_ele, _version) -> bool:
    """Check the current Allplan version."""
    return True


class ColzeBasic25mF45:
    """Crea la geometría y atributos del codo 45° Ø25."""

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

    def _create_colze_brep(self):
        base = float(self.param["BASE_LEN"])
        left_vertical = float(self.param["LEFT_VERTICAL"])
        left_diagonal = float(self.param["LEFT_DIAGONAL"])
        top_diagonal = float(self.param["TOP_DIAGONAL"])
        right_diagonal = float(self.param["RIGHT_DIAGONAL"])
        right_vertical = float(self.param["RIGHT_VERTICAL"])
        height = float(self.param["HEIGHT"])

        # Perfil 2D del croquis en XY (mm), luego se extruye en Z.
        # Recorrido correcto del perímetro (sentido antihorario):
        # base izq -> vertical izq -> diagonal 0.040 -> diagonal superior 0.0325
        # -> diagonal 0.02654 -> vertical der 0.0200 -> base.
        p0 = AllplanGeo.Point3D(0.0, 0.0, 0.0)                 # esquina inferior izquierda
        p1 = AllplanGeo.Point3D(0.0, left_vertical, 0.0)       # vertical izquierda
        # Subida por diagonal izquierda (45°)
        p2 = AllplanGeo.Point3D(
            p1.X + left_diagonal * math.cos(math.radians(45.0)),
            p1.Y + left_diagonal * math.sin(math.radians(45.0)),
            0.0,
        )
        # Bajada por diagonal superior hacia la derecha (-45°)
        p3 = AllplanGeo.Point3D(
            p2.X + top_diagonal * math.cos(math.radians(-45.0)),
            p2.Y + top_diagonal * math.sin(math.radians(-45.0)),
            0.0,
        )
        # Bajada por diagonal derecha hacia la izquierda (-135°)
        p4 = AllplanGeo.Point3D(
            p3.X + right_diagonal * math.cos(math.radians(-135.0)),
            p3.Y + right_diagonal * math.sin(math.radians(-135.0)),
            0.0,
        )
        p5 = AllplanGeo.Point3D(base, right_vertical, 0.0)     # vertical derecha (arriba)
        p6 = AllplanGeo.Point3D(base, 0.0, 0.0)                # esquina inferior derecha

        points = [p0, p1, p2, p3, p4, p5, p6, p0]
        polygon = AllplanGeo.Polygon3D(points)

        # Patrón Clima: extrusión por path para obtener un Polyhedron estable.
        path = AllplanGeo.Polyline3D()
        path += AllplanGeo.Point3D(0.0, 0.0, 0.0)
        path += AllplanGeo.Point3D(0.0, 0.0, height)

        err, polyhedron = AllplanGeo.CreatePolyhedron(polygon, path)
        if err != 0 or polyhedron is None or not polyhedron.IsValid():
            raise RuntimeError(f"CreatePolyhedron del codo falló (err={err})")

        err, brep = AllplanGeo.CreateBRep3D(polyhedron)
        if err != 0 or brep is None or not brep.IsValid():
            raise RuntimeError(f"CreateBRep3D del codo falló (err={err})")

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
            print(f"[ColzeBasic25mF45] Advertencia al agregar atributos copia: {ex}")

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
                    attr_list.append(AllplanBaseElements.AttributeDouble(attr_pmp_pes_unitari_id, float(self.param["pmp_pes_unitari"])))

                _add_int_or_string("pmp_diametre", 25)
                _add_int_or_string("pmp_seccio", 25)
            except Exception as ex:
                print(f"[ColzeBasic25mF45] Advertencia al agregar atributos: {ex}")

        attr_set = AllplanBaseElements.AttributeSet(attr_list)
        model_elem.SetAttributes(AllplanBaseElements.Attributes([attr_set]))

    def create_result(self) -> CreateElementResult:
        outer_model = self._create_model()
        brep = self._create_colze_brep()
        copy_props = self._create_copy_common_props()

        copy_1 = AllplanBasisElements.ModelElement3D(copy_props, brep)
        self._apply_copy_attributes(copy_1, include_material=False)

        copy_2 = AllplanBasisElements.ModelElement3D(copy_props, brep)
        self._apply_copy_attributes(copy_2, include_material=True)

        return CreateElementResult([outer_model, copy_1, copy_2])


def _create_element(build_ele, doc) -> CreateElementResult:
    return ColzeBasic25mF45(build_ele, doc).create_result()


class ColzeBasic25mF45Script(BaseScriptObject):
    """PythonPart: Codo 45° Ø25 para saneamiento fecal."""

    def __init__(self, build_ele: BuildingElement, script_object_data: BaseScriptObjectData):
        super().__init__(script_object_data)
        self.build_ele = build_ele
        self.doc = self.coord_input.GetInputViewDocument()

    def get_attributes(self, *args, **kwargs):
        return []

    def execute(self, *args, **kwargs) -> CreateElementResult:
        return _create_element(self.build_ele, self.doc)
