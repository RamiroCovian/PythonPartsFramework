# -*- coding: utf-8 -*-
"""Bifurcación de saneamiento (derivación 45°) """

import math
from typing import Optional, Any, Dict

import NemAll_Python_Geometry as AllplanGeo
import NemAll_Python_IFW_ElementAdapter as AllplanElementAdapter  # noqa: F401 (import de contexto Allplan)
import NemAll_Python_AllplanSettings as AllplanSettings
import NemAll_Python_BasisElements as AllplanBasisElements
import NemAll_Python_BaseElements as AllplanBaseElements

from BuildingElement import BuildingElement
from CreateElementResult import CreateElementResult


# ===== Requisito estándar =====
def check_allplan_version(_build_ele: BuildingElement, _version: str) -> bool:
    """Se soportan todas las versiones."""
    return True
# ==============================


class BifurcacionDerivacion45:
    # --- Rotaciones hardcodeadas para D110 (TipoTubo == 0) --- #
    ROT_X_D110: float = 0.0  # grados-360,180,0
    ROT_Y_D110: float = 0.0  # grados
    ROT_Z_D110: float = 0.0  # grados
    # --- Rotaciones hardcodeadas para D40 (TipoTubo == 2 o diámetro == 40) --- #
    ROT_X_D40: float = 0.0  # grados
    ROT_Y_D40: float = 0.0  # grados
    ROT_Z_D40: float = 180.0  # grados90,180,180
    # --- Rotaciones hardcodeadas para REDUCCION_110_50 (TipoTubo == 3) --- #
    ROT_X_D3: float = 180.0  # grados
    ROT_Y_D3: float = 0.0  # grados
    ROT_Z_D3: float = 0.0  # grados
    """Implementación OO de la bifurcación de saneamiento con derivación a 45°.

    - Controlada por `TipoTubo` y atributos del `build_ele`.
    - Mantiene lógica y “hardcodes” del script original.
    """

    # --- Parámetros y utilidades centralizados --- #
    DEFAULTS: Dict[str, float] = {
        'DIAMETRO': 110.0,
        'LARGO': 125.0,
        'LARGO_RAMA': 200.0,
        'ANGULO': 45.0,
        'LARGO_ANILLO': 73.0,
        'SOBRESALE_ANILLO': 10.0,
        'RAMA_OFFSET_Z': 42.0,
    }

    TIPO_TUBO_MAP: Dict[int, tuple] = {
        0: (110.0, 373.0),  # D110
        2: (40.0,  450.0),  # D40
        3: (110.0, 400.0)   # REDUCCION_110_50 (bifurcación con reducción de 110mm a 50mm)
    }

    MAINTAIN_PROPORTIONS: bool = True
    REF_DIAM_PROPORTION: float = 110.0

    # --- Variables agrupadas por tipo de objeto --- #

    # === D110 (TipoTubo == 0) ===
    # Usa valores por defecto y proporcionales, no requiere hardcodes adicionales

    # === D40 (TipoTubo == 2 o diámetro == 40) ===
    HARD: Dict[str, float] = {
        # D40
        'LARGO_PRINCIPAL_40MM': 495.0,         # Largo principal del tubo D40
        'LARGO_RAMA_40MM': 270.0,              # Largo de la rama D40
        'DIAMETRO_RAMA_40MM': 40.0,            # Diámetro de la rama D40
        'LARGO_ANILLO_40MM': 109.0,            # Largo del anillo D40
        'SOBRESALE_ANILLO_40MM': 15.0,         # Sobresale anillo D40
        'OFFSET_RAMA_40MM': 6.0,               # Offset rama D40

        # === REDUCCION_110_50 (TipoTubo == 3) ===
        'LARGO_PRINCIPAL_3': 298.0,            # Largo principal reducción 110-50
        'LARGO_RAMA_3_HORIZONTAL': 28.0,       # Largo rama horizontal reducción 110-50
        'LARGO_RAMA_3_INCLINADO': 31.0,        # Largo rama inclinada reducción 110-50
        'ANGULO_RAMA_3_HORIZONTAL': 90.0,      # Ángulo rama horizontal reducción 110-50
        'ANGULO_RAMA_3_INCLINADO': 45.0,       # Ángulo rama inclinada reducción 110-50
        'OFFSET_RAMA_3': 74.2,                 # Offset rama reducción 110-50
        'LARGO_ANILLO_3': 73.0,                # Largo anillo principal reducción 110-50
        'LARGO_ANILLO_RAMA_3': 40.0            # Largo anillo rama reducción 110-50
    }

    # --- Constante de rotación final --- #
    ROTAR_FINAL_Y_GRADOS: float = 270.0
    LAYER = 40148  # IS_CON_SANE_FAB (is cone fab)

    def __init__(self, build_ele: BuildingElement, doc=None):
        self.build_ele = build_ele
        self.doc = doc

    # ---------- API ----------
    def create_result(self) -> CreateElementResult:
        d = self.DEFAULTS
        h = self.HARD

        # --- Lectura de atributos de paleta ---
        diametro = self._attr_int("Diametro", d['DIAMETRO'])
        largo = self._attr_val("Largo", d['LARGO'])
        largo2 = self._attr_val("LargoRama", d['LARGO_RAMA'])
        angulo = self._attr_val("Angulo", d['ANGULO'])
        largo_anillo = self._attr_val("LargoAnillo", d['LARGO_ANILLO'])
        sobresale_anillo = self._attr_val("SobresaleAnillo", d['SOBRESALE_ANILLO'])
        rama_offset_z_local = d['RAMA_OFFSET_Z']

        tipo_val = self._attr_int("TipoTubo", None)
        if tipo_val is not None and tipo_val in self.TIPO_TUBO_MAP:
            diametro, largo = self.TIPO_TUBO_MAP[tipo_val]

        # --- Hardcodes y ajustes por tipo ---
        if tipo_val == 2 or diametro == 40:
            branch_diametro = h['DIAMETRO_RAMA_40MM']
            largo2 = h['LARGO_RAMA_40MM']
            largo_anillo = h['LARGO_ANILLO_40MM']
            sobresale_anillo = h['SOBRESALE_ANILLO_40MM']
            largo = h['LARGO_PRINCIPAL_40MM']
            largo_anillo_rama = h['LARGO_ANILLO_40MM']
        elif tipo_val == 3:
            branch_diametro = 50.0
            largo2 = h['LARGO_RAMA_3_HORIZONTAL'] + h['LARGO_RAMA_3_INCLINADO']
            largo_anillo = h['LARGO_ANILLO_3']
            # sobresale_anillo queda del default
            largo = h['LARGO_PRINCIPAL_3']
            largo_anillo_rama = h['LARGO_ANILLO_RAMA_3']
        else:
            branch_diametro = diametro
            largo_anillo_rama = largo_anillo

        # --- Escalado proporcional ---
        # No aplicar escalado a reducción 110-50 (TipoTubo == 3)
        if self.MAINTAIN_PROPORTIONS and diametro > 0 and not (tipo_val == 3):
            scale = diametro / self.REF_DIAM_PROPORTION
            largo = max(1.0, largo * scale)
            largo2 = max(1.0, largo2 * scale)
            largo_anillo = max(1.0, largo_anillo * scale)
            sobresale_anillo = max(0.1, sobresale_anillo * scale)
            rama_offset_z_local = d['RAMA_OFFSET_Z'] * scale
        if diametro == 40.0:
            largo += 20.0  # ajuste original

        # --- Geometría principal ---
        diametro_anillo_main = diametro + 2 * sobresale_anillo
        diametro_anillo_branch = branch_diametro + 2 * sobresale_anillo

        angulo_rad = math.radians(angulo)
        branch_largo_anillo = h['LARGO_ANILLO_RAMA_3'] if tipo_val == 3 else largo_anillo

        base = diametro
        altura = largo - 2 * largo_anillo

        p1 = AllplanGeo.Point3D(0, 0, largo_anillo)
        x_dir = AllplanGeo.Vector3D(1, 0, 0)
        z_dir1 = AllplanGeo.Vector3D(0, 0, 1)

        axis1 = AllplanGeo.AxisPlacement3D(p1, x_dir, z_dir1)
        cubo1 = AllplanGeo.BRep3D.CreateCuboid(axis1, base, base, altura)

        anillo1 = AllplanGeo.BRep3D.CreateCuboid(
            self._anillo_axis(base, diametro_anillo_main, largo_anillo + altura, x_dir, z_dir1),
            diametro_anillo_main, diametro_anillo_main, largo_anillo
        )

        base2 = branch_diametro
        half_largo = largo * 0.5
        sin_a, cos_a = math.sin(angulo_rad), math.cos(angulo_rad)

        # Rama (según tipo)
        if tipo_val == 3:
            # tramo horizontal
            p2 = AllplanGeo.Point3D(0, 0, half_largo - rama_offset_z_local + self.HARD['OFFSET_RAMA_3'])
            ang_h_rad = math.radians(self.HARD['ANGULO_RAMA_3_HORIZONTAL'])
            z_dir_h = AllplanGeo.Vector3D(0, -math.sin(ang_h_rad), math.cos(ang_h_rad))
            axis_h = AllplanGeo.AxisPlacement3D(p2, x_dir, z_dir_h)
            tramo_h = AllplanGeo.BRep3D.CreateCuboid(axis_h, base2, base2, self.HARD['LARGO_RAMA_3_HORIZONTAL'])

            # tramo inclinado
            p2_incl = AllplanGeo.Point3D(
                p2.X + self.HARD['LARGO_RAMA_3_HORIZONTAL'] * z_dir_h.X,
                p2.Y + self.HARD['LARGO_RAMA_3_HORIZONTAL'] * z_dir_h.Y,
                p2.Z + self.HARD['LARGO_RAMA_3_HORIZONTAL'] * z_dir_h.Z
            )
            ang_i_rad = math.radians(self.HARD['ANGULO_RAMA_3_INCLINADO'])
            z_dir2 = AllplanGeo.Vector3D(0, -math.sin(ang_i_rad), math.cos(ang_i_rad))
            axis_incl = AllplanGeo.AxisPlacement3D(p2_incl, x_dir, z_dir2)
            tramo_incl = AllplanGeo.BRep3D.CreateCuboid(axis_incl, base2, base2, self.HARD['LARGO_RAMA_3_INCLINADO'])

            cubo2 = self._make_union(tramo_h, tramo_incl)

            p2_fin = AllplanGeo.Point3D(
                p2_incl.X + self.HARD['LARGO_RAMA_3_INCLINADO'] * z_dir2.X,
                p2_incl.Y + self.HARD['LARGO_RAMA_3_INCLINADO'] * z_dir2.Y,
                p2_incl.Z + self.HARD['LARGO_RAMA_3_INCLINADO'] * z_dir2.Z
            )
        else:
            altura2 = largo2 - branch_largo_anillo
            if tipo_val == 2 or diametro == 40.0:
                p2 = AllplanGeo.Point3D(0, 0, half_largo - rama_offset_z_local + self.HARD['OFFSET_RAMA_40MM'])
            else:
                p2 = AllplanGeo.Point3D(0, 0, half_largo - rama_offset_z_local)

            z_dir2 = AllplanGeo.Vector3D(0, -sin_a, cos_a)
            axis2 = AllplanGeo.AxisPlacement3D(p2, x_dir, z_dir2)
            cubo2 = AllplanGeo.BRep3D.CreateCuboid(axis2, base2, base2, altura2)

            p2_fin = AllplanGeo.Point3D(
                p2.X + altura2 * z_dir2.X,
                p2.Y + altura2 * z_dir2.Y,
                p2.Z + altura2 * z_dir2.Z
            )

        # Anillo de la rama
        delta_branch = (base2 - diametro_anillo_branch) / 2.0
        y_dir2 = AllplanGeo.Vector3D(0, cos_a, sin_a)  # usado para desplazar a esquina “exterior”
        # z_dir2 debe existir en ambos caminos; en tipo 3 ya lo definimos arriba
        anillo_rama = AllplanGeo.BRep3D.CreateCuboid(
            AllplanGeo.AxisPlacement3D(
                AllplanGeo.Point3D(
                    p2_fin.X + delta_branch * x_dir.X + delta_branch * y_dir2.X - sobresale_anillo * z_dir2.X,
                    p2_fin.Y + delta_branch * x_dir.Y + delta_branch * y_dir2.Y - sobresale_anillo * z_dir2.Y,
                    p2_fin.Z + delta_branch * x_dir.Z + delta_branch * y_dir2.Z - sobresale_anillo * z_dir2.Z
                ),
                x_dir, z_dir2
            ),
            diametro_anillo_branch, diametro_anillo_branch, branch_largo_anillo
        )

        brep_ext = self._make_union(cubo1, cubo2, anillo1, anillo_rama)


        # --- Rotaciones finales (como en script original) ---
        if tipo_val == 2 or diametro == 40.0:
            # Rotación hardcodeada para D40
            brep_ext = self._apply_rotations(
                brep_ext,
                rx=270.0 + self.ROT_X_D40,
                ry=self.ROTAR_FINAL_Y_GRADOS + self.ROT_Y_D40,
                rz=self.ROT_Z_D40
            )
        elif tipo_val == 0:
            # Rotación hardcodeada para D110
            brep_ext = self._apply_rotations(
                brep_ext,
                rx=90.0 + self.ROT_X_D110,
                ry=self.ROTAR_FINAL_Y_GRADOS + self.ROT_Y_D110,
                rz=self.ROT_Z_D110
            )
        elif tipo_val is None or tipo_val == 1:
            brep_ext = self._apply_rotations(brep_ext, rx=90.0, ry=self.ROTAR_FINAL_Y_GRADOS, rz=0.0)
        elif tipo_val == 3:
            # Rotación hardcodeada para reducción 110-50
            brep_ext = self._apply_rotations(
                brep_ext,
                rx=270.0 + self.ROT_X_D3,
                ry=self.ROTAR_FINAL_Y_GRADOS + self.ROT_Y_D3,
                rz=self.ROT_Z_D3
            )
        else:
            brep_ext = self._apply_rotations(brep_ext, rx=270.0, ry=self.ROTAR_FINAL_Y_GRADOS, rz=0.0)

        # --- Color específico para D110, 70 para los demás ---
        color = 120 if tipo_val == 0 else 70
        props = self._props(color)
        props.Layer = self.LAYER  # IS_CON_SANE_FAB (is cone fab)
        props.ColorByLayer = False  # No afectar el color
        model_element = AllplanBasisElements.ModelElement3D(props, brep_ext)

        # Add attributes based on tipo_val (bifurcation type)
        attr_list = []
        if tipo_val == 0:
            # YØ110-45°
            attr_list.append(AllplanBaseElements.AttributeString(1083, "DER. Y 110Ø 45°"))  # Custom attribute 01
            attr_list.append(AllplanBaseElements.AttributeString(1084, "Ø110"))                # Custom attribute 02
            attr_list.append(AllplanBaseElements.AttributeString(1085, ""))                    # Custom attribute 03
            attr_list.append(AllplanBaseElements.AttributeString(1086, ""))                    # Custom attribute 04
            attr_list.append(AllplanBaseElements.AttributeString(1087, ""))                    # Custom attribute 05
            attr_list.append(AllplanBaseElements.AttributeString(1895, ""))                    # Custom attribute 06
            attr_list.append(AllplanBaseElements.AttributeString(1896, "110-110"))             # Custom attribute 07
            attr_list.append(AllplanBaseElements.AttributeString(1897, ""))                    # Custom attribute 08
            attr_list.append(AllplanBaseElements.AttributeString(1898, ""))                    # Custom attribute 09
            attr_list.append(AllplanBaseElements.AttributeString(1899, ""))                    # Custom attribute 10
            attr_list.append(AllplanBaseElements.AttributeString(1900, ""))                    # Custom attribute 11
            attr_list.append(AllplanBaseElements.AttributeString(1901, ""))                    # Custom attribute 12
            attr_list.append(AllplanBaseElements.AttributeString(1902, ""))                    # Custom attribute 13
            attr_list.append(AllplanBaseElements.AttributeString(1903, ""))                    # Custom attribute 14
            attr_list.append(AllplanBaseElements.AttributeString(1904, ""))                    # Custom attribute 15
            
            # Agregar atributos de usuario adicionales si hay documento disponible
            if self.doc:
                self._add_user_attributes_110mm(attr_list)
        elif tipo_val == 2:
            # YØ40-45°
            attr_list.append(AllplanBaseElements.AttributeString(1083, "DER. Y 40Ø 45°"))     # Custom attribute 01
            attr_list.append(AllplanBaseElements.AttributeString(1084, "Ø40"))                 # Custom attribute 02
            attr_list.append(AllplanBaseElements.AttributeString(1085, ""))                    # Custom attribute 03
            attr_list.append(AllplanBaseElements.AttributeString(1086, ""))                    # Custom attribute 04
            attr_list.append(AllplanBaseElements.AttributeString(1087, ""))                    # Custom attribute 05
            attr_list.append(AllplanBaseElements.AttributeString(1895, ""))                    # Custom attribute 06
            attr_list.append(AllplanBaseElements.AttributeString(1896, "40-40"))               # Custom attribute 07
            attr_list.append(AllplanBaseElements.AttributeString(1897, ""))                    # Custom attribute 08
            attr_list.append(AllplanBaseElements.AttributeString(1898, ""))                    # Custom attribute 09
            attr_list.append(AllplanBaseElements.AttributeString(1899, ""))                    # Custom attribute 10
            attr_list.append(AllplanBaseElements.AttributeString(1900, ""))                    # Custom attribute 11
            attr_list.append(AllplanBaseElements.AttributeString(1901, ""))                    # Custom attribute 12
            attr_list.append(AllplanBaseElements.AttributeString(1902, ""))                    # Custom attribute 13
            attr_list.append(AllplanBaseElements.AttributeString(1903, ""))                    # Custom attribute 14
            attr_list.append(AllplanBaseElements.AttributeString(1904, ""))                    # Custom attribute 15
            
            # Agregar atributos de usuario adicionales si hay documento disponible
            if self.doc:
                self._add_user_attributes_40mm(attr_list)
        elif tipo_val == 3:
            # Reducción 110-50 (DER. Y 110-50Ø 45°)
            attr_list.append(AllplanBaseElements.AttributeString(1083, "DER. Y 110-50Ø 45°")) # Custom attribute 01
            attr_list.append(AllplanBaseElements.AttributeString(1084, "Ø110-110-50mm"))      # Custom attribute 02
            attr_list.append(AllplanBaseElements.AttributeString(1085, ""))                    # Custom attribute 03
            attr_list.append(AllplanBaseElements.AttributeString(1086, ""))                    # Custom attribute 04
            attr_list.append(AllplanBaseElements.AttributeString(1087, ""))                    # Custom attribute 05
            attr_list.append(AllplanBaseElements.AttributeString(1895, "110-50"))              # Custom attribute 06
            attr_list.append(AllplanBaseElements.AttributeString(1896, ""))                    # Custom attribute 07
            attr_list.append(AllplanBaseElements.AttributeString(1897, ""))                    # Custom attribute 08
            attr_list.append(AllplanBaseElements.AttributeString(1898, ""))                    # Custom attribute 09
            attr_list.append(AllplanBaseElements.AttributeString(1899, ""))                    # Custom attribute 10
            attr_list.append(AllplanBaseElements.AttributeString(1900, ""))                    # Custom attribute 11
            attr_list.append(AllplanBaseElements.AttributeString(1901, ""))                    # Custom attribute 12
            attr_list.append(AllplanBaseElements.AttributeString(1902, ""))                    # Custom attribute 13
            attr_list.append(AllplanBaseElements.AttributeString(1903, ""))                    # Custom attribute 14
            attr_list.append(AllplanBaseElements.AttributeString(1904, ""))                    # Custom attribute 15
            
            # Agregar atributos de usuario adicionales si hay documento disponible
            if self.doc:
                self._add_user_attributes_110_50mm(attr_list)
        else:
            # Default case
            attr_list.append(AllplanBaseElements.AttributeString(1083, ""))
            attr_list.append(AllplanBaseElements.AttributeString(1084, ""))
            attr_list.append(AllplanBaseElements.AttributeString(1085, ""))
            attr_list.append(AllplanBaseElements.AttributeString(1086, ""))
            attr_list.append(AllplanBaseElements.AttributeString(1087, ""))
            attr_list.append(AllplanBaseElements.AttributeString(1895, ""))
            attr_list.append(AllplanBaseElements.AttributeString(1896, ""))
            attr_list.append(AllplanBaseElements.AttributeString(1897, ""))
            attr_list.append(AllplanBaseElements.AttributeString(1898, ""))
            attr_list.append(AllplanBaseElements.AttributeString(1899, ""))
            attr_list.append(AllplanBaseElements.AttributeString(1900, ""))
            attr_list.append(AllplanBaseElements.AttributeString(1901, ""))
            attr_list.append(AllplanBaseElements.AttributeString(1902, ""))
            attr_list.append(AllplanBaseElements.AttributeString(1903, ""))
            attr_list.append(AllplanBaseElements.AttributeString(1904, ""))

        attr_set = AllplanBaseElements.AttributeSet(attr_list)
        attributes = AllplanBaseElements.Attributes([attr_set])
        model_element.SetAttributes(attributes)

        return CreateElementResult([model_element])



    # ---------- Utilidades ----------
    def _attr_val(self, name: str, default: float) -> float:
        a = getattr(self.build_ele, name, None)
        if hasattr(a, 'value'):
            try:
                return float(a.value)
            except (TypeError, ValueError):
                return default
        return default

    def _attr_int(self, name: str, default: Optional[int]) -> Optional[int]:
        a = getattr(self.build_ele, name, None)
        if hasattr(a, 'value'):
            try:
                return int(a.value)
            except (TypeError, ValueError):
                return default
        return default

    def _props(self, color: int) -> Any:
        p = AllplanSettings.AllplanGlobalSettings.GetCurrentCommonProperties()
        p.Color = int(color)
        # hereda Pen/Stroke/Layer desde la paleta si existen
        for attr in ("Pen", "Stroke", "Layer"):
            v = getattr(self.build_ele, attr, None)
            if hasattr(v, 'value'):
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
        for angle, axis in zip([rx, ry, rz], ['x', 'y', 'z']):
            if abs(angle) > 1e-6:
                mat = AllplanGeo.Matrix3D()
                if axis == 'x':
                    axis_line = AllplanGeo.Line3D(0, 0, 0, 1, 0, 0)
                elif axis == 'y':
                    axis_line = AllplanGeo.Line3D(0, 0, 0, 0, 1, 0)
                else:
                    axis_line = AllplanGeo.Line3D(0, 0, 0, 0, 0, 1)
                mat.SetRotation(axis_line, AllplanGeo.Angle(math.radians(angle)))
                solid = AllplanGeo.Transform(solid, mat)
        return solid

    @staticmethod
    def _anillo_axis(base: float, diam_an: float, z_top: float, x_dir, z_dir):
        delta = (base - diam_an) / 2.0
        return AllplanGeo.AxisPlacement3D(AllplanGeo.Point3D(delta, delta, z_top), x_dir, z_dir)

    def _add_user_attributes_40mm(self, attr_list):
        """Agrega atributos de usuario para bifurcación de 40mm."""
        if not self.doc:
            return

        try:
            # Obtener IDs de atributos por nombre
            attr_6_cc_is_id = AllplanBaseElements.AttributeService.GetAttributeID(self.doc, "6_CC_IS")
            attr_pmp_carticulo_id = AllplanBaseElements.AttributeService.GetAttributeID(self.doc, "pmp_CARTICULO")
            attr_pmp_nom_id = AllplanBaseElements.AttributeService.GetAttributeID(self.doc, "pmp_nom")
            attr_pmp_pes_unitari_id = AllplanBaseElements.AttributeService.GetAttributeID(self.doc, "pmp_pes_unitari")
            attr_pmp_seccio_id = AllplanBaseElements.AttributeService.GetAttributeID(self.doc, "pmp_seccio")

            # 6_CC_IS: "IS"
            if attr_6_cc_is_id and attr_6_cc_is_id > 0:
                attr_list.append(AllplanBaseElements.AttributeString(attr_6_cc_is_id, ""))

            # pmp_CARTICULO: "KN07_008_001"
            if attr_pmp_carticulo_id and attr_pmp_carticulo_id > 0:
                attr_list.append(AllplanBaseElements.AttributeString(attr_pmp_carticulo_id, "KN07_008_001"))

            # pmp_nom: "DER. Y 40Ø 45°"
            if attr_pmp_nom_id and attr_pmp_nom_id > 0:
                attr_list.append(AllplanBaseElements.AttributeString(attr_pmp_nom_id, "DER. Y 40Ø 45°"))

            # pmp_pes_unitari: 0.0654 (AttributeDouble)
            if attr_pmp_pes_unitari_id and attr_pmp_pes_unitari_id > 0:
                attr_list.append(AllplanBaseElements.AttributeDouble(attr_pmp_pes_unitari_id, 0.0654))

            # pmp_seccio: 40 (AttributeInt o AttributeString según el tipo)
            if attr_pmp_seccio_id and attr_pmp_seccio_id > 0:
                try:
                    attr_list.append(AllplanBaseElements.AttributeInt(attr_pmp_seccio_id, 40))
                except:
                    attr_list.append(AllplanBaseElements.AttributeString(attr_pmp_seccio_id, "40"))

        except Exception as e:
            # No bloquear la creación si hay problemas con los atributos
            print(f"[DerivacioY_45_008] Advertencia al agregar atributos de usuario 40mm: {e}")

    def _add_user_attributes_110mm(self, attr_list):
        """Agrega atributos de usuario para bifurcación de 110mm."""
        if not self.doc:
            return

        try:
            # Obtener IDs de atributos por nombre
            attr_6_cc_is_id = AllplanBaseElements.AttributeService.GetAttributeID(self.doc, "6_CC_IS")
            attr_pmp_carticulo_id = AllplanBaseElements.AttributeService.GetAttributeID(self.doc, "pmp_CARTICULO")
            attr_pmp_nom_id = AllplanBaseElements.AttributeService.GetAttributeID(self.doc, "pmp_nom")
            attr_pmp_pes_unitari_id = AllplanBaseElements.AttributeService.GetAttributeID(self.doc, "pmp_pes_unitari")
            attr_pmp_seccio_id = AllplanBaseElements.AttributeService.GetAttributeID(self.doc, "pmp_seccio")

            # 6_CC_IS: "IS"
            if attr_6_cc_is_id and attr_6_cc_is_id > 0:
                attr_list.append(AllplanBaseElements.AttributeString(attr_6_cc_is_id, ""))

            # pmp_CARTICULO: "KN07_008_002"
            if attr_pmp_carticulo_id and attr_pmp_carticulo_id > 0:
                attr_list.append(AllplanBaseElements.AttributeString(attr_pmp_carticulo_id, "KN07_008_002"))

            # pmp_nom: "DER. Y 110Ø 45°"
            if attr_pmp_nom_id and attr_pmp_nom_id > 0:
                attr_list.append(AllplanBaseElements.AttributeString(attr_pmp_nom_id, "DER. Y 110Ø 45°"))

            # pmp_pes_unitari: 0.2509 (AttributeDouble)
            if attr_pmp_pes_unitari_id and attr_pmp_pes_unitari_id > 0:
                attr_list.append(AllplanBaseElements.AttributeDouble(attr_pmp_pes_unitari_id, 0.2509))

            # pmp_seccio: 110 (AttributeInt o AttributeString según el tipo)
            if attr_pmp_seccio_id and attr_pmp_seccio_id > 0:
                try:
                    attr_list.append(AllplanBaseElements.AttributeInt(attr_pmp_seccio_id, 110))
                except:
                    attr_list.append(AllplanBaseElements.AttributeString(attr_pmp_seccio_id, "110"))

        except Exception as e:
            # No bloquear la creación si hay problemas con los atributos
            print(f"[DerivacioY_45_008] Advertencia al agregar atributos de usuario 110mm: {e}")

    def _add_user_attributes_110_50mm(self, attr_list):
        """Agrega atributos de usuario para reducción 110-50mm."""
        if not self.doc:
            return

        try:
            # Obtener IDs de atributos por nombre
            attr_6_cc_is_id = AllplanBaseElements.AttributeService.GetAttributeID(self.doc, "6_CC_IS")
            attr_pmp_carticulo_id = AllplanBaseElements.AttributeService.GetAttributeID(self.doc, "pmp_CARTICULO")
            attr_pmp_nom_id = AllplanBaseElements.AttributeService.GetAttributeID(self.doc, "pmp_nom")
            attr_pmp_pes_unitari_id = AllplanBaseElements.AttributeService.GetAttributeID(self.doc, "pmp_pes_unitari")
            attr_pmp_seccio_id = AllplanBaseElements.AttributeService.GetAttributeID(self.doc, "pmp_seccio")

            # 6_CC_IS: "IS"
            if attr_6_cc_is_id and attr_6_cc_is_id > 0:
                attr_list.append(AllplanBaseElements.AttributeString(attr_6_cc_is_id, ""))

            # pmp_CARTICULO: "KN07_008_003"
            if attr_pmp_carticulo_id and attr_pmp_carticulo_id > 0:
                attr_list.append(AllplanBaseElements.AttributeString(attr_pmp_carticulo_id, "KN07_008_003"))

            # pmp_nom: "DER. Y 110-50Ø 45°"
            if attr_pmp_nom_id and attr_pmp_nom_id > 0:
                attr_list.append(AllplanBaseElements.AttributeString(attr_pmp_nom_id, "DER. Y 110-50Ø 45°"))

            # pmp_pes_unitari: 0.3426 (AttributeDouble)
            if attr_pmp_pes_unitari_id and attr_pmp_pes_unitari_id > 0:
                attr_list.append(AllplanBaseElements.AttributeDouble(attr_pmp_pes_unitari_id, 0.3426))

            # pmp_seccio: "Ø110-110-50mm" (AttributeString)
            if attr_pmp_seccio_id and attr_pmp_seccio_id > 0:
                attr_list.append(AllplanBaseElements.AttributeString(attr_pmp_seccio_id, "Ø110-110-50mm"))

        except Exception as e:
            # No bloquear la creación si hay problemas con los atributos
            print(f"[DerivacioY_45_008] Advertencia al agregar atributos de usuario 110-50mm: {e}")


# ===== Punto de entrada PythonPart =====
def create_element(build_ele: BuildingElement, _doc: Any) -> CreateElementResult:
    """Instancia la clase y delega la creación del elemento."""
    return BifurcacionDerivacion45(build_ele, _doc).create_result()
