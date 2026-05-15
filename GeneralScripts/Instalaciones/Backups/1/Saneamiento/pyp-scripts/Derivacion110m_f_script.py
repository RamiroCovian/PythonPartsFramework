# -*- coding: utf-8 -*-
"""Bifurcación Y Ø110 pluvial, derivación 45° (geometría D110 portada de DerivacioY_45_008).

Instalación fecal: usar otro script cuando exista; este no se carga en tricapa fecal (ver geo_handler).
"""

import math
from typing import Any, List

import NemAll_Python_Geometry as AllplanGeo
import NemAll_Python_AllplanSettings as AllplanSettings
import NemAll_Python_BasisElements as AllplanBasisElements
import NemAll_Python_BaseElements as AllplanBaseElements
from BaseScriptObject import BaseScriptObject
from BuildingElement import BuildingElement
from CreateElementResult import CreateElementResult


def check_allplan_version(_build_ele, _version) -> bool:
    return True


class DerivacionY110D110:
    """Equivalente a TipoTubo==0 en DerivacioY_45_008; solo red pluvial (tricapa_v / p_110)."""

    type_te = "SAN_Y110_PLUVIAL"
    LAYER = 40148
    COLOR = 120
    ROT_X_D110 = 0.0
    ROT_Y_D110 = 0.0
    ROT_Z_D110 = 0.0
    ROTAR_FINAL_Y_GRADOS = 270.0
    MAINTAIN_PROPORTIONS = True
    REF_DIAM_PROPORTION = 110.0
    RAMA_OFFSET_Z = 42.0
    ANGULO_DEFAULT = 45.0
    # Valores base D110 (TIPO_TUBO_MAP[0] + DEFAULTS del script antiguo).
    DIAMETRO = 110.0
    LARGO_PRINCIPAL = 373.0
    LARGO_RAMA = 200.0
    LARGO_ANILLO = 73.0
    SOBRESALE_ANILLO = 10.0

    def __init__(self, build_ele: BuildingElement, doc=None):
        self.build_ele = build_ele
        self.doc = doc

    def set_diameters(
        self, _d_main_in: float, _d_branch: float, _d_main_out: float
    ) -> None:
        pass

    def build(self) -> List[Any]:
        res = self.create_result()
        return list(getattr(res, "elements", None) or [])

    def _attr_val(self, name: str, default: float) -> float:
        a = getattr(self.build_ele, name, None)
        if hasattr(a, "value"):
            try:
                return float(a.value)
            except (TypeError, ValueError):
                return default
        return default

    def _props(self, color: int) -> Any:
        p = AllplanSettings.AllplanGlobalSettings.GetCurrentCommonProperties()
        p.Color = int(color)
        for attr in ("Pen", "Stroke", "Layer"):
            v = getattr(self.build_ele, attr, None)
            if hasattr(v, "value"):
                setattr(p, attr, v.value)
        return p

    @staticmethod
    def _make_union(*solids):
        result = solids[0]
        for s in solids[1:]:
            err, result2 = AllplanGeo.MakeUnion(result, s)
            if err == 0 and result2 and result2.IsValid():
                result = result2
        return result

    @staticmethod
    def _apply_rotations(solid, rx=0.0, ry=0.0, rz=0.0):
        for angle, axis in zip([rx, ry, rz], ["x", "y", "z"]):
            if abs(angle) > 1e-6:
                mat = AllplanGeo.Matrix3D()
                if axis == "x":
                    axis_line = AllplanGeo.Line3D(0, 0, 0, 1, 0, 0)
                elif axis == "y":
                    axis_line = AllplanGeo.Line3D(0, 0, 0, 0, 1, 0)
                else:
                    axis_line = AllplanGeo.Line3D(0, 0, 0, 0, 0, 1)
                mat.SetRotation(axis_line, AllplanGeo.Angle(math.radians(angle)))
                solid = AllplanGeo.Transform(solid, mat)
        return solid

    @staticmethod
    def _anillo_axis(base: float, diam_an: float, z_top: float, x_dir, z_dir):
        delta = (base - diam_an) / 2.0
        return AllplanGeo.AxisPlacement3D(
            AllplanGeo.Point3D(delta, delta, z_top), x_dir, z_dir
        )

    def _add_user_attributes_110mm(self, attr_list):
        if not self.doc:
            return
        doc = self.doc
        get_id = AllplanBaseElements.AttributeService.GetAttributeID
        try:
            id6 = get_id(doc, "6_CC_IS")
            id_cart = get_id(doc, "pmp_CARTICULO")
            id_nom = get_id(doc, "pmp_nom")
            id_pes = get_id(doc, "pmp_pes_unitari")
            id_sec = get_id(doc, "pmp_seccio")
            if id6 and id6 > 0:
                attr_list.append(AllplanBaseElements.AttributeString(id6, ""))
            if id_cart and id_cart > 0:
                attr_list.append(
                    AllplanBaseElements.AttributeString(id_cart, "KN07_008_002")
                )
            if id_nom and id_nom > 0:
                attr_list.append(
                    AllplanBaseElements.AttributeString(id_nom, "DER. Y 110Ø 45°")
                )
            if id_pes and id_pes > 0:
                attr_list.append(AllplanBaseElements.AttributeDouble(id_pes, 0.2509))
            if id_sec and id_sec > 0:
                try:
                    attr_list.append(AllplanBaseElements.AttributeInt(id_sec, 110))
                except Exception:
                    attr_list.append(AllplanBaseElements.AttributeString(id_sec, "110"))
        except Exception as e:
            print(f"[Derivacion110m_f_script] Atributos usuario 110mm pluvial: {e}")

    def create_result(self) -> CreateElementResult:
        angulo = self._attr_val("Angulo", self.ANGULO_DEFAULT)
        diametro = self.DIAMETRO
        largo = self._attr_val("Largo", self.LARGO_PRINCIPAL)
        largo2 = self._attr_val("LargoRama", self.LARGO_RAMA)
        largo_anillo = self._attr_val("LargoAnillo", self.LARGO_ANILLO)
        sobresale_anillo = self._attr_val("SobresaleAnillo", self.SOBRESALE_ANILLO)
        rama_offset_z_local = self.RAMA_OFFSET_Z
        branch_diametro = diametro
        branch_largo_anillo = largo_anillo

        if self.MAINTAIN_PROPORTIONS and diametro > 0:
            scale = diametro / self.REF_DIAM_PROPORTION
            largo = max(1.0, largo * scale)
            largo2 = max(1.0, largo2 * scale)
            largo_anillo = max(1.0, largo_anillo * scale)
            sobresale_anillo = max(0.1, sobresale_anillo * scale)
            rama_offset_z_local = self.RAMA_OFFSET_Z * scale

        diametro_anillo_main = diametro + 2 * sobresale_anillo
        diametro_anillo_branch = branch_diametro + 2 * sobresale_anillo
        angulo_rad = math.radians(angulo)

        base = diametro
        altura = largo - 2 * largo_anillo
        p1 = AllplanGeo.Point3D(0, 0, largo_anillo)
        x_dir = AllplanGeo.Vector3D(1, 0, 0)
        z_dir1 = AllplanGeo.Vector3D(0, 0, 1)
        axis1 = AllplanGeo.AxisPlacement3D(p1, x_dir, z_dir1)
        cubo1 = AllplanGeo.BRep3D.CreateCuboid(axis1, base, base, altura)
        anillo1 = AllplanGeo.BRep3D.CreateCuboid(
            self._anillo_axis(
                base, diametro_anillo_main, largo_anillo + altura, x_dir, z_dir1
            ),
            diametro_anillo_main,
            diametro_anillo_main,
            largo_anillo,
        )

        base2 = branch_diametro
        half_largo = largo * 0.5
        sin_a, cos_a = math.sin(angulo_rad), math.cos(angulo_rad)
        altura2 = largo2 - branch_largo_anillo
        p2 = AllplanGeo.Point3D(0, 0, half_largo - rama_offset_z_local)
        z_dir2 = AllplanGeo.Vector3D(0, -sin_a, cos_a)
        axis2 = AllplanGeo.AxisPlacement3D(p2, x_dir, z_dir2)
        cubo2 = AllplanGeo.BRep3D.CreateCuboid(axis2, base2, base2, altura2)
        p2_fin = AllplanGeo.Point3D(
            p2.X + altura2 * z_dir2.X,
            p2.Y + altura2 * z_dir2.Y,
            p2.Z + altura2 * z_dir2.Z,
        )

        delta_branch = (base2 - diametro_anillo_branch) / 2.0
        y_dir2 = AllplanGeo.Vector3D(0, cos_a, sin_a)
        anillo_rama = AllplanGeo.BRep3D.CreateCuboid(
            AllplanGeo.AxisPlacement3D(
                AllplanGeo.Point3D(
                    p2_fin.X
                    + delta_branch * x_dir.X
                    + delta_branch * y_dir2.X
                    - sobresale_anillo * z_dir2.X,
                    p2_fin.Y
                    + delta_branch * x_dir.Y
                    + delta_branch * y_dir2.Y
                    - sobresale_anillo * z_dir2.Y,
                    p2_fin.Z
                    + delta_branch * x_dir.Z
                    + delta_branch * y_dir2.Z
                    - sobresale_anillo * z_dir2.Z,
                ),
                x_dir,
                z_dir2,
            ),
            diametro_anillo_branch,
            diametro_anillo_branch,
            branch_largo_anillo,
        )

        brep_ext = self._make_union(cubo1, cubo2, anillo1, anillo_rama)
        brep_ext = self._apply_rotations(
            brep_ext,
            rx=90.0 + self.ROT_X_D110,
            ry=self.ROTAR_FINAL_Y_GRADOS + self.ROT_Y_D110,
            rz=self.ROT_Z_D110,
        )

        props = self._props(self.COLOR)
        props.Layer = self.LAYER
        props.ColorByLayer = False
        model_element = AllplanBasisElements.ModelElement3D(props, brep_ext)

        fixed_attrs = [
            (1083, "DER. Y 110Ø 45°"),
            (1084, "Ø110"),
            (1085, ""),
            (1086, ""),
            (1087, ""),
            (1895, ""),
            (1896, "110-110"),
            (1897, ""),
            (1898, ""),
            (1899, ""),
            (1900, ""),
            (1901, ""),
            (1902, ""),
            (1903, ""),
            (1904, ""),
        ]
        attr_list = [
            AllplanBaseElements.AttributeString(k, v) for k, v in fixed_attrs
        ]
        if self.doc:
            self._add_user_attributes_110mm(attr_list)

        attr_set = AllplanBaseElements.AttributeSet(attr_list)
        model_element.SetAttributes(AllplanBaseElements.Attributes([attr_set]))
        return CreateElementResult([model_element])


def create_element(build_ele, _doc) -> CreateElementResult:
    return DerivacionY110D110(build_ele, _doc).create_result()


class Derivacion110mScript(BaseScriptObject):
    def __init__(self, build_ele: BuildingElement, script_object_data: Any):
        super().__init__(script_object_data)
        self.build_ele = build_ele
        self.doc = self.coord_input.GetInputViewDocument()

    def get_attributes(self, *args, **kwargs):
        return []

    def execute(self, *args, **kwargs) -> CreateElementResult:
        return create_element(self.build_ele, self.doc)
