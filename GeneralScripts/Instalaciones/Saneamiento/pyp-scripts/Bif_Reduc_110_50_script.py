# -*- coding: utf-8 -*-
"""Bifurcación doble rama 110-50 (DER. Y 110-50 45°) con rama reductora."""

import math
import os
from typing import Optional, List, Dict, Any

import NemAll_Python_Geometry as AllplanGeo
import NemAll_Python_BasisElements as AllplanBasisElements
import NemAll_Python_AllplanSettings as AllplanSettings
import NemAll_Python_BaseElements as AllplanBaseElements
from CreateElementResult import CreateElementResult


def check_allplan_version(_build_ele, _version) -> bool:
    """Se soportan todas las versiones."""
    return True


def _debug_te_y110_40() -> bool:
    """Activa trazas con variable de entorno SANEAMIENTO_DEBUG_TE_Y110_40=1."""
    return str(os.getenv("SANEAMIENTO_DEBUG_TE_Y110_40", "0")).strip().lower() in (
        "1",
        "true",
        "yes",
        "on",
    )


class BifurcacionReduc11050:
    """Bifurcación fija con doble rama (DER. Y 110-50 45°).

    Orientación local final alineada con ``DerivacionY110D110`` (misma secuencia
    rx=90°, ry=270°, rz=0° alrededor del origen) para que el pipeline aplique
    ``try_apply_old_d110_d110_bif_transform`` igual que en la TE 110-110-110.
    """

    type_te = "SAN_Y110_40"

    DIAMETRO_RAMA3: float = 40.0
    DIAMETRO_ANILLO_RAMA3: float = 30.0

    OFFSET_ANILLO_RAMA2_X: float = -15.0
    OFFSET_ANILLO_RAMA2_Y: float = -10.0
    OFFSET_ANILLO_RAMA2_Z: float = 0.0

    OFFSET_ANILLO_RAMA3_X: float = 10.0
    OFFSET_ANILLO_RAMA3_Y: float = 0.0
    OFFSET_ANILLO_RAMA3_Z: float = 0.0

    LARGO_ANILLO_RAMA3: float = 70.0

    OFFSET_RAMAS_X: float = 40.0
    OFFSET_RAMAS_Y: float = 0.0
    OFFSET_RAMAS_Z: float = 0.0

    LAYER = 40148
    DEFAULT_PARAMS: Dict[str, float] = {
        'DIAMETRO': 110.0,
        'DIAMETRO_RAMA': 45.0,
        'LARGO_PRINCIPAL': 301.0,
        'LARGO_RAMA': 30.0,
        'LARGO_RAMA2': 72.0,
        'LARGO_RAMA3': 105.0,
        'ANGULO': 90.0,
        'ANGULO_RAMA2': -45.0,
        'LARGO_ANILLO': 75.0,
        'SOBRESALE_ANILLO': 10.0,
        'COLOR': 70,
        'CLEARANCE_RAMA': 45.0,
        'LARGO_ANILLO_RAMA2': 40.0
    }

    def __init__(self, build_ele, doc=None, params: Optional[Dict[str, float]] = None):
        self.build_ele = build_ele
        self.doc = doc
        self.params = dict(self.DEFAULT_PARAMS)
        if params:
            self.params.update(params)

    def set_diameters(
        self, d_main_in: float, d_branch: float, d_main_out: float
    ) -> None:
        """API compatible con el pipeline TE (orden main_in, branch, main_out)."""
        if _debug_te_y110_40():
            print(
                "[SANEAMIENTO][TE-Y110-40][DEBUG] BifurcacionReduc11050.set_diameters "
                f"main_in={d_main_in} branch={d_branch} main_out={d_main_out}"
            )
        return None

    def build(self) -> List[Any]:
        res = self.create_result()
        return list(getattr(res, "elements", None) or [])

    def create_result(self) -> CreateElementResult:
        if _debug_te_y110_40():
            _keys = tuple(sorted(self.params.keys()))
            print(
                "[SANEAMIENTO][TE-Y110-40][DEBUG] BifurcacionReduc11050.create_result "
                f"param_keys={_keys} COLOR={self.params.get('COLOR')} "
                f"DIAMETRO={self.params.get('DIAMETRO')} DIAMETRO_RAMA="
                f"{self.params.get('DIAMETRO_RAMA')} RAMA3_mm={self.DIAMETRO_RAMA3}"
            )
        elems = self._build_bifurcacion_doble(self.params)
        if _debug_te_y110_40():
            print(
                "[SANEAMIENTO][TE-Y110-40][DEBUG] BifurcacionReduc11050.create_result "
                f"-> {len(elems)} elemento(s)"
            )
        return CreateElementResult(elems)

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
    def _rotate_vec_around_x(vec: AllplanGeo.Vector3D, angle_rad: float) -> AllplanGeo.Vector3D:
        y_new = vec.Y * math.cos(angle_rad) - vec.Z * math.sin(angle_rad)
        z_new = vec.Y * math.sin(angle_rad) + vec.Z * math.cos(angle_rad)
        return AllplanGeo.Vector3D(vec.X, y_new, z_new)

    @staticmethod
    def _make_union(*solids):
        if not solids:
            return None
        result = solids[0]
        for s in solids[1:]:
            err, result2 = AllplanGeo.MakeUnion(result, s)
            if err == 0 and result2 and result2.IsValid():
                result = result2
        return result

    @staticmethod
    def _apply_rotations_origin(solid, rx=0.0, ry=0.0, rz=0.0):
        """Igual que ``DerivacionY110D110._apply_rotations`` (ejes por el origen)."""
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

    def _add_user_attributes_bifurcacion_doble(self, attr_list):
        if not self.doc:
            return
        try:
            attr_6_cc_is_id = AllplanBaseElements.AttributeService.GetAttributeID(self.doc, "6_CC_IS")
            attr_pmp_carticulo_id = AllplanBaseElements.AttributeService.GetAttributeID(self.doc, "pmp_CARTICULO")
            attr_pmp_nom_id = AllplanBaseElements.AttributeService.GetAttributeID(self.doc, "pmp_nom")
            attr_pmp_pes_unitari_id = AllplanBaseElements.AttributeService.GetAttributeID(self.doc, "pmp_pes_unitari")
            attr_pmp_seccio_id = AllplanBaseElements.AttributeService.GetAttributeID(self.doc, "pmp_seccio")

            if attr_6_cc_is_id and attr_6_cc_is_id > 0:
                attr_list.append(AllplanBaseElements.AttributeString(attr_6_cc_is_id, ""))
            if attr_pmp_carticulo_id and attr_pmp_carticulo_id > 0:
                attr_list.append(AllplanBaseElements.AttributeString(attr_pmp_carticulo_id, "KN07_008_003"))
            if attr_pmp_nom_id and attr_pmp_nom_id > 0:
                attr_list.append(AllplanBaseElements.AttributeString(attr_pmp_nom_id, "DER. Y 110-50 45°"))
            if attr_pmp_pes_unitari_id and attr_pmp_pes_unitari_id > 0:
                attr_list.append(AllplanBaseElements.AttributeDouble(attr_pmp_pes_unitari_id, 0.3426))
            if attr_pmp_seccio_id and attr_pmp_seccio_id > 0:
                attr_list.append(AllplanBaseElements.AttributeString(attr_pmp_seccio_id, "Ø110-110-50mm"))
        except Exception as e:
            print(f"[Bif_Reduc_110_50_script] Advertencia al agregar atributos de usuario bifurcación doble: {e}")

    def _build_bifurcacion_doble(self, params: Dict[str, float]) -> List[Any]:
        p = params
        props = self._props(color=p['COLOR'])

        x_dir = AllplanGeo.Vector3D(1, 0, 0)
        z_dir = AllplanGeo.Vector3D(0, 0, 1)
        ang_rad = math.radians(p['ANGULO'])

        base, base_rama = p['DIAMETRO'], p['DIAMETRO_RAMA']
        diam_anillo = base + 2 * p['SOBRESALE_ANILLO']
        diam_anillo_rama = base_rama + 2 * p['SOBRESALE_ANILLO']

        altura_cuerpo = p['LARGO_PRINCIPAL'] - 2 * p['LARGO_ANILLO']
        axis_main = AllplanGeo.AxisPlacement3D(AllplanGeo.Point3D(0, 0, p['LARGO_ANILLO']), x_dir, z_dir)
        cuerpo = AllplanGeo.BRep3D.CreateCuboid(axis_main, base, base, altura_cuerpo)

        offset_xy = (diam_anillo - base) / 2.0
        anillo_sup = AllplanGeo.BRep3D.CreateCuboid(
            AllplanGeo.AxisPlacement3D(
                AllplanGeo.Point3D(-offset_xy, -offset_xy, p['LARGO_ANILLO'] + altura_cuerpo),
                x_dir, z_dir
            ),
            diam_anillo, diam_anillo, p['LARGO_ANILLO']
        )

        z_dir_rama = AllplanGeo.Vector3D(0, -math.sin(ang_rad), math.cos(ang_rad))
        z_top_tubo = p['LARGO_ANILLO'] + altura_cuerpo
        if z_dir_rama.Z >= 0:
            p_rama_z = z_top_tubo - p['CLEARANCE_RAMA'] - p['LARGO_RAMA'] * z_dir_rama.Z
        else:
            p_rama_z = z_top_tubo - p['CLEARANCE_RAMA']
        p_rama = AllplanGeo.Point3D(0, 0, p_rama_z)
        axis_rama = AllplanGeo.AxisPlacement3D(p_rama, x_dir, z_dir_rama)
        rama = AllplanGeo.BRep3D.CreateCuboid(axis_rama, base_rama, base_rama, p['LARGO_RAMA'])

        p_rama_fin = AllplanGeo.Point3D(
            p_rama.X + p['LARGO_RAMA'] * z_dir_rama.X,
            p_rama.Y + p['LARGO_RAMA'] * z_dir_rama.Y,
            p_rama.Z + p['LARGO_RAMA'] * z_dir_rama.Z
        )

        ang_rad2_rel = math.radians(p['ANGULO_RAMA2'])
        OVERLAP = 2.0
        p_rama2 = AllplanGeo.Point3D(
            p_rama_fin.X - OVERLAP * z_dir_rama.X,
            p_rama_fin.Y - OVERLAP * z_dir_rama.Y,
            p_rama_fin.Z - OVERLAP * z_dir_rama.Z
        )
        z_dir_rama2 = self._rotate_vec_around_x(z_dir_rama, ang_rad2_rel)
        axis_rama2 = AllplanGeo.AxisPlacement3D(p_rama2, x_dir, z_dir_rama2)
        altura_rama2_cuerpo = p['LARGO_RAMA2'] - p['LARGO_ANILLO_RAMA2']
        rama2 = AllplanGeo.BRep3D.CreateCuboid(axis_rama2, base_rama, base_rama, altura_rama2_cuerpo)

        p_rama2_fin = AllplanGeo.Point3D(
            p_rama2.X + altura_rama2_cuerpo * z_dir_rama2.X,
            p_rama2.Y + altura_rama2_cuerpo * z_dir_rama2.Y,
            p_rama2.Z + altura_rama2_cuerpo * z_dir_rama2.Z
        )
        anillo_rama2 = AllplanGeo.BRep3D.CreateCuboid(
            AllplanGeo.AxisPlacement3D(
                AllplanGeo.Point3D(
                    p_rama2_fin.X - p['SOBRESALE_ANILLO'] * z_dir_rama2.X - (base_rama - diam_anillo_rama) / 2 - 20 + self.OFFSET_ANILLO_RAMA2_X,
                    p_rama2_fin.Y - p['SOBRESALE_ANILLO'] * z_dir_rama2.Y - (base_rama - diam_anillo_rama) / 2 - 10 + self.OFFSET_ANILLO_RAMA2_Y,
                    p_rama2_fin.Z - p['SOBRESALE_ANILLO'] * z_dir_rama2.Z + self.OFFSET_ANILLO_RAMA2_Z
                ),
                x_dir, z_dir_rama2
            ),
            diam_anillo_rama, diam_anillo_rama, p['LARGO_ANILLO_RAMA2']
        )

        OVERLAP3 = 2.0
        p_rama3 = AllplanGeo.Point3D(
            p_rama2_fin.X - OVERLAP3 * z_dir_rama2.X,
            p_rama2_fin.Y - OVERLAP3 * z_dir_rama2.Y,
            p_rama2_fin.Z - OVERLAP3 * z_dir_rama2.Z
        )
        axis_rama3 = AllplanGeo.AxisPlacement3D(p_rama3, x_dir, z_dir_rama2)
        rama3 = AllplanGeo.BRep3D.CreateCuboid(axis_rama3, self.DIAMETRO_RAMA3, self.DIAMETRO_RAMA3, p['LARGO_RAMA3'])

        diam_anillo_rama3 = self.DIAMETRO_ANILLO_RAMA3 + 2 * p['SOBRESALE_ANILLO']
        anillo_rama3 = AllplanGeo.BRep3D.CreateCuboid(
            AllplanGeo.AxisPlacement3D(
                AllplanGeo.Point3D(
                    p_rama2_fin.X - p['SOBRESALE_ANILLO'] * z_dir_rama2.X - (self.DIAMETRO_ANILLO_RAMA3 - diam_anillo_rama3) / 2 - 20 + self.OFFSET_ANILLO_RAMA3_X,
                    p_rama2_fin.Y - p['SOBRESALE_ANILLO'] * z_dir_rama2.Y - (self.DIAMETRO_ANILLO_RAMA3 - diam_anillo_rama3) / 2 - 10 + self.OFFSET_ANILLO_RAMA3_Y,
                    p_rama2_fin.Z - p['SOBRESALE_ANILLO'] * z_dir_rama2.Z + self.OFFSET_ANILLO_RAMA3_Z
                ),
                x_dir, z_dir_rama2
            ),
            diam_anillo_rama3, diam_anillo_rama3, self.LARGO_ANILLO_RAMA3
        )

        brep_cuerpo = self._make_union(cuerpo, anillo_sup)
        brep_ramas = self._make_union(rama, rama2, anillo_rama2, rama3, anillo_rama3)

        if self.OFFSET_RAMAS_X != 0.0 or self.OFFSET_RAMAS_Y != 0.0 or self.OFFSET_RAMAS_Z != 0.0:
            brep_ramas = AllplanGeo.Move(
                brep_ramas,
                AllplanGeo.Vector3D(self.OFFSET_RAMAS_X, self.OFFSET_RAMAS_Y, self.OFFSET_RAMAS_Z)
            )

        brep_final = self._make_union(brep_cuerpo, brep_ramas)
        # Misma orientación base que DerivacionY110D110 (rx=90+0, ry=270+0, rz=0).
        brep_final = self._apply_rotations_origin(brep_final, 90.0, 270.0, 0.0)
        model_element = AllplanBasisElements.ModelElement3D(props, brep_final)

        attr_list = []
        attr_list.append(AllplanBaseElements.AttributeString(1083, "RED. M-F 110-50Ø"))
        attr_list.append(AllplanBaseElements.AttributeString(1084, "Ø110-50"))
        attr_list.append(AllplanBaseElements.AttributeString(1085, ""))
        attr_list.append(AllplanBaseElements.AttributeString(1086, ""))
        attr_list.append(AllplanBaseElements.AttributeString(1087, ""))
        attr_list.append(AllplanBaseElements.AttributeString(1895, ""))
        attr_list.append(AllplanBaseElements.AttributeString(1896, "110-50"))
        attr_list.append(AllplanBaseElements.AttributeString(1897, ""))
        attr_list.append(AllplanBaseElements.AttributeString(1898, ""))
        attr_list.append(AllplanBaseElements.AttributeString(1899, ""))
        attr_list.append(AllplanBaseElements.AttributeString(1900, ""))
        attr_list.append(AllplanBaseElements.AttributeString(1901, ""))
        attr_list.append(AllplanBaseElements.AttributeString(1902, ""))
        attr_list.append(AllplanBaseElements.AttributeString(1903, ""))
        attr_list.append(AllplanBaseElements.AttributeString(1904, ""))

        if self.doc:
            self._add_user_attributes_bifurcacion_doble(attr_list)

        if attr_list:
            attr_set = AllplanBaseElements.AttributeSet(attr_list)
            attributes = AllplanBaseElements.Attributes([attr_set])
            model_element.SetAttributes(attributes)

        return [model_element]


def create_element(build_ele, doc) -> CreateElementResult:
    return BifurcacionReduc11050(build_ele, doc).create_result()
