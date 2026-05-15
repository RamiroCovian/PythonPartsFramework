# -*- coding: utf-8 -*-
"""Conjuntos de reducción """

import math
from typing import Optional, List, Dict, Any

import NemAll_Python_Geometry as AllplanGeo
import NemAll_Python_BasisElements as AllplanBasisElements
import NemAll_Python_AllplanSettings as AllplanSettings
import NemAll_Python_BaseElements as AllplanBaseElements
from CreateElementResult import CreateElementResult


# ===== Requisito estándar =====
def check_allplan_version(_build_ele, _version) -> bool:
    """Se soportan todas las versiones."""
    return True
# ==============================


class ConjuntosReduccion:
    """Implementación OO de 'conjuntos de reducción'.

    - TipoTubo = 0: Bifurcación doble rama 110-50 (DER. Y 110-50 45°).
    - TipoTubo = 2: Figura reductora (trapecio + añadidos).
    - Otros valores: no crea elementos.
    """

    # Rotaciones hardcodeadas para BIFURCACION_DOBLE_RAMA_110_50 (TipoTubo = 0), en grados.
    ROT_X_TIPO0: float = 90.0
    ROT_Y_TIPO0: float = 180.0
    ROT_Z_TIPO0: float = 0.0

    # Rotaciones hardcodeadas para el objeto 2 (TipoTubo = 2), en grados.
    ROT_X_TIPO2: float = 180.0
    ROT_Y_TIPO2: float = 0.0
    ROT_Z_TIPO2: float = 90.0

    # Diámetro hardcodeado para la rama 3
    DIAMETRO_RAMA3: float = 40.0  # Cambia este valor según lo que necesites

    # Diámetro específico para el anillo rama 3 (independiente de DIAMETRO_RAMA3)
    DIAMETRO_ANILLO_RAMA3: float = 30.0  # Diámetro del anillo rama 3 (sin sobresaliente)

    # Offsets hardcodeados para mover el anillo rama 2
    OFFSET_ANILLO_RAMA2_X: float = -15.0   # Offset en X (positivo = hacia la derecha)
    OFFSET_ANILLO_RAMA2_Y: float = -10.0   # Offset en Y (positivo = hacia adelante)
    OFFSET_ANILLO_RAMA2_Z: float = 0.0   # Offset en Z (positivo = hacia arriba)

    # Offsets hardcodeados para mover el anillo rama 3
    OFFSET_ANILLO_RAMA3_X: float = 10.0   # Offset en X (positivo = hacia la derecha)
    OFFSET_ANILLO_RAMA3_Y: float = 0.0   # Offset en Y (positivo = hacia adelante)
    OFFSET_ANILLO_RAMA3_Z: float = 0.0   # Offset en Z (positivo = hacia arriba)

    # Largo hardcodeado para el anillo rama 3
    LARGO_ANILLO_RAMA3: float = 70.0      # Largo del anillo rama 3 (independiente del rama 2)

    # Offsets hardcodeados para mover todo el conjunto de ramas (objeto 2)
    OFFSET_RAMAS_X: float = 40.0   # Offset en X (positivo = hacia la derecha)
    OFFSET_RAMAS_Y: float = 0.0   # Offset en Y (positivo = hacia adelante)
    OFFSET_RAMAS_Z: float = 0.0   # Offset en Z (positivo = hacia arriba)

    # Offsets hardcodeados para mover los cuboides al final del anillo
    OFFSET_CUBOIDES_X: float = 26.0   # Offset en X para los cuboides (positivo = hacia la derecha)
    OFFSET_CUBOIDES_Y: float = 20.0   # Offset en Y para los cuboides (positivo = hacia adelante)
    OFFSET_CUBOIDES_Z: float = -23.0   # Offset en Z para los cuboides (positivo = hacia arriba)

    # Rotaciones hardcodeadas para los cuboides al final del anillo
    ROT_CUBOIDES_X: float = 90.0   # Rotación en X (grados)
    ROT_CUBOIDES_Y: float = 180.0  # Rotación en Y (grados)
    ROT_CUBOIDES_Z: float = 0.0    # Rotación en Z (grados)

    # Offsets para mover el cuboide pequeño (cuboide_40)
    OFFSET_CUBOIDE_PEQUENO_X: float = 5.0   # Offset en X para el cuboide pequeño
    OFFSET_CUBOIDE_PEQUENO_Y: float = 5.0   # Offset en Y para el cuboide pequeño
    OFFSET_CUBOIDE_PEQUENO_Z: float = 0.0   # Offset en Z para el cuboide pequeño

    # Dimensiones del bloque adicional (cubo trunc)
    ADD_X: float = 50.0  # Ancho del cubo truncado
    ADD_Y: float = 37.5  # Alto del cubo truncado
    ADD_Z: float = 60.0  # Profundidad del cubo truncado

    # Dimensiones del anillo
    ANILLO_LARGO: float = 10.0      # Largo del anillo
    SOBRESALE_ANILLO: float = 5.0   # Sobresaliente del anillo
    LAYER = 40148  # IS_CON_SANE_FAB (is cone fab)
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

    # ---------- API ----------
    def create_result(self) -> CreateElementResult:
        tipo_val = self._get_build_ele_value('TipoTubo')

        if tipo_val == 0:
            elems = self._build_bifurcacion_doble(self.params)
        elif tipo_val == 2:
            elems = self._build_figura_reductora(self.params)
        else:
            elems = []

        return CreateElementResult(elems)

    # ---------- Utilidades ----------
    def _get_build_ele_value(self, attr: str) -> Optional[Any]:
        val = getattr(self.build_ele, attr, None)
        if hasattr(val, 'value'):
            try:
                return int(val.value)
            except Exception:
                return None
        return None

    def _props(self, color: int, pen: int = 1, stroke: int = 1, layer: int = None):
        if layer is None:
            layer = self.LAYER
        p = AllplanSettings.AllplanGlobalSettings.GetCurrentCommonProperties()
        p.Color = color
        p.ColorByLayer = False  # No afectar el color
        p.Pen = pen
        p.Stroke = stroke
        p.Layer = layer
        return p

    @staticmethod
    def _create_trapezoidal_prism(base1, base2, height, length):
        y0, y1 = 0.0, height
        x0 = (base2 - base1) / 2.0
        x1 = x0 + base1
        poly = AllplanGeo.Polygon3D([
            AllplanGeo.Point3D(x0, y0, 0.0),
            AllplanGeo.Point3D(x1, y0, 0.0),
            AllplanGeo.Point3D(base2, y1, 0.0),
            AllplanGeo.Point3D(0.0, y1, 0.0),
            AllplanGeo.Point3D(x0, y0, 0.0)
        ])
        path = AllplanGeo.Polyline3D()
        path += AllplanGeo.Point3D(0.0, 0.0, 0.0)
        path += AllplanGeo.Point3D(0.0, 0.0, length)
        err, solid = AllplanGeo.CreatePolyhedron(poly, path)
        return solid if err == 0 and solid and solid.IsValid() else None

    @staticmethod
    def _rotate_vec_around_x(vec: AllplanGeo.Vector3D, angle_rad: float) -> AllplanGeo.Vector3D:
        y_new = vec.Y * math.cos(angle_rad) - vec.Z * math.sin(angle_rad)
        z_new = vec.Y * math.sin(angle_rad) + vec.Z * math.cos(angle_rad)
        return AllplanGeo.Vector3D(vec.X, y_new, z_new)

    @staticmethod
    def _make_union(*solids):
        """Realiza la unión secuencial de sólidos, retorna el último válido."""
        if not solids:
            return None
        result = solids[0]
        for s in solids[1:]:
            err, result2 = AllplanGeo.MakeUnion(result, s)
            if err == 0 and result2 and result2.IsValid():
                result = result2
        return result

    @staticmethod
    def _apply_rotations(solid, cx, cy, cz, rx=0.0, ry=0.0, rz=0.0):
        """Aplica rotaciones en X, Y, Z (en grados) alrededor del punto (cx,cy,cz)."""
        for angle, axis in zip([rx, ry, rz], ['x', 'y', 'z']):
            if abs(angle) > 1e-6:
                mat = AllplanGeo.Matrix3D()
                if axis == 'x':
                    axis_line = AllplanGeo.Line3D(cx, cy, cz, cx + 1.0, cy, cz)
                elif axis == 'y':
                    axis_line = AllplanGeo.Line3D(cx, cy, cz, cx, cy + 1.0, cz)
                else:
                    axis_line = AllplanGeo.Line3D(cx, cy, cz, cx, cy, cz + 1.0)
                mat.SetRotation(axis_line, AllplanGeo.Angle(math.radians(angle)))
                solid = AllplanGeo.Transform(solid, mat)
        return solid

    def _add_user_attributes_bifurcacion_doble(self, attr_list):
        """Agrega atributos de usuario para bifurcación doble rama 110-50."""
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

            # pmp_nom: "DER. Y 110-50 45°"
            if attr_pmp_nom_id and attr_pmp_nom_id > 0:
                attr_list.append(AllplanBaseElements.AttributeString(attr_pmp_nom_id, "DER. Y 110-50 45°"))

            # pmp_pes_unitari: 0.3426 (AttributeDouble)
            if attr_pmp_pes_unitari_id and attr_pmp_pes_unitari_id > 0:
                attr_list.append(AllplanBaseElements.AttributeDouble(attr_pmp_pes_unitari_id, 0.3426))

            # pmp_seccio: "Ø110-110-50mm" (AttributeString)
            if attr_pmp_seccio_id and attr_pmp_seccio_id > 0:
                attr_list.append(AllplanBaseElements.AttributeString(attr_pmp_seccio_id, "Ø110-110-50mm"))

        except Exception as e:
            # No bloquear la creación si hay problemas con los atributos
            print(f"[Conjuntsreduction_006] Advertencia al agregar atributos de usuario bifurcación doble: {e}")

    def _add_user_attributes_reducer_rigid_50_40(self, attr_list):
        """Agrega atributos de usuario para reductor rígido 50-40."""
        if not self.doc:
            return
        try:
            attr_6_cc_is_id = AllplanBaseElements.AttributeService.GetAttributeID(self.doc, "6_CC_IS")
            attr_pmp_carticulo_id = AllplanBaseElements.AttributeService.GetAttributeID(self.doc, "pmp_CARTICULO")
            attr_pmp_nom_id = AllplanBaseElements.AttributeService.GetAttributeID(self.doc, "pmp_nom")
            attr_pmp_pes_unitari_id = AllplanBaseElements.AttributeService.GetAttributeID(self.doc, "pmp_pes_unitari")
            attr_pmp_seccio_id = AllplanBaseElements.AttributeService.GetAttributeID(self.doc, "pmp_seccio")

            if attr_6_cc_is_id and attr_6_cc_is_id > 0:
                attr_list.append(AllplanBaseElements.AttributeString(attr_6_cc_is_id, "IS"))
            if attr_pmp_carticulo_id and attr_pmp_carticulo_id > 0:
                attr_list.append(AllplanBaseElements.AttributeString(attr_pmp_carticulo_id, "KN07_007_001"))
            if attr_pmp_nom_id and attr_pmp_nom_id > 0:
                attr_list.append(AllplanBaseElements.AttributeString(attr_pmp_nom_id, "RED. M-F 50-40Ø"))
            if attr_pmp_pes_unitari_id and attr_pmp_pes_unitari_id > 0:
                attr_list.append(AllplanBaseElements.AttributeDouble(attr_pmp_pes_unitari_id, 0.0319))
            if attr_pmp_seccio_id and attr_pmp_seccio_id > 0:
                attr_list.append(AllplanBaseElements.AttributeString(attr_pmp_seccio_id, "Ø40-50mm"))
        except Exception as e:
            print(f"[Conjuntsreduction_006] Advertencia al agregar atributos de usuario reductor 50-40: {e}")

    def _add_user_attributes_reducer_rigid_110_50(self, attr_list):
        """Agrega atributos de usuario para reductor rígido 110-50."""
        if not self.doc:
            return
        try:
            attr_6_cc_is_id = AllplanBaseElements.AttributeService.GetAttributeID(self.doc, "6_CC_IS")
            attr_pmp_carticulo_id = AllplanBaseElements.AttributeService.GetAttributeID(self.doc, "pmp_CARTICULO")
            attr_pmp_nom_id = AllplanBaseElements.AttributeService.GetAttributeID(self.doc, "pmp_nom")
            attr_pmp_pes_unitari_id = AllplanBaseElements.AttributeService.GetAttributeID(self.doc, "pmp_pes_unitari")
            attr_pmp_seccio_id = AllplanBaseElements.AttributeService.GetAttributeID(self.doc, "pmp_seccio")

            if attr_6_cc_is_id and attr_6_cc_is_id > 0:
                attr_list.append(AllplanBaseElements.AttributeString(attr_6_cc_is_id, "IS"))
            if attr_pmp_carticulo_id and attr_pmp_carticulo_id > 0:
                attr_list.append(AllplanBaseElements.AttributeString(attr_pmp_carticulo_id, "KN07_007_002"))
            if attr_pmp_nom_id and attr_pmp_nom_id > 0:
                attr_list.append(AllplanBaseElements.AttributeString(attr_pmp_nom_id, "RED. M-F 110-50Ø"))
            if attr_pmp_pes_unitari_id and attr_pmp_pes_unitari_id > 0:
                attr_list.append(AllplanBaseElements.AttributeDouble(attr_pmp_pes_unitari_id, 0.1119))
            if attr_pmp_seccio_id and attr_pmp_seccio_id > 0:
                attr_list.append(AllplanBaseElements.AttributeString(attr_pmp_seccio_id, "110-50"))
        except Exception as e:
            print(f"[Conjuntsreduction_006] Advertencia al agregar atributos de usuario reductor 110-50: {e}")

    # ---------- Tipo 0: Bifurcación fija con doble rama (DER. Y 110-50 45°) ----------
    def _build_bifurcacion_doble(self, params: Dict[str, float]) -> List[Any]:
        p = params
        props = self._props(color=p['COLOR'])

        x_dir = AllplanGeo.Vector3D(1, 0, 0)
        z_dir = AllplanGeo.Vector3D(0, 0, 1)
        ang_rad = math.radians(p['ANGULO'])

        base, base_rama = p['DIAMETRO'], p['DIAMETRO_RAMA']
        diam_anillo = base + 2 * p['SOBRESALE_ANILLO']
        diam_anillo_rama = base_rama + 2 * p['SOBRESALE_ANILLO']

        # Cuerpo principal (entre anillos)
        altura_cuerpo = p['LARGO_PRINCIPAL'] - 2 * p['LARGO_ANILLO']
        axis_main = AllplanGeo.AxisPlacement3D(AllplanGeo.Point3D(0, 0, p['LARGO_ANILLO']), x_dir, z_dir)
        cuerpo = AllplanGeo.BRep3D.CreateCuboid(axis_main, base, base, altura_cuerpo)

        # Anillo superior
        offset_xy = (diam_anillo - base) / 2.0
        anillo_sup = AllplanGeo.BRep3D.CreateCuboid(
            AllplanGeo.AxisPlacement3D(
                AllplanGeo.Point3D(-offset_xy, -offset_xy, p['LARGO_ANILLO'] + altura_cuerpo),
                x_dir, z_dir
            ),
            diam_anillo, diam_anillo, p['LARGO_ANILLO']
        )

        # Rama 1
        z_dir_rama = AllplanGeo.Vector3D(0, -math.sin(ang_rad), math.cos(ang_rad))
        z_top_tubo = p['LARGO_ANILLO'] + altura_cuerpo
        if z_dir_rama.Z >= 0:
            p_rama_z = z_top_tubo - p['CLEARANCE_RAMA'] - p['LARGO_RAMA'] * z_dir_rama.Z
        else:
            p_rama_z = z_top_tubo - p['CLEARANCE_RAMA']
        p_rama = AllplanGeo.Point3D(0, 0, p_rama_z)
        axis_rama = AllplanGeo.AxisPlacement3D(p_rama, x_dir, z_dir_rama)
        rama = AllplanGeo.BRep3D.CreateCuboid(axis_rama, base_rama, base_rama, p['LARGO_RAMA'])

        # Fin rama 1
        p_rama_fin = AllplanGeo.Point3D(
            p_rama.X + p['LARGO_RAMA'] * z_dir_rama.X,
            p_rama.Y + p['LARGO_RAMA'] * z_dir_rama.Y,
            p_rama.Z + p['LARGO_RAMA'] * z_dir_rama.Z
        )

        # Rama 2 (rotación relativa alrededor de X)
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

        # Anillo rama 2
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

        # Rama 3 (colineal con rama2)
        OVERLAP3 = 2.0
        p_rama3 = AllplanGeo.Point3D(
            p_rama2_fin.X - OVERLAP3 * z_dir_rama2.X,
            p_rama2_fin.Y - OVERLAP3 * z_dir_rama2.Y,
            p_rama2_fin.Z - OVERLAP3 * z_dir_rama2.Z
        )
        axis_rama3 = AllplanGeo.AxisPlacement3D(p_rama3, x_dir, z_dir_rama2)
        rama3 = AllplanGeo.BRep3D.CreateCuboid(axis_rama3, self.DIAMETRO_RAMA3, self.DIAMETRO_RAMA3, p['LARGO_RAMA3'])

        # Anillo rama 3 (copia del anillo rama 2 en el mismo lugar + offsets)
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

        # Crear objetos temporalmente separados para poder mover las ramas
        # Objeto 1: Cuerpo principal + Anillo superior
        brep_cuerpo = self._make_union(cuerpo, anillo_sup)
        
        # Objeto 2: Todas las ramas unidas (Rama 1 + Rama 2 + Anillo Rama 2 + Rama 3 + Anillo Rama 3)
        brep_ramas = self._make_union(rama, rama2, anillo_rama2, rama3, anillo_rama3)
        
        # Aplicar offsets para mover todo el conjunto de ramas
        if self.OFFSET_RAMAS_X != 0.0 or self.OFFSET_RAMAS_Y != 0.0 or self.OFFSET_RAMAS_Z != 0.0:
            brep_ramas = AllplanGeo.Move(
                brep_ramas,
                AllplanGeo.Vector3D(self.OFFSET_RAMAS_X, self.OFFSET_RAMAS_Y, self.OFFSET_RAMAS_Z)
            )

        # Rotación hardcodeada alrededor del propio eje (centro aproximado del cuerpo principal)
        cx = base * 0.5
        cy = base * 0.5
        cz = p['LARGO_ANILLO'] + altura_cuerpo * 0.5
        
        # Aplicar rotaciones al objeto 1 (cuerpo + anillo superior)
        brep_cuerpo = self._apply_rotations(
            brep_cuerpo,
            cx, cy, cz,
            rx=self.ROT_X_TIPO0,
            ry=self.ROT_Y_TIPO0,
            rz=self.ROT_Z_TIPO0
        )
        brep_cuerpo = AllplanGeo.Rotate(
            brep_cuerpo,
            AllplanGeo.Axis3D(AllplanGeo.Point3D(0, 0, 0), AllplanGeo.Vector3D(0, 1, 0)),
            AllplanGeo.Angle(math.radians(90))
        )
        
        # Aplicar rotaciones al objeto 2 (ramas)
        brep_ramas = self._apply_rotations(
            brep_ramas,
            cx, cy, cz,
            rx=self.ROT_X_TIPO0,
            ry=self.ROT_Y_TIPO0,
            rz=self.ROT_Z_TIPO0
        )
        brep_ramas = AllplanGeo.Rotate(
            brep_ramas,
            AllplanGeo.Axis3D(AllplanGeo.Point3D(0, 0, 0), AllplanGeo.Vector3D(0, 1, 0)),
            AllplanGeo.Angle(math.radians(90))
        )

        # Unir ambos objetos en uno solo (después de aplicar offsets y rotaciones)
        brep_final = self._make_union(brep_cuerpo, brep_ramas)

        # Crear ModelElement3D unificado
        model_element = AllplanBasisElements.ModelElement3D(props, brep_final)
        
        # Agregar atributos custom y de usuario
        attr_list = []
        
        # Custom attributes (hardcoded IDs)
        attr_list.append(AllplanBaseElements.AttributeString(1083, "RED. M-F 110-50Ø"))  # Custom attribute 01
        attr_list.append(AllplanBaseElements.AttributeString(1084, "Ø110-50"))           # Custom attribute 02
        attr_list.append(AllplanBaseElements.AttributeString(1085, ""))                 # Custom attribute 03
        attr_list.append(AllplanBaseElements.AttributeString(1086, ""))                 # Custom attribute 04
        attr_list.append(AllplanBaseElements.AttributeString(1087, ""))                 # Custom attribute 05
        attr_list.append(AllplanBaseElements.AttributeString(1895, ""))                 # Custom attribute 06
        attr_list.append(AllplanBaseElements.AttributeString(1896, "110-50"))            # Custom attribute 07
        attr_list.append(AllplanBaseElements.AttributeString(1897, ""))                 # Custom attribute 08
        attr_list.append(AllplanBaseElements.AttributeString(1898, ""))                 # Custom attribute 09
        attr_list.append(AllplanBaseElements.AttributeString(1899, ""))                 # Custom attribute 10
        attr_list.append(AllplanBaseElements.AttributeString(1900, ""))                 # Custom attribute 11
        attr_list.append(AllplanBaseElements.AttributeString(1901, ""))                 # Custom attribute 12
        attr_list.append(AllplanBaseElements.AttributeString(1902, ""))                 # Custom attribute 13
        attr_list.append(AllplanBaseElements.AttributeString(1903, ""))                 # Custom attribute 14
        attr_list.append(AllplanBaseElements.AttributeString(1904, ""))                 # Custom attribute 15
        
        # Agregar atributos de usuario si hay documento disponible
        if self.doc:
            self._add_user_attributes_bifurcacion_doble(attr_list)
        
        if attr_list:
            attr_set = AllplanBaseElements.AttributeSet(attr_list)
            attributes = AllplanBaseElements.Attributes([attr_set])
            model_element.SetAttributes(attributes)

        return [model_element]

    # ---------- Tipo 2: Figura reductora ----------
    def _build_figura_reductora(self, _params: Dict[str, float]) -> List[Any]:
        props = self._props(color=70)

        # Cuboide base (polyhedron extruido 110 en Z)
        cara_inf = AllplanGeo.Polygon3D([
            AllplanGeo.Point3D(0, 0, 0),
            AllplanGeo.Point3D(110.0, 0, 0),
            AllplanGeo.Point3D(110.0, 60.0, 0),
            AllplanGeo.Point3D(0, 60.0, 0),
            AllplanGeo.Point3D(0, 0, 0)
        ])
        path_cuboide = AllplanGeo.Polyline3D()
        path_cuboide += AllplanGeo.Point3D(0, 0, 0)
        path_cuboide += AllplanGeo.Point3D(0, 0, 110.0)
        err, cuboide = AllplanGeo.CreatePolyhedron(cara_inf, path_cuboide)
        if err != 0 or cuboide is None or not cuboide.IsValid():
            return []

        # Trapecio extruido
        base_mayor, alto_trap, ANGULO_CARAS_DEG = 110.0, 50.0, 33.0
        base_menor = max(1.0, base_mayor - 2.0 * alto_trap * math.tan(math.radians(ANGULO_CARAS_DEG)))
        salida_sur, EPS_UNION = 60.0, 0.1
        ROT_X_DEG, ROT_Y_DEG, ROT_Z_DEG = 0.0, 90.0, 0.0
        OFFSET_X, OFFSET_Z = -25.0, 0.0

        trap = self._create_trapezoidal_prism(base1=base_menor, base2=base_mayor, height=alto_trap, length=salida_sur)
        if trap is None:
            return [AllplanBasisElements.ModelElement3D(props, cuboide)]

        dx = (110.0 - base_mayor) * 0.5
        dy = -alto_trap + EPS_UNION
        dz = (110.0 - salida_sur) * 0.5

        trap = AllplanGeo.Move(trap, AllplanGeo.Vector3D(dx + OFFSET_X, dy, dz + OFFSET_Z))
        cx = dx + OFFSET_X + base_mayor * 0.5
        cy = dy + alto_trap * 0.5
        cz = dz + OFFSET_Z + salida_sur * 0.5
        trap = self._apply_rotations(trap, cx, cy, cz, ROT_X_DEG, ROT_Y_DEG, ROT_Z_DEG)

        final_body = self._make_union(cuboide, trap)

        # Bloque adicional (cubo trunc + anillo)
        # Dimensiones tomadas de constantes de clase
        x_center = dx + OFFSET_X + base_mayor * 0.5
        z_center = dz + OFFSET_Z + salida_sur * 0.5
        y_top = dy

        add_min = AllplanGeo.Point3D(x_center - self.ADD_X * 0.5, y_top - self.ADD_Y, z_center - self.ADD_Z * 0.5)
        add_max = AllplanGeo.Point3D(x_center + self.ADD_X * 0.5, y_top,            z_center + self.ADD_Z * 0.5)
        cubo_trunc = AllplanGeo.Polyhedron3D.CreateCuboid(add_min, add_max)
        final_body = self._make_union(final_body, cubo_trunc)

        y_end_cubo = y_top - self.ADD_Y
        ring_min = AllplanGeo.Point3D(
            x_center - (self.ADD_X * 0.5 + self.SOBRESALE_ANILLO),
            y_end_cubo - self.ANILLO_LARGO,
            z_center - (self.ADD_Z * 0.5 + self.SOBRESALE_ANILLO)
        )
        ring_max = AllplanGeo.Point3D(
            x_center + (self.ADD_X * 0.5 + self.SOBRESALE_ANILLO),
            y_end_cubo,
            z_center + (self.ADD_Z * 0.5 + self.SOBRESALE_ANILLO)
        )
        anillo = AllplanGeo.Polyhedron3D.CreateCuboid(ring_min, ring_max)
        final_body = self._make_union(final_body, anillo)

        # Dos cuboides al final del anillo, unidos y rotados
        cub1_largo, cub1_ancho, cub1_alto = 60.0, 50.0, 50.0
        cub2_largo, cub2_ancho, cub2_alto = 45.0, 40.0, 40.0

        y_base = y_end_cubo - self.ANILLO_LARGO - cub1_alto
        x_base = x_center - cub1_ancho * 0.5
        z_base = z_center - cub1_largo * 0.5

        # Aplicar offsets para mover los cuboides
        x_base += self.OFFSET_CUBOIDES_X
        y_base += self.OFFSET_CUBOIDES_Y
        z_base += self.OFFSET_CUBOIDES_Z

        min1 = AllplanGeo.Point3D(x_base, y_base, z_base)
        max1 = AllplanGeo.Point3D(x_base + cub1_ancho, y_base + cub1_alto, z_base + cub1_largo)
        cuboide_50 = AllplanGeo.Polyhedron3D.CreateCuboid(min1, max1)

        # Posición del cuboide pequeño con offsets
        min2_x = x_base + self.OFFSET_CUBOIDE_PEQUENO_X
        min2_y = y_base + self.OFFSET_CUBOIDE_PEQUENO_Y
        min2_z = z_base + cub1_largo + self.OFFSET_CUBOIDE_PEQUENO_Z
        min2 = AllplanGeo.Point3D(min2_x, min2_y, min2_z)
        max2 = AllplanGeo.Point3D(min2_x + cub2_ancho, min2_y + cub2_alto, min2_z + cub2_largo)
        cuboide_40 = AllplanGeo.Polyhedron3D.CreateCuboid(min2, max2)

        solido_cub = self._make_union(cuboide_50, cuboide_40)

        rot_x_deg, rot_y_deg, rot_z_deg = self.ROT_CUBOIDES_X, self.ROT_CUBOIDES_Y, self.ROT_CUBOIDES_Z
        cx2 = x_base + cub1_ancho * 0.5
        cy2 = y_base + cub1_alto * 0.5
        cz2 = z_base + (cub1_largo + cub2_largo) * 0.5
        solido_cub = self._apply_rotations(solido_cub, cx2, cy2, cz2, rot_x_deg, rot_y_deg, rot_z_deg)

        # Prisma triangular añadido
        SIZE = 50.0
        ROT_X_TRI_DEG, ROT_Y_TRI_DEG, ROT_Z_TRI_DEG = 180.0, 0.0, 0.0
        OFFSET_TRI_X, OFFSET_TRI_Y, OFFSET_TRI_Z = -25.0, 17.0, 0.0

        p0t = AllplanGeo.Point3D(0.0, 0.0, 0.0)
        p1t = AllplanGeo.Point3D(SIZE, 0.0, 0.0)
        p2t = AllplanGeo.Point3D(0.0, SIZE, 0.0)
        base_face = AllplanGeo.Polygon3D([p0t, p1t, p2t, p0t])

        path = AllplanGeo.Polyline3D()
        path += AllplanGeo.Point3D(0.0, 0.0, 0.0)
        path += AllplanGeo.Point3D(0.0, 0.0, SIZE)

        err_tri, prisma_tri = AllplanGeo.CreatePolyhedron(base_face, path)
        if err_tri == 0 and prisma_tri and prisma_tri.IsValid():
            cx3 = SIZE / 3.0
            cy3 = SIZE / 3.0
            cz3 = SIZE / 2.0
            prisma_tri = self._apply_rotations(prisma_tri, cx3, cy3, cz3, ROT_X_TRI_DEG, ROT_Y_TRI_DEG, ROT_Z_TRI_DEG)

            dx = (110.0 - base_mayor) * 0.5  # reutilizo base_mayor local
            x_right = dx + OFFSET_X + base_mayor + OFFSET_TRI_X
            y_b = dy + OFFSET_TRI_Y
            z_b = z_center - SIZE * 0.5 + OFFSET_TRI_Z

            prisma_tri = AllplanGeo.Move(prisma_tri, AllplanGeo.Vector3D(x_right, y_b, z_b))
            final_body = self._make_union(final_body, prisma_tri)

        # Rotación del objeto completo
        rot_obj_x_deg, rot_obj_y_deg, rot_obj_z_deg = 180.0, 180.0, 0.0
        cx_obj = x_center
        cy_obj = y_top - self.ADD_Y * 0.5
        cz_obj = z_center

        obj = self._apply_rotations(final_body, cx_obj, cy_obj, cz_obj, rot_obj_x_deg, rot_obj_y_deg, rot_obj_z_deg)

        # Aplicar rotaciones adicionales hardcodeadas para Tipo 2 (sobre su propio eje)
        # Estas rotaciones se aplican alrededor del centro del objeto después de las rotaciones base
        obj = self._apply_rotations(
            obj,
            cx_obj, cy_obj, cz_obj,
            rx=self.ROT_X_TIPO2,
            ry=self.ROT_Y_TIPO2,
            rz=self.ROT_Z_TIPO2
        )

        # Mantener los cuboides finales como entidad independiente del reductor principal.
        obj_cuboides = self._apply_rotations(
            solido_cub,
            cx_obj, cy_obj, cz_obj,
            rot_obj_x_deg, rot_obj_y_deg, rot_obj_z_deg
        )
        obj_cuboides = self._apply_rotations(
            obj_cuboides,
            cx_obj, cy_obj, cz_obj,
            rx=self.ROT_X_TIPO2,
            ry=self.ROT_Y_TIPO2,
            rz=self.ROT_Z_TIPO2
        )

        model_reductor = AllplanBasisElements.ModelElement3D(props, obj)
        model_cuboides = AllplanBasisElements.ModelElement3D(props, obj_cuboides)

        # Atributos para la figura principal (reductor 110-50).
        red_attr_list = [
            AllplanBaseElements.AttributeString(1083, "RED. M-F 110-50Ø"),  # Custom attribute 01
            AllplanBaseElements.AttributeString(1084, "Ø110-50"),           # Custom attribute 02
            AllplanBaseElements.AttributeString(1085, ""),                  # Custom attribute 03
            AllplanBaseElements.AttributeString(1086, ""),                  # Custom attribute 04
            AllplanBaseElements.AttributeString(1087, ""),                  # Custom attribute 05
            AllplanBaseElements.AttributeString(1895, ""),                  # Custom attribute 06
            AllplanBaseElements.AttributeString(1896, "110-50"),            # Custom attribute 07
            AllplanBaseElements.AttributeString(1897, ""),                  # Custom attribute 08
            AllplanBaseElements.AttributeString(1898, ""),                  # Custom attribute 09
            AllplanBaseElements.AttributeString(1899, ""),                  # Custom attribute 10
            AllplanBaseElements.AttributeString(1900, ""),                  # Custom attribute 11
            AllplanBaseElements.AttributeString(1901, ""),                  # Custom attribute 12
            AllplanBaseElements.AttributeString(1902, ""),                  # Custom attribute 13
            AllplanBaseElements.AttributeString(1903, ""),                  # Custom attribute 14
            AllplanBaseElements.AttributeString(1904, ""),                  # Custom attribute 15
        ]
        if self.doc:
            self._add_user_attributes_reducer_rigid_110_50(red_attr_list)
        red_attr_set = AllplanBaseElements.AttributeSet(red_attr_list)
        red_attributes = AllplanBaseElements.Attributes([red_attr_set])
        model_reductor.SetAttributes(red_attributes)

        # Atributos Custom para la entidad independiente de cuboides (reductor 50-40).
        cub_attr_list = [
            AllplanBaseElements.AttributeString(1083, "RED. M-F 50-40Ø"),  # Custom attribute 01
            AllplanBaseElements.AttributeString(1084, "Ø40-50"),           # Custom attribute 02
            AllplanBaseElements.AttributeString(1085, ""),                 # Custom attribute 03
            AllplanBaseElements.AttributeString(1086, ""),                 # Custom attribute 04
            AllplanBaseElements.AttributeString(1087, ""),                 # Custom attribute 05
            AllplanBaseElements.AttributeString(1895, ""),                 # Custom attribute 06
            AllplanBaseElements.AttributeString(1896, "40-50"),            # Custom attribute 07
            AllplanBaseElements.AttributeString(1897, ""),                 # Custom attribute 08
            AllplanBaseElements.AttributeString(1898, ""),                 # Custom attribute 09
            AllplanBaseElements.AttributeString(1899, ""),                 # Custom attribute 10
            AllplanBaseElements.AttributeString(1900, ""),                 # Custom attribute 11
            AllplanBaseElements.AttributeString(1901, ""),                 # Custom attribute 12
            AllplanBaseElements.AttributeString(1902, ""),                 # Custom attribute 13
            AllplanBaseElements.AttributeString(1903, ""),                 # Custom attribute 14
            AllplanBaseElements.AttributeString(1904, ""),                 # Custom attribute 15
        ]
        # Agregar atributos de usuario solicitados para el reductor 50-40.
        if self.doc:
            self._add_user_attributes_reducer_rigid_50_40(cub_attr_list)
        cub_attr_set = AllplanBaseElements.AttributeSet(cub_attr_list)
        cub_attributes = AllplanBaseElements.Attributes([cub_attr_set])
        model_cuboides.SetAttributes(cub_attributes)

        return [model_reductor, model_cuboides]


# ===== Punto de entrada PythonPart =====
def create_element(build_ele, _doc) -> CreateElementResult:
    """Instancia la clase y delega la creación de los elementos."""
    return ConjuntosReduccion(build_ele, _doc).create_result()
