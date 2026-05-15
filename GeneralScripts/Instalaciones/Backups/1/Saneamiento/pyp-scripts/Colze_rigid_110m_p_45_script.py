# -*- coding: utf-8 -*-
"""Codo rígido pluvial Ø110 a 45° (misma geometría que fecal Ø110 45°)."""

import math

import NemAll_Python_Geometry as AllplanGeo
import NemAll_Python_BasisElements as AllplanBasisElements
import NemAll_Python_AllplanSettings as AllplanSettings
import NemAll_Python_BaseElements as AllplanBaseElements
from NemAll_Python_BaseElements import LayerService
from CreateElementResult import CreateElementResult
from BaseScriptObject import BaseScriptObject, BaseScriptObjectData
from BuildingElement import BuildingElement


def check_allplan_version(_build_ele, _version) -> bool:
    """Check the current Allplan version (se soportan todas las versiones)."""
    return True


class CodoRigido110mP45:
    """Codo pluvial 110mm 45° con geometría compartida con fecal 110mm 45°."""

    # Independiente de fecal: aquí quedan definidos layer/atributos propios.
    LAYER_SHORT = "IS_CON_SANE_FAB"
    LAYER_FALLBACK = 40148
    COLOR = 7
    ATTR_1083 = "COLZE M-F 110Ø 45º"
    ATTR_1084 = "Ø110"
    ATTR_1896 = "110"
    PMP_CARTICULO = "KN07_004_003"
    PMP_DIAMETRE = 110
    PMP_NOM = "CS45°Ø110"
    PMP_PES_UNITARI = 0.2110
    PMP_SECCIO = "Ø110/45°"
    ATTR_6_CC_IS = ""

    ROT_X_110MM_45 = 180.0
    ROT_Y_110MM_45 = 0.0
    ROT_Z_110MM_45 = 45.0

    PARAM_110_45 = dict(
        DIAMETRO=110.0,
        LARGO_VERTICAL=10.0,
        LARGO_INCLINADA=80.0,
        LARGO_HORIZONTAL=70.0,
        ANGULO_INCLINADA=23.0,
        ANGULO_HORIZONTAL=45.0,
        LARGO_ANILLO=73.0,
        SOBRESALE_ANILLO=9.0,
    )

    def __init__(self, build_ele, doc=None):
        self.build_ele = build_ele
        self.doc = doc

    def _props(self, color: int, pen: int = 1, stroke: int = 1, layer: int = None):
        if layer is None:
            layer = self.LAYER_FALLBACK
            if self.doc and self.LAYER_SHORT:
                layer_id = LayerService.GetIDByShortName(self.LAYER_SHORT, self.doc)
                if layer_id > 0:
                    layer = layer_id
        p = AllplanSettings.AllplanGlobalSettings.GetCurrentCommonProperties()
        p.Color = color
        p.ColorByLayer = False
        p.Pen = pen
        p.Stroke = stroke
        p.Layer = layer
        return p

    @staticmethod
    def _crear_prisma(diametro: float, largo: float):
        return AllplanGeo.Polyhedron3D.CreateCuboid(
            AllplanGeo.Point3D(0, 0, 0), AllplanGeo.Point3D(diametro, diametro, largo)
        )

    def _add_user_attributes_110mm_45(self, attr_list):
        """Atributos de usuario del codo pluvial 110mm 45°."""
        if not self.doc:
            return
        try:
            attr_6_cc_is_id = AllplanBaseElements.AttributeService.GetAttributeID(
                self.doc, "6_CC_IS"
            )
            attr_pmp_carticulo_id = AllplanBaseElements.AttributeService.GetAttributeID(
                self.doc, "pmp_CARTICULO"
            )
            attr_pmp_diametre_id = AllplanBaseElements.AttributeService.GetAttributeID(
                self.doc, "pmp_diametre"
            )
            attr_pmp_nom_id = AllplanBaseElements.AttributeService.GetAttributeID(
                self.doc, "pmp_nom"
            )
            attr_pmp_pes_unitari_id = AllplanBaseElements.AttributeService.GetAttributeID(
                self.doc, "pmp_pes_unitari"
            )
            attr_pmp_seccio_id = AllplanBaseElements.AttributeService.GetAttributeID(
                self.doc, "pmp_seccio"
            )

            if attr_6_cc_is_id and attr_6_cc_is_id > 0:
                attr_list.append(
                    AllplanBaseElements.AttributeString(attr_6_cc_is_id, self.ATTR_6_CC_IS)
                )
            if attr_pmp_carticulo_id and attr_pmp_carticulo_id > 0:
                attr_list.append(
                    AllplanBaseElements.AttributeString(
                        attr_pmp_carticulo_id, self.PMP_CARTICULO
                    )
                )
            if attr_pmp_diametre_id and attr_pmp_diametre_id > 0:
                try:
                    attr_list.append(
                        AllplanBaseElements.AttributeInt(
                            attr_pmp_diametre_id, int(self.PMP_DIAMETRE)
                        )
                    )
                except Exception:
                    attr_list.append(
                        AllplanBaseElements.AttributeString(
                            attr_pmp_diametre_id, str(self.PMP_DIAMETRE)
                        )
                    )
            if attr_pmp_nom_id and attr_pmp_nom_id > 0:
                attr_list.append(
                    AllplanBaseElements.AttributeString(attr_pmp_nom_id, self.PMP_NOM)
                )
            if attr_pmp_pes_unitari_id and attr_pmp_pes_unitari_id > 0:
                attr_list.append(
                    AllplanBaseElements.AttributeDouble(
                        attr_pmp_pes_unitari_id, self.PMP_PES_UNITARI
                    )
                )
            if attr_pmp_seccio_id and attr_pmp_seccio_id > 0:
                attr_list.append(
                    AllplanBaseElements.AttributeString(attr_pmp_seccio_id, self.PMP_SECCIO)
                )
        except Exception as e:
            print(
                f"[Colze_rigid_110m_p_45_script] Advertencia atributos 110mm 45°: {e}"
            )

    def _build_110mm_45(self):
        p = self.PARAM_110_45
        props = self._props(color=self.COLOR)

        cubo0 = self._crear_prisma(p["DIAMETRO"], p["LARGO_VERTICAL"])

        rad_incl = math.radians(p["ANGULO_INCLINADA"])
        cubo1 = self._crear_prisma(p["DIAMETRO"], p["LARGO_INCLINADA"])
        m1 = AllplanGeo.Matrix3D()
        m1.SetRotation(AllplanGeo.Line3D(0, 0, 0, 1, 0, 0), AllplanGeo.Angle(-rad_incl))
        cubo1 = AllplanGeo.Transform(cubo1, m1)
        t1 = AllplanGeo.Matrix3D()
        t1.SetTranslation(AllplanGeo.Vector3D(0, 0, p["LARGO_VERTICAL"]))
        cubo1 = AllplanGeo.Transform(cubo1, t1)

        dz = p["LARGO_INCLINADA"] * math.cos(rad_incl)
        dy = p["LARGO_INCLINADA"] * math.sin(rad_incl)

        rad_h = math.radians(p["ANGULO_HORIZONTAL"])
        cubo2 = self._crear_prisma(p["DIAMETRO"], p["LARGO_HORIZONTAL"])
        m2 = AllplanGeo.Matrix3D()
        m2.SetRotation(AllplanGeo.Line3D(0, 0, 0, 1, 0, 0), AllplanGeo.Angle(-rad_h))
        cubo2 = AllplanGeo.Transform(cubo2, m2)
        t2 = AllplanGeo.Matrix3D()
        t2.SetTranslation(AllplanGeo.Vector3D(0, dy, p["LARGO_VERTICAL"] + dz))
        cubo2 = AllplanGeo.Transform(cubo2, t2)

        anillo = AllplanGeo.Polyhedron3D.CreateCuboid(
            AllplanGeo.Point3D(
                -p["SOBRESALE_ANILLO"], -p["SOBRESALE_ANILLO"], -p["LARGO_ANILLO"]
            ),
            AllplanGeo.Point3D(
                p["DIAMETRO"] + p["SOBRESALE_ANILLO"],
                p["DIAMETRO"] + p["SOBRESALE_ANILLO"],
                0,
            ),
        )

        err, codo = AllplanGeo.MakeUnion(cubo0, cubo1)
        if err == 0 and codo.IsValid():
            err, codo = AllplanGeo.MakeUnion(codo, cubo2)
        if err == 0 and codo.IsValid():
            err, codo = AllplanGeo.MakeUnion(codo, anillo)
        if err != 0 or not codo.IsValid():
            return props, None

        eje_y = AllplanGeo.Axis3D(AllplanGeo.Point3D(0, 0, 0), AllplanGeo.Vector3D(0, 1, 0))
        codo_rot = AllplanGeo.Rotate(codo, eje_y, AllplanGeo.Angle(math.radians(270)))

        cx = p["DIAMETRO"] / 2.0
        cy = p["DIAMETRO"] / 2.0 + p["LARGO_INCLINADA"] * math.sin(
            math.radians(p["ANGULO_INCLINADA"])
        ) / 2.0
        cz = (
            p["LARGO_VERTICAL"]
            + p["LARGO_INCLINADA"] * math.cos(math.radians(p["ANGULO_INCLINADA"]))
            + p["LARGO_HORIZONTAL"]
        ) / 2.0

        if abs(self.ROT_X_110MM_45) > 1e-6:
            eje_x = AllplanGeo.Axis3D(
                AllplanGeo.Point3D(cx, cy, cz), AllplanGeo.Vector3D(1, 0, 0)
            )
            codo_rot = AllplanGeo.Rotate(
                codo_rot, eje_x, AllplanGeo.Angle(math.radians(self.ROT_X_110MM_45))
            )
        if abs(self.ROT_Y_110MM_45) > 1e-6:
            eje_y_rot = AllplanGeo.Axis3D(
                AllplanGeo.Point3D(cx, cy, cz), AllplanGeo.Vector3D(0, 1, 0)
            )
            codo_rot = AllplanGeo.Rotate(
                codo_rot, eje_y_rot, AllplanGeo.Angle(math.radians(self.ROT_Y_110MM_45))
            )
        if abs(self.ROT_Z_110MM_45) > 1e-6:
            eje_z = AllplanGeo.Axis3D(
                AllplanGeo.Point3D(cx, cy, cz), AllplanGeo.Vector3D(0, 0, 1)
            )
            codo_rot = AllplanGeo.Rotate(
                codo_rot, eje_z, AllplanGeo.Angle(math.radians(self.ROT_Z_110MM_45))
            )

        return props, codo_rot

    def create_result(self) -> CreateElementResult:
        props, solid = self._build_110mm_45()
        if solid is None or not solid.IsValid():
            print("Error al crear el codo 110mm 45°.")
            return CreateElementResult([])

        model_elem = AllplanBasisElements.ModelElement3D(props, solid)
        attr_list = [
            AllplanBaseElements.AttributeString(1083, self.ATTR_1083),
            AllplanBaseElements.AttributeString(1084, self.ATTR_1084),
            AllplanBaseElements.AttributeString(1085, ""),
            AllplanBaseElements.AttributeString(1086, ""),
            AllplanBaseElements.AttributeString(1087, ""),
            AllplanBaseElements.AttributeString(1895, ""),
            AllplanBaseElements.AttributeString(1896, self.ATTR_1896),
        ]
        if self.doc:
            self._add_user_attributes_110mm_45(attr_list)

        attr_set = AllplanBaseElements.AttributeSet(attr_list)
        model_elem.SetAttributes(AllplanBaseElements.Attributes([attr_set]))
        return CreateElementResult([model_elem])


def create_element(build_ele, _doc) -> CreateElementResult:
    return CodoRigido110mP45(build_ele, _doc).create_result()


def _create_element(build_ele, doc) -> CreateElementResult:
    return create_element(build_ele, doc)


class CodoRigido110mP45Script(BaseScriptObject):
    """PythonPart: codo rígido pluvial Ø110 para 45°."""

    def __init__(
        self, build_ele: BuildingElement, script_object_data: BaseScriptObjectData
    ):
        super().__init__(script_object_data)
        self.build_ele = build_ele
        self.doc = self.coord_input.GetInputViewDocument()

    def get_attributes(self, *args, **kwargs):
        return []

    def execute(self, *args, **kwargs) -> CreateElementResult:
        return _create_element(self.build_ele, self.doc)
