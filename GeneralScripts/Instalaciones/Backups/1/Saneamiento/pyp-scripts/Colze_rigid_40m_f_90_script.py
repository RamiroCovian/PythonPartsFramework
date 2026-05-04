# -*- coding: utf-8 -*-
"""Codo rígido fecal Ø40 a 90° (87°) portado de Saneamiento_old."""

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


class CodoRigido40mF90:
    """Solo variante usada en Saneamiento_old: Tipo 3 (1_40mm 87°)."""

    LAYER = 40148  # IS_CON_SANE_FAB

    # En el script old para Tipo 3 están a 0; se mantienen exactos.
    ROT_X_1_40MM_87 = 90.0
    ROT_Y_1_40MM_87 = 180.0
    ROT_Z_1_40MM_87 = -135.0

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

    def _add_user_attributes_40mm_87(self, attr_list):
        """Atributos de usuario exactos de Colze_rigidSane_004.py (40mm 87°)."""
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
                attr_list.append(AllplanBaseElements.AttributeString(attr_6_cc_is_id, ""))
            if attr_pmp_carticulo_id and attr_pmp_carticulo_id > 0:
                attr_list.append(
                    AllplanBaseElements.AttributeString(attr_pmp_carticulo_id, "KN07_004_002")
                )
            if attr_pmp_nom_id and attr_pmp_nom_id > 0:
                attr_list.append(
                    AllplanBaseElements.AttributeString(attr_pmp_nom_id, "COLZE M-F 40Ø 87°")
                )
            if attr_pmp_pes_unitari_id and attr_pmp_pes_unitari_id > 0:
                attr_list.append(
                    AllplanBaseElements.AttributeDouble(attr_pmp_pes_unitari_id, 0.0530)
                )
            if attr_pmp_seccio_id and attr_pmp_seccio_id > 0:
                try:
                    attr_list.append(AllplanBaseElements.AttributeInt(attr_pmp_seccio_id, 40))
                except Exception:
                    attr_list.append(
                        AllplanBaseElements.AttributeString(attr_pmp_seccio_id, "40")
                    )
        except Exception as e:
            print(
                f"[Colze_rigid_40m_f_90_script] Advertencia atributos 40mm 87°: {e}"
            )

    def _build_1_40mm_87(self):
        """Geometría exacta del Tipo 3 (1_40mm 87°) en Saneamiento_old."""
        DIAMETRO = 40.0
        LARGO_VERTICAL = 40.0
        LARGO_HORIZONTAL = 60.0
        SOBRESALE_ANILLO = 10.0
        LARGO_ANILLO = 30.0

        props = self._props(color=70)

        cubo_vertical = AllplanGeo.Polyhedron3D.CreateCuboid(
            AllplanGeo.Point3D(0, 0, 0),
            AllplanGeo.Point3D(DIAMETRO, DIAMETRO, LARGO_VERTICAL),
        )
        cubo_horizontal = AllplanGeo.Polyhedron3D.CreateCuboid(
            AllplanGeo.Point3D(0, 0, LARGO_VERTICAL),
            AllplanGeo.Point3D(LARGO_HORIZONTAL, DIAMETRO, LARGO_VERTICAL + DIAMETRO),
        )
        anillo = AllplanGeo.Polyhedron3D.CreateCuboid(
            AllplanGeo.Point3D(
                LARGO_HORIZONTAL, -SOBRESALE_ANILLO, LARGO_VERTICAL - SOBRESALE_ANILLO
            ),
            AllplanGeo.Point3D(
                LARGO_HORIZONTAL + LARGO_ANILLO,
                DIAMETRO + SOBRESALE_ANILLO,
                LARGO_VERTICAL + DIAMETRO + SOBRESALE_ANILLO,
            ),
        )
        if not anillo.IsValid():
            return props, None

        err, solido = AllplanGeo.MakeUnion(cubo_vertical, cubo_horizontal)
        if err == 0 and solido.IsValid():
            err, solido = AllplanGeo.MakeUnion(solido, anillo)
        if err != 0 or not solido.IsValid():
            return props, None

        cx = (LARGO_HORIZONTAL + DIAMETRO) / 2.0
        cy = DIAMETRO / 2.0
        cz = (LARGO_VERTICAL + DIAMETRO) / 2.0

        if abs(self.ROT_X_1_40MM_87) > 1e-6:
            eje_x = AllplanGeo.Axis3D(
                AllplanGeo.Point3D(cx, cy, cz), AllplanGeo.Vector3D(1, 0, 0)
            )
            solido = AllplanGeo.Rotate(
                solido, eje_x, AllplanGeo.Angle(math.radians(self.ROT_X_1_40MM_87))
            )
        if abs(self.ROT_Y_1_40MM_87) > 1e-6:
            eje_y = AllplanGeo.Axis3D(
                AllplanGeo.Point3D(cx, cy, cz), AllplanGeo.Vector3D(0, 1, 0)
            )
            solido = AllplanGeo.Rotate(
                solido, eje_y, AllplanGeo.Angle(math.radians(self.ROT_Y_1_40MM_87))
            )
        if abs(self.ROT_Z_1_40MM_87) > 1e-6:
            eje_z = AllplanGeo.Axis3D(
                AllplanGeo.Point3D(cx, cy, cz), AllplanGeo.Vector3D(0, 0, 1)
            )
            solido = AllplanGeo.Rotate(
                solido, eje_z, AllplanGeo.Angle(math.radians(self.ROT_Z_1_40MM_87))
            )

        return props, solido

    def _create_copy_common_props(self):
        props = AllplanSettings.AllplanGlobalSettings.GetCurrentCommonProperties()
        props.ColorByLayer = False
        props.Color = 5
        props.Pen = 1
        props.Stroke = 1
        props.Layer = self.LAYER
        return props

    def _apply_copy_attributes(self, model_elem, include_material=False):
        if not self.doc:
            return
        attr_list = []
        try:
            attr_6_cc_is_id = AllplanBaseElements.AttributeService.GetAttributeID(
                self.doc, "6_CC_IS"
            )
            if attr_6_cc_is_id and attr_6_cc_is_id > 0:
                attr_list.append(AllplanBaseElements.AttributeString(attr_6_cc_is_id, "IS"))

            if include_material:
                attr_material_id = AllplanBaseElements.AttributeService.GetAttributeID(
                    self.doc, "Material"
                )
                if attr_material_id and attr_material_id > 0:
                    attr_list.append(
                        AllplanBaseElements.AttributeString(attr_material_id, "CAVITAT")
                    )
        except Exception as ex:
            print(f"[Colze_rigid_40m_f_90_script] Advertencia atributos copia: {ex}")

        if attr_list:
            attr_set = AllplanBaseElements.AttributeSet(attr_list)
            model_elem.SetAttributes(AllplanBaseElements.Attributes([attr_set]))

    def create_result(self) -> CreateElementResult:
        props, solid = self._build_1_40mm_87()
        if solid is None or not solid.IsValid():
            print("Error al crear el codo 40mm 87°.")
            return CreateElementResult([])

        model_elem = AllplanBasisElements.ModelElement3D(props, solid)

        attr_list = [
            AllplanBaseElements.AttributeString(1083, "CS87ºØ40"),
            AllplanBaseElements.AttributeString(1084, "Ø40"),
            AllplanBaseElements.AttributeString(1085, ""),
            AllplanBaseElements.AttributeString(1086, ""),
            AllplanBaseElements.AttributeString(1087, ""),
            AllplanBaseElements.AttributeString(1895, ""),
            AllplanBaseElements.AttributeString(1896, "40"),
        ]
        if self.doc:
            self._add_user_attributes_40mm_87(attr_list)

        attr_set = AllplanBaseElements.AttributeSet(attr_list)
        model_elem.SetAttributes(AllplanBaseElements.Attributes([attr_set]))

        copy_props = self._create_copy_common_props()
        copy_1 = AllplanBasisElements.ModelElement3D(copy_props, solid)
        self._apply_copy_attributes(copy_1, include_material=False)
        copy_2 = AllplanBasisElements.ModelElement3D(copy_props, solid)
        self._apply_copy_attributes(copy_2, include_material=True)

        return CreateElementResult([model_elem, copy_1, copy_2])


def create_element(build_ele, _doc) -> CreateElementResult:
    """Punto de entrada PythonPart."""
    return CodoRigido40mF90(build_ele, _doc).create_result()


def _create_element(build_ele, doc) -> CreateElementResult:
    return create_element(build_ele, doc)


class CodoRigido40mF90Script(BaseScriptObject):
    """PythonPart: codo rígido fecal Ø40 para 90° (87°)."""

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
