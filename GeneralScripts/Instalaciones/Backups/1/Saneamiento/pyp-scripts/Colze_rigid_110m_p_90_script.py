# -*- coding: utf-8 -*-
"""Codo rigido pluvial 110mm 90/87 (L1000_D87, variante usada en Saneamiento_old)."""

import math

import NemAll_Python_Geometry as AllplanGeo
import NemAll_Python_BasisElements as AllplanBasisElements
import NemAll_Python_AllplanSettings as AllplanSettings
import NemAll_Python_BaseElements as AllplanBaseElements
from CreateElementResult import CreateElementResult
from BaseScriptObject import BaseScriptObject, BaseScriptObjectData
from BuildingElement import BuildingElement


def check_allplan_version(_build_ele, _version) -> bool:
    """Check the current Allplan version (se soportan todas las versiones)."""
    return True


class CodoRigido110mP90:
    """Solo codo 110mm 87/90 equivalente a TipoColze==5 en Saneamiento_old."""

    LAYER = 40148  # IS_CON_SANE_FAB
    COLOR = 120

    # Rotaciones hardcodeadas del modelo 110mm 87° (TipoColze==5)
    ROT_X_110MM_87 = -90.0
    ROT_Y_110MM_87 = 180.0
    ROT_Z_110MM_87 = -45.0

    # Geometria del codo 110mm 87° (L1000_D87)
    DIAMETRO = 110.0
    LARGO_VERTICAL = 110.0
    LARGO_INCLINADA = 110.0
    LARGO_HORIZONTAL = 110.0
    ANGULO_INCLINADA = 45.0
    ANGULO_HORIZONTAL = 90.0
    LARGO_ANILLO = 75.0
    SOBRESALE_ANILLO = 10.0

    # Atributos exactos usados en Saneamiento_old para 110mm 87°
    ATTR_1083 = "COLZE M-F 110Ø 87º"
    ATTR_1084 = "Ø110"
    ATTR_1896 = "110"
    ATTR_6_CC_IS = ""
    PMP_CARTICULO = "KN07_004_004"
    PMP_NOM = "COLZE M-F 110Ø 87°"
    PMP_PES_UNITARI = 0.4633
    PMP_SECCIO = 110

    def __init__(self, build_ele, doc=None):
        self.build_ele = build_ele
        self.doc = doc

    def _props(self, color: int, pen: int = 1, stroke: int = 1, layer: int = None):
        if layer is None:
            layer = self.LAYER
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

    def _add_user_attributes_110mm_87(self, attr_list):
        if not self.doc:
            return

        try:
            attr_6_cc_is_id = AllplanBaseElements.AttributeService.GetAttributeID(
                self.doc, "6_CC_IS"
            )
            attr_pmp_carticulo_id = AllplanBaseElements.AttributeService.GetAttributeID(
                self.doc, "pmp_CARTICULO"
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
                try:
                    attr_list.append(
                        AllplanBaseElements.AttributeInt(
                            attr_pmp_seccio_id, int(self.PMP_SECCIO)
                        )
                    )
                except Exception:
                    attr_list.append(
                        AllplanBaseElements.AttributeString(
                            attr_pmp_seccio_id, str(self.PMP_SECCIO)
                        )
                    )
        except Exception as e:
            print(
                f"[Colze_rigid_110m_p_90_script] Advertencia atributos 110mm 87°: {e}"
            )

    def _build_110mm_87_variant_5(self):
        props = self._props(color=self.COLOR)

        cubo0 = self._crear_prisma(self.DIAMETRO, self.LARGO_VERTICAL)

        rad_inc = math.radians(self.ANGULO_INCLINADA)
        cubo1 = self._crear_prisma(self.DIAMETRO, self.LARGO_INCLINADA)
        m1 = AllplanGeo.Matrix3D()
        m1.SetRotation(AllplanGeo.Line3D(0, 0, 0, 1, 0, 0), AllplanGeo.Angle(-rad_inc))
        cubo1 = AllplanGeo.Transform(cubo1, m1)
        t1 = AllplanGeo.Matrix3D()
        t1.SetTranslation(AllplanGeo.Vector3D(0, 0, self.LARGO_VERTICAL))
        cubo1 = AllplanGeo.Transform(cubo1, t1)

        dz = self.LARGO_INCLINADA * math.cos(rad_inc)
        dy = self.LARGO_INCLINADA * math.sin(rad_inc)

        rad_h = math.radians(self.ANGULO_HORIZONTAL)
        cubo2 = self._crear_prisma(self.DIAMETRO, self.LARGO_HORIZONTAL)
        m2 = AllplanGeo.Matrix3D()
        m2.SetRotation(AllplanGeo.Line3D(0, 0, 0, 1, 0, 0), AllplanGeo.Angle(-rad_h))
        cubo2 = AllplanGeo.Transform(cubo2, m2)
        t2 = AllplanGeo.Matrix3D()
        t2.SetTranslation(AllplanGeo.Vector3D(0, dy, self.LARGO_VERTICAL + dz))
        cubo2 = AllplanGeo.Transform(cubo2, t2)

        anillo = AllplanGeo.Polyhedron3D.CreateCuboid(
            AllplanGeo.Point3D(
                -self.SOBRESALE_ANILLO, -self.SOBRESALE_ANILLO, -self.LARGO_ANILLO
            ),
            AllplanGeo.Point3D(
                self.DIAMETRO + self.SOBRESALE_ANILLO,
                self.DIAMETRO + self.SOBRESALE_ANILLO,
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

        eje_z = AllplanGeo.Axis3D(AllplanGeo.Point3D(0, 0, 0), AllplanGeo.Vector3D(0, 0, 1))
        s = AllplanGeo.Rotate(codo, eje_z, AllplanGeo.Angle(math.radians(90)))
        eje_x = AllplanGeo.Axis3D(AllplanGeo.Point3D(0, 0, 0), AllplanGeo.Vector3D(1, 0, 0))
        s = AllplanGeo.Rotate(s, eje_x, AllplanGeo.Angle(math.radians(180)))

        cx = self.DIAMETRO / 2.0
        cy = self.DIAMETRO / 2.0 + self.LARGO_INCLINADA * math.sin(
            math.radians(self.ANGULO_INCLINADA)
        ) / 2.0
        cz = (
            self.LARGO_VERTICAL
            + self.LARGO_INCLINADA * math.cos(math.radians(self.ANGULO_INCLINADA))
            + self.LARGO_HORIZONTAL
        ) / 2.0

        if abs(self.ROT_X_110MM_87) > 1e-6:
            eje_x_rot = AllplanGeo.Axis3D(
                AllplanGeo.Point3D(cx, cy, cz), AllplanGeo.Vector3D(1, 0, 0)
            )
            s = AllplanGeo.Rotate(
                s, eje_x_rot, AllplanGeo.Angle(math.radians(self.ROT_X_110MM_87))
            )
        if abs(self.ROT_Y_110MM_87) > 1e-6:
            eje_y_rot = AllplanGeo.Axis3D(
                AllplanGeo.Point3D(cx, cy, cz), AllplanGeo.Vector3D(0, 1, 0)
            )
            s = AllplanGeo.Rotate(
                s, eje_y_rot, AllplanGeo.Angle(math.radians(self.ROT_Y_110MM_87))
            )
        if abs(self.ROT_Z_110MM_87) > 1e-6:
            eje_z_rot = AllplanGeo.Axis3D(
                AllplanGeo.Point3D(cx, cy, cz), AllplanGeo.Vector3D(0, 0, 1)
            )
            s = AllplanGeo.Rotate(
                s, eje_z_rot, AllplanGeo.Angle(math.radians(self.ROT_Z_110MM_87))
            )

        return props, s

    def create_result(self) -> CreateElementResult:
        props, solid = self._build_110mm_87_variant_5()
        if solid is None or not solid.IsValid():
            print("Error al crear el codo 110mm 87°.")
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
        self._add_user_attributes_110mm_87(attr_list)

        attr_set = AllplanBaseElements.AttributeSet(attr_list)
        model_elem.SetAttributes(AllplanBaseElements.Attributes([attr_set]))
        return CreateElementResult([model_elem])


def create_element(build_ele, _doc) -> CreateElementResult:
    return CodoRigido110mP90(build_ele, _doc).create_result()


def _create_element(build_ele, doc) -> CreateElementResult:
    return create_element(build_ele, doc)


class CodoRigido110mP90Script(BaseScriptObject):
    """PythonPart: codo rigido pluvial Ø110 para 90°/87°."""

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
