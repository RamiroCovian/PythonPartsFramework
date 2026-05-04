# -*- coding: utf-8 -*-
"""Codo Rígido / Saneamiento """

import math
import NemAll_Python_Geometry as AllplanGeo
import NemAll_Python_BasisElements as AllplanBasisElements
import NemAll_Python_AllplanSettings as AllplanSettings
import NemAll_Python_BaseElements as AllplanBaseElements
from CreateElementResult import CreateElementResult


# ===== Requisito estándar =====
def check_allplan_version(_build_ele, _version) -> bool:
    """Check the current Allplan version (se soportan todas las versiones)."""
    return True
# ==============================


class CodoRigido:
    """Implementa las 6 variantes de codo (110/40 · 45°/87°) más el default."""

    LAYER = 40148  # IS_CON_SANE_FAB (is cone fab)

    # ===== VARIABLES HARDCODEADAS PARA 110MM 45° (TipoColze==1 y default) =====

    # Rotaciones sobre el propio eje (en grados)
    ROT_X_110MM_45 = 180.0  # Rotación en eje X
    ROT_Y_110MM_45 = 0.0  # Rotación en eje Y
    ROT_Z_110MM_45 = 0.0   # Rotación en eje Z

    # =========================================================================

    # ===== VARIABLES HARDCODEADAS PARA 40MM 45° (TipoColze==2) =====

    # Rotaciones sobre el propio eje (en grados)
    ROT_X_40MM_45 = 180.0  # Rotación en eje X
    ROT_Y_40MM_45 = 0.0  # Rotación en eje Y
    ROT_Z_40MM_45 = -180.0  # Rotación en eje Z

    # =====================================================================

    # ===== VARIABLES HARDCODEADAS PARA 1_40MM 87° (TipoColze==3) =====

    # Rotaciones sobre el propio eje (en grados)
    ROT_X_1_40MM_87 = 0.0   # Rotación en eje X270
    ROT_Y_1_40MM_87 = 0.0   # Rotación en eje Y180
    ROT_Z_1_40MM_87 = 0.0   # Rotación en eje Z

    # ===================================================================

    # ===== VARIABLES HARDCODEADAS PARA 110MM 87° (TipoColze==5) =====

    # Rotaciones sobre el propio eje (en grados)
    ROT_X_110MM_87 = 180.0   # Rotación adicional en eje X
    ROT_Y_110MM_87 = 90.0    # Rotación adicional en eje Y
    ROT_Z_110MM_87 = 90.0     # Rotación adicional en eje Z

    # =================================================================

    # Mapeo/parametría base usada en 45°
    PARAMS = [
        dict(DIAMETRO=110.0, LARGO_VERTICAL=10.0, LARGO_INCLINADA=80.0, LARGO_HORIZONTAL=70.0,
             ANGULO_INCLINADA=23.0, ANGULO_HORIZONTAL=45.0, LARGO_ANILLO=73.0, SOBRESALE_ANILLO=9.0),
        dict(DIAMETRO=40.0, LARGO_VERTICAL=20.0, LARGO_INCLINADA=3.0, LARGO_HORIZONTAL=60.0,
             ANGULO_INCLINADA=25.0, ANGULO_HORIZONTAL=45.0, LARGO_ANILLO=40.0, SOBRESALE_ANILLO=5.0)
    ]

    def __init__(self, build_ele, doc=None):
        self.build_ele = build_ele
        self.doc = doc

    # ---------- API pública ----------
    def create_result(self) -> CreateElementResult:
        """Evalúa TipoColze y construye la variante correspondiente."""
        tipo_val = self._get_tipo_colze(default=1)

        if tipo_val == 2:
            props, solid = self._build_40mm_45()
        elif tipo_val == 3:
            props, solid = self._build_1_40mm_87()
        elif tipo_val == 4:
            props, solid = self._build_2_40mm_87()
        elif tipo_val in (5, 6):
            props, solid = self._build_110mm_87(variant=tipo_val)
        else:
            props, solid = self._build_110mm_45()

        if solid is None or not solid.IsValid():
            print("Error al crear el codo.")
            return CreateElementResult([])

        # Crear ModelElement3D
        model_elem = AllplanBasisElements.ModelElement3D(props, solid)

        # Agregar atributos personalizados según el tipo
        attr_list = []
        if tipo_val == 1:  # 110mm 45° (default)
            attr_list.append(AllplanBaseElements.AttributeString(1083, "COLZE M-F 110Ø 45º"))
            attr_list.append(AllplanBaseElements.AttributeString(1084, "Ø110"))
            attr_list.append(AllplanBaseElements.AttributeString(1085, ""))
            attr_list.append(AllplanBaseElements.AttributeString(1086, ""))
            attr_list.append(AllplanBaseElements.AttributeString(1087, ""))
            attr_list.append(AllplanBaseElements.AttributeString(1895, ""))
            attr_list.append(AllplanBaseElements.AttributeString(1896, "110"))
            
            # Agregar atributos de usuario adicionales si hay documento disponible
            if self.doc:
                self._add_user_attributes_110mm_45(attr_list)
        elif tipo_val == 2:  # 40mm 45°
            attr_list.append(AllplanBaseElements.AttributeString(1083, "CS45ºØ40"))
            attr_list.append(AllplanBaseElements.AttributeString(1084, "Ø40"))
            attr_list.append(AllplanBaseElements.AttributeString(1085, ""))
            attr_list.append(AllplanBaseElements.AttributeString(1086, ""))
            attr_list.append(AllplanBaseElements.AttributeString(1087, ""))
            attr_list.append(AllplanBaseElements.AttributeString(1895, ""))
            attr_list.append(AllplanBaseElements.AttributeString(1896, "40"))
            
            # Agregar atributos de usuario adicionales si hay documento disponible
            if self.doc:
                self._add_user_attributes_40mm_45(attr_list)
        elif tipo_val in (3, 4):  # 40mm 87° (ambas variantes)
            attr_list.append(AllplanBaseElements.AttributeString(1083, "CS87ºØ40"))
            attr_list.append(AllplanBaseElements.AttributeString(1084, "Ø40"))
            attr_list.append(AllplanBaseElements.AttributeString(1085, ""))
            attr_list.append(AllplanBaseElements.AttributeString(1086, ""))
            attr_list.append(AllplanBaseElements.AttributeString(1087, ""))
            attr_list.append(AllplanBaseElements.AttributeString(1895, ""))
            attr_list.append(AllplanBaseElements.AttributeString(1896, "40"))
            
            # Agregar atributos de usuario adicionales si hay documento disponible
            if self.doc:
                self._add_user_attributes_40mm_87(attr_list)
        elif tipo_val in (5, 6):  # 110mm 87° (ambas variantes)
            attr_list.append(AllplanBaseElements.AttributeString(1083, "COLZE M-F 110Ø 87º"))
            attr_list.append(AllplanBaseElements.AttributeString(1084, "Ø110"))
            attr_list.append(AllplanBaseElements.AttributeString(1085, ""))
            attr_list.append(AllplanBaseElements.AttributeString(1086, ""))
            attr_list.append(AllplanBaseElements.AttributeString(1087, ""))
            attr_list.append(AllplanBaseElements.AttributeString(1895, ""))
            attr_list.append(AllplanBaseElements.AttributeString(1896, "110"))
            
            # Agregar atributos de usuario adicionales si hay documento disponible
            if self.doc:
                self._add_user_attributes_110mm_87(attr_list)

        # Asignar atributos
        if attr_list:
            attr_set_list = []
            attr_set_list.append(AllplanBaseElements.AttributeSet(attr_list))
            attributes = AllplanBaseElements.Attributes(attr_set_list)
            model_elem.SetAttributes(attributes)

        return CreateElementResult([model_elem])

    # ---------- Helpers generales ----------
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
    def _crear_prisma(diametro: float, largo: float):
        return AllplanGeo.Polyhedron3D.CreateCuboid(
            AllplanGeo.Point3D(0, 0, 0),
            AllplanGeo.Point3D(diametro, diametro, largo)
        )

    def _get_tipo_colze(self, default: int = 1) -> int:
        attr = getattr(self.build_ele, "TipoColze", None)
        try:
            return int(getattr(attr, "value", default)) if attr is not None else default
        except Exception:
            return default

    def _add_user_attributes_110mm_45(self, attr_list):
        """Agrega atributos de usuario para codo 110mm 45°."""
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

            # pmp_CARTICULO: "KN07_004_003"
            if attr_pmp_carticulo_id and attr_pmp_carticulo_id > 0:
                attr_list.append(AllplanBaseElements.AttributeString(attr_pmp_carticulo_id, "KN07_004_003"))

            # pmp_nom: "COLZE M-F 110Ø 45°"
            if attr_pmp_nom_id and attr_pmp_nom_id > 0:
                attr_list.append(AllplanBaseElements.AttributeString(attr_pmp_nom_id, "COLZE M-F 110Ø 45°"))

            # pmp_pes_unitari: 0.2110 (AttributeDouble)
            if attr_pmp_pes_unitari_id and attr_pmp_pes_unitari_id > 0:
                attr_list.append(AllplanBaseElements.AttributeDouble(attr_pmp_pes_unitari_id, 0.2110))

            # pmp_seccio: "Ø110/45°" (AttributeString)
            if attr_pmp_seccio_id and attr_pmp_seccio_id > 0:
                attr_list.append(AllplanBaseElements.AttributeString(attr_pmp_seccio_id, "Ø110/45°"))

        except Exception as e:
            # No bloquear la creación si hay problemas con los atributos
            print(f"[Colze_rigidSane_004] Advertencia al agregar atributos de usuario 110mm 45°: {e}")

    def _add_user_attributes_40mm_45(self, attr_list):
        """Agrega atributos de usuario para codo 40mm 45°."""
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

            # pmp_CARTICULO: "KN07_004_001"
            if attr_pmp_carticulo_id and attr_pmp_carticulo_id > 0:
                attr_list.append(AllplanBaseElements.AttributeString(attr_pmp_carticulo_id, "KN07_004_001"))

            # pmp_nom: "COLZE M-F 40Ø 45°"
            if attr_pmp_nom_id and attr_pmp_nom_id > 0:
                attr_list.append(AllplanBaseElements.AttributeString(attr_pmp_nom_id, "COLZE M-F 40Ø 45°"))

            # pmp_pes_unitari: 0.0340 (AttributeDouble)
            if attr_pmp_pes_unitari_id and attr_pmp_pes_unitari_id > 0:
                attr_list.append(AllplanBaseElements.AttributeDouble(attr_pmp_pes_unitari_id, 0.0340))

            # pmp_seccio: "40" (AttributeInt o AttributeString según el tipo)
            if attr_pmp_seccio_id and attr_pmp_seccio_id > 0:
                try:
                    attr_list.append(AllplanBaseElements.AttributeInt(attr_pmp_seccio_id, 40))
                except:
                    attr_list.append(AllplanBaseElements.AttributeString(attr_pmp_seccio_id, "40"))

        except Exception as e:
            # No bloquear la creación si hay problemas con los atributos
            print(f"[Colze_rigidSane_004] Advertencia al agregar atributos de usuario 40mm 45°: {e}")

    def _add_user_attributes_110mm_87(self, attr_list):
        """Agrega atributos de usuario para codo 110mm 87° (90°)."""
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

            # pmp_CARTICULO: "KN07_004_004"
            if attr_pmp_carticulo_id and attr_pmp_carticulo_id > 0:
                attr_list.append(AllplanBaseElements.AttributeString(attr_pmp_carticulo_id, "KN07_004_004"))

            # pmp_nom: "COLZE M-F 110Ø 87°"
            if attr_pmp_nom_id and attr_pmp_nom_id > 0:
                attr_list.append(AllplanBaseElements.AttributeString(attr_pmp_nom_id, "COLZE M-F 110Ø 87°"))

            # pmp_pes_unitari: 0.4633 (AttributeDouble)
            if attr_pmp_pes_unitari_id and attr_pmp_pes_unitari_id > 0:
                attr_list.append(AllplanBaseElements.AttributeDouble(attr_pmp_pes_unitari_id, 0.4633))

            # pmp_seccio: "110" (AttributeInt o AttributeString según el tipo)
            if attr_pmp_seccio_id and attr_pmp_seccio_id > 0:
                try:
                    attr_list.append(AllplanBaseElements.AttributeInt(attr_pmp_seccio_id, 110))
                except:
                    attr_list.append(AllplanBaseElements.AttributeString(attr_pmp_seccio_id, "110"))

        except Exception as e:
            # No bloquear la creación si hay problemas con los atributos
            print(f"[Colze_rigidSane_004] Advertencia al agregar atributos de usuario 110mm 87°: {e}")

    def _add_user_attributes_40mm_87(self, attr_list):
        """Agrega atributos de usuario para codo 40mm 87°."""
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

            # pmp_CARTICULO: "KN07_004_002"
            if attr_pmp_carticulo_id and attr_pmp_carticulo_id > 0:
                attr_list.append(AllplanBaseElements.AttributeString(attr_pmp_carticulo_id, "KN07_004_002"))

            # pmp_nom: "COLZE M-F 40Ø 87°"
            if attr_pmp_nom_id and attr_pmp_nom_id > 0:
                attr_list.append(AllplanBaseElements.AttributeString(attr_pmp_nom_id, "COLZE M-F 40Ø 87°"))

            # pmp_pes_unitari: 0.0530 (AttributeDouble)
            if attr_pmp_pes_unitari_id and attr_pmp_pes_unitari_id > 0:
                attr_list.append(AllplanBaseElements.AttributeDouble(attr_pmp_pes_unitari_id, 0.0530))

            # pmp_seccio: "40" (AttributeInt o AttributeString según el tipo)
            if attr_pmp_seccio_id and attr_pmp_seccio_id > 0:
                try:
                    attr_list.append(AllplanBaseElements.AttributeInt(attr_pmp_seccio_id, 40))
                except:
                    attr_list.append(AllplanBaseElements.AttributeString(attr_pmp_seccio_id, "40"))

        except Exception as e:
            # No bloquear la creación si hay problemas con los atributos
            print(f"[Colze_rigidSane_004] Advertencia al agregar atributos de usuario 40mm 87°: {e}")

    # ---------- VARIANTES ----------
    def _build_40mm_45(self):
        """Tipo 2: 40mm 45°"""
        p = self.PARAMS[1]
        props = self._props(color=70)

        cubo0 = self._crear_prisma(p['DIAMETRO'], p['LARGO_VERTICAL'])

        rad_incl = math.radians(p['ANGULO_INCLINADA'])
        cubo1 = self._crear_prisma(p['DIAMETRO'], p['LARGO_INCLINADA'])
        m1 = AllplanGeo.Matrix3D(); m1.SetRotation(AllplanGeo.Line3D(0, 0, 0, 1, 0, 0), AllplanGeo.Angle(-rad_incl))
        cubo1 = AllplanGeo.Transform(cubo1, m1)
        t1 = AllplanGeo.Matrix3D(); t1.SetTranslation(AllplanGeo.Vector3D(0, 0, p['LARGO_VERTICAL']))
        cubo1 = AllplanGeo.Transform(cubo1, t1)

        dz = p['LARGO_INCLINADA'] * math.cos(rad_incl)
        dy = p['LARGO_INCLINADA'] * math.sin(rad_incl)

        rad_h = math.radians(p['ANGULO_HORIZONTAL'])
        cubo2 = self._crear_prisma(p['DIAMETRO'], p['LARGO_HORIZONTAL'])
        m2 = AllplanGeo.Matrix3D(); m2.SetRotation(AllplanGeo.Line3D(0, 0, 0, 1, 0, 0), AllplanGeo.Angle(-rad_h))
        cubo2 = AllplanGeo.Transform(cubo2, m2)
        t2 = AllplanGeo.Matrix3D(); t2.SetTranslation(AllplanGeo.Vector3D(0, dy, p['LARGO_VERTICAL'] + dz))
        cubo2 = AllplanGeo.Transform(cubo2, t2)

        anillo = AllplanGeo.Polyhedron3D.CreateCuboid(
            AllplanGeo.Point3D(-p['SOBRESALE_ANILLO'], -p['SOBRESALE_ANILLO'], -p['LARGO_ANILLO']),
            AllplanGeo.Point3D(p['DIAMETRO'] + p['SOBRESALE_ANILLO'], p['DIAMETRO'] + p['SOBRESALE_ANILLO'], 0)
        )

        err, codo = AllplanGeo.MakeUnion(cubo0, cubo1)
        if err == 0 and codo.IsValid(): err, codo = AllplanGeo.MakeUnion(codo, cubo2)
        if err == 0 and codo.IsValid(): err, codo = AllplanGeo.MakeUnion(codo, anillo)
        if err != 0 or not codo.IsValid():
            return props, None

        eje_y = AllplanGeo.Axis3D(AllplanGeo.Point3D(0, 0, 0), AllplanGeo.Vector3D(0, 1, 0))
        codo_rot = AllplanGeo.Rotate(codo, eje_y, AllplanGeo.Angle(math.radians(270)))

        # Aplicar rotaciones hardcodeadas sobre el propio eje
        # Calcular centroide aproximado del codo para rotar sobre su centro
        cx = p['DIAMETRO'] / 2.0
        cy = p['DIAMETRO'] / 2.0 + p['LARGO_INCLINADA'] * math.sin(math.radians(p['ANGULO_INCLINADA'])) / 2.0
        cz = (p['LARGO_VERTICAL'] + p['LARGO_INCLINADA'] * math.cos(math.radians(p['ANGULO_INCLINADA'])) + p['LARGO_HORIZONTAL']) / 2.0

        # Aplicar rotaciones en orden X, Y, Z
        if abs(self.ROT_X_40MM_45) > 1e-6:
            eje_x = AllplanGeo.Axis3D(AllplanGeo.Point3D(cx, cy, cz), AllplanGeo.Vector3D(1, 0, 0))
            codo_rot = AllplanGeo.Rotate(codo_rot, eje_x, AllplanGeo.Angle(math.radians(self.ROT_X_40MM_45)))
        if abs(self.ROT_Y_40MM_45) > 1e-6:
            eje_y_rot = AllplanGeo.Axis3D(AllplanGeo.Point3D(cx, cy, cz), AllplanGeo.Vector3D(0, 1, 0))
            codo_rot = AllplanGeo.Rotate(codo_rot, eje_y_rot, AllplanGeo.Angle(math.radians(self.ROT_Y_40MM_45)))
        if abs(self.ROT_Z_40MM_45) > 1e-6:
            eje_z = AllplanGeo.Axis3D(AllplanGeo.Point3D(cx, cy, cz), AllplanGeo.Vector3D(0, 0, 1))
            codo_rot = AllplanGeo.Rotate(codo_rot, eje_z, AllplanGeo.Angle(math.radians(self.ROT_Z_40MM_45)))

        return props, codo_rot

    def _build_1_40mm_87(self):
        """Tipo 3: 1_40mm 87°"""
        DIAMETRO = 40.0
        LARGO_VERTICAL = 40.0
        LARGO_HORIZONTAL = 60.0
        SOBRESALE_ANILLO = 10.0
        LARGO_ANILLO = 30.0

        props = self._props(color=70)

        cubo_vertical = AllplanGeo.Polyhedron3D.CreateCuboid(
            AllplanGeo.Point3D(0, 0, 0),
            AllplanGeo.Point3D(DIAMETRO, DIAMETRO, LARGO_VERTICAL)
        )
        cubo_horizontal = AllplanGeo.Polyhedron3D.CreateCuboid(
            AllplanGeo.Point3D(0, 0, LARGO_VERTICAL),
            AllplanGeo.Point3D(LARGO_HORIZONTAL, DIAMETRO, LARGO_VERTICAL + DIAMETRO)
        )
        anillo = AllplanGeo.Polyhedron3D.CreateCuboid(
            AllplanGeo.Point3D(LARGO_HORIZONTAL, -SOBRESALE_ANILLO, LARGO_VERTICAL - SOBRESALE_ANILLO),
            AllplanGeo.Point3D(LARGO_HORIZONTAL + LARGO_ANILLO, DIAMETRO + SOBRESALE_ANILLO,
                               LARGO_VERTICAL + DIAMETRO + SOBRESALE_ANILLO)
        )
        if not anillo.IsValid():
            return props, None

        err, solido = AllplanGeo.MakeUnion(cubo_vertical, cubo_horizontal)
        if err == 0 and solido.IsValid(): err, solido = AllplanGeo.MakeUnion(solido, anillo)
        if err != 0 or not solido.IsValid():
            return props, None

        # Aplicar rotaciones hardcodeadas sobre el propio eje
        # Calcular centroide aproximado del objeto para rotar sobre su centro
        cx = (LARGO_HORIZONTAL + DIAMETRO) / 2.0
        cy = DIAMETRO / 2.0
        cz = (LARGO_VERTICAL + DIAMETRO) / 2.0

        # Aplicar rotaciones en orden X, Y, Z
        if abs(self.ROT_X_1_40MM_87) > 1e-6:
            eje_x = AllplanGeo.Axis3D(AllplanGeo.Point3D(cx, cy, cz), AllplanGeo.Vector3D(1, 0, 0))
            solido = AllplanGeo.Rotate(solido, eje_x, AllplanGeo.Angle(math.radians(self.ROT_X_1_40MM_87)))
        if abs(self.ROT_Y_1_40MM_87) > 1e-6:
            eje_y = AllplanGeo.Axis3D(AllplanGeo.Point3D(cx, cy, cz), AllplanGeo.Vector3D(0, 1, 0))
            solido = AllplanGeo.Rotate(solido, eje_y, AllplanGeo.Angle(math.radians(self.ROT_Y_1_40MM_87)))
        if abs(self.ROT_Z_1_40MM_87) > 1e-6:
            eje_z = AllplanGeo.Axis3D(AllplanGeo.Point3D(cx, cy, cz), AllplanGeo.Vector3D(0, 0, 1))
            solido = AllplanGeo.Rotate(solido, eje_z, AllplanGeo.Angle(math.radians(self.ROT_Z_1_40MM_87)))

        return props, solido

    def _build_2_40mm_87(self):
        """Tipo 4: 2_40mm 87° (mismas piezas que el tipo 3, con rotaciones fijas)."""
        DIAMETRO = 40.0
        LARGO_VERTICAL = 50.0
        LARGO_HORIZONTAL = 60.0
        SOBRESALE_ANILLO = 10.0
        LARGO_ANILLO = 30.0

        props = self._props(color=70)

        cubo_vertical = AllplanGeo.Polyhedron3D.CreateCuboid(
            AllplanGeo.Point3D(0, 0, 0),
            AllplanGeo.Point3D(DIAMETRO, DIAMETRO, LARGO_VERTICAL)
        )
        cubo_horizontal = AllplanGeo.Polyhedron3D.CreateCuboid(
            AllplanGeo.Point3D(0, 0, LARGO_VERTICAL),
            AllplanGeo.Point3D(LARGO_HORIZONTAL, DIAMETRO, LARGO_VERTICAL + DIAMETRO)
        )
        anillo = AllplanGeo.Polyhedron3D.CreateCuboid(
            AllplanGeo.Point3D(LARGO_HORIZONTAL, -SOBRESALE_ANILLO, LARGO_VERTICAL - SOBRESALE_ANILLO),
            AllplanGeo.Point3D(LARGO_HORIZONTAL + LARGO_ANILLO, DIAMETRO + SOBRESALE_ANILLO,
                               LARGO_VERTICAL + DIAMETRO + SOBRESALE_ANILLO)
        )
        if not anillo.IsValid():
            return props, None

        err, solido = AllplanGeo.MakeUnion(cubo_vertical, cubo_horizontal)
        if err == 0 and solido.IsValid(): err, solido = AllplanGeo.MakeUnion(solido, anillo)
        if err != 0 or not solido.IsValid():
            return props, None

        # Rotaciones fijas para este caso
        ROT_X, ROT_Y, ROT_Z = 90, 270, 0
        s = solido
        eje_x = AllplanGeo.Axis3D(AllplanGeo.Point3D(0, 0, 0), AllplanGeo.Vector3D(1, 0, 0))
        eje_y = AllplanGeo.Axis3D(AllplanGeo.Point3D(0, 0, 0), AllplanGeo.Vector3D(0, 1, 0))
        eje_z = AllplanGeo.Axis3D(AllplanGeo.Point3D(0, 0, 0), AllplanGeo.Vector3D(0, 0, 1))

        if ROT_X:
            s = AllplanGeo.Rotate(s, eje_x, AllplanGeo.Angle(math.radians(ROT_X)))
        if ROT_Y:
            s = AllplanGeo.Rotate(s, eje_y, AllplanGeo.Angle(math.radians(ROT_Y)))
        if ROT_Z:
            s = AllplanGeo.Rotate(s, eje_z, AllplanGeo.Angle(math.radians(ROT_Z)))

        return props, s

    def _build_110mm_87(self, variant: int):
        """Tipos 5/6: 110mm 87° (la 6 agrega rotación Y=270°)."""
        DIAMETRO = 110.0
        LARGO_VERTICAL = 110.0
        LARGO_INCLINADA = 110.0
        LARGO_HORIZONTAL = 110.0
        ANGULO_INCLINADA = 45.0
        ANGULO_HORIZONTAL = 90.0
        LARGO_ANILLO = 75.0
        SOBRESALE_ANILLO = 10.0

        props = self._props(color=120)

        cubo0 = self._crear_prisma(DIAMETRO, LARGO_VERTICAL)

        rad_inc = math.radians(ANGULO_INCLINADA)
        cubo1 = self._crear_prisma(DIAMETRO, LARGO_INCLINADA)
        m1 = AllplanGeo.Matrix3D(); m1.SetRotation(AllplanGeo.Line3D(0, 0, 0, 1, 0, 0), AllplanGeo.Angle(-rad_inc))
        cubo1 = AllplanGeo.Transform(cubo1, m1)
        t1 = AllplanGeo.Matrix3D(); t1.SetTranslation(AllplanGeo.Vector3D(0, 0, LARGO_VERTICAL))
        cubo1 = AllplanGeo.Transform(cubo1, t1)

        dz = LARGO_INCLINADA * math.cos(rad_inc)
        dy = LARGO_INCLINADA * math.sin(rad_inc)

        rad_h = math.radians(ANGULO_HORIZONTAL)
        cubo2 = self._crear_prisma(DIAMETRO, LARGO_HORIZONTAL)
        m2 = AllplanGeo.Matrix3D(); m2.SetRotation(AllplanGeo.Line3D(0, 0, 0, 1, 0, 0), AllplanGeo.Angle(-rad_h))
        cubo2 = AllplanGeo.Transform(cubo2, m2)
        t2 = AllplanGeo.Matrix3D(); t2.SetTranslation(AllplanGeo.Vector3D(0, dy, LARGO_VERTICAL + dz))
        cubo2 = AllplanGeo.Transform(cubo2, t2)

        anillo = AllplanGeo.Polyhedron3D.CreateCuboid(
            AllplanGeo.Point3D(-SOBRESALE_ANILLO, -SOBRESALE_ANILLO, -LARGO_ANILLO),
            AllplanGeo.Point3D(DIAMETRO + SOBRESALE_ANILLO, DIAMETRO + SOBRESALE_ANILLO, 0)
        )

        err, codo = AllplanGeo.MakeUnion(cubo0, cubo1)
        if err == 0 and codo.IsValid(): err, codo = AllplanGeo.MakeUnion(codo, cubo2)
        if err == 0 and codo.IsValid(): err, codo = AllplanGeo.MakeUnion(codo, anillo)
        if err != 0 or not codo.IsValid():
            return props, None

        eje_z = AllplanGeo.Axis3D(AllplanGeo.Point3D(0, 0, 0), AllplanGeo.Vector3D(0, 0, 1))
        s = AllplanGeo.Rotate(codo, eje_z, AllplanGeo.Angle(math.radians(90)))
        eje_x = AllplanGeo.Axis3D(AllplanGeo.Point3D(0, 0, 0), AllplanGeo.Vector3D(1, 0, 0))
        s = AllplanGeo.Rotate(s, eje_x, AllplanGeo.Angle(math.radians(180)))

        if variant == 6:
            eje_y = AllplanGeo.Axis3D(AllplanGeo.Point3D(0, 0, 0), AllplanGeo.Vector3D(0, 1, 0))
            s = AllplanGeo.Rotate(s, eje_y, AllplanGeo.Angle(math.radians(270)))

        # Aplicar rotaciones hardcodeadas sobre el propio eje para TipoColze==5
        if variant == 5:
            # Calcular centroide aproximado del codo para rotar sobre su centro
            cx = DIAMETRO / 2.0
            cy = DIAMETRO / 2.0 + LARGO_INCLINADA * math.sin(math.radians(ANGULO_INCLINADA)) / 2.0
            cz = (LARGO_VERTICAL + LARGO_INCLINADA * math.cos(math.radians(ANGULO_INCLINADA)) + LARGO_HORIZONTAL) / 2.0

            # Aplicar rotaciones en orden X, Y, Z
            if abs(self.ROT_X_110MM_87) > 1e-6:
                eje_x_rot = AllplanGeo.Axis3D(AllplanGeo.Point3D(cx, cy, cz), AllplanGeo.Vector3D(1, 0, 0))
                s = AllplanGeo.Rotate(s, eje_x_rot, AllplanGeo.Angle(math.radians(self.ROT_X_110MM_87)))
            if abs(self.ROT_Y_110MM_87) > 1e-6:
                eje_y_rot = AllplanGeo.Axis3D(AllplanGeo.Point3D(cx, cy, cz), AllplanGeo.Vector3D(0, 1, 0))
                s = AllplanGeo.Rotate(s, eje_y_rot, AllplanGeo.Angle(math.radians(self.ROT_Y_110MM_87)))
            if abs(self.ROT_Z_110MM_87) > 1e-6:
                eje_z_rot = AllplanGeo.Axis3D(AllplanGeo.Point3D(cx, cy, cz), AllplanGeo.Vector3D(0, 0, 1))
                s = AllplanGeo.Rotate(s, eje_z_rot, AllplanGeo.Angle(math.radians(self.ROT_Z_110MM_87)))

        return props, s

    def _build_110mm_45(self):
        """Default (y Tipo 1): 110mm 45°."""
        p = self.PARAMS[0]
        props = self._props(color=70)

        cubo0 = self._crear_prisma(p['DIAMETRO'], p['LARGO_VERTICAL'])

        rad_incl = math.radians(p['ANGULO_INCLINADA'])
        cubo1 = self._crear_prisma(p['DIAMETRO'], p['LARGO_INCLINADA'])
        m1 = AllplanGeo.Matrix3D(); m1.SetRotation(AllplanGeo.Line3D(0, 0, 0, 1, 0, 0), AllplanGeo.Angle(-rad_incl))
        cubo1 = AllplanGeo.Transform(cubo1, m1)
        t1 = AllplanGeo.Matrix3D(); t1.SetTranslation(AllplanGeo.Vector3D(0, 0, p['LARGO_VERTICAL']))
        cubo1 = AllplanGeo.Transform(cubo1, t1)

        dz = p['LARGO_INCLINADA'] * math.cos(rad_incl)
        dy = p['LARGO_INCLINADA'] * math.sin(rad_incl)

        rad_h = math.radians(p['ANGULO_HORIZONTAL'])
        cubo2 = self._crear_prisma(p['DIAMETRO'], p['LARGO_HORIZONTAL'])
        m2 = AllplanGeo.Matrix3D(); m2.SetRotation(AllplanGeo.Line3D(0, 0, 0, 1, 0, 0), AllplanGeo.Angle(-rad_h))
        cubo2 = AllplanGeo.Transform(cubo2, m2)
        t2 = AllplanGeo.Matrix3D(); t2.SetTranslation(AllplanGeo.Vector3D(0, dy, p['LARGO_VERTICAL'] + dz))
        cubo2 = AllplanGeo.Transform(cubo2, t2)

        anillo = AllplanGeo.Polyhedron3D.CreateCuboid(
            AllplanGeo.Point3D(-p['SOBRESALE_ANILLO'], -p['SOBRESALE_ANILLO'], -p['LARGO_ANILLO']),
            AllplanGeo.Point3D(p['DIAMETRO'] + p['SOBRESALE_ANILLO'], p['DIAMETRO'] + p['SOBRESALE_ANILLO'], 0)
        )

        err, codo = AllplanGeo.MakeUnion(cubo0, cubo1)
        if err == 0 and codo.IsValid(): err, codo = AllplanGeo.MakeUnion(codo, cubo2)
        if err == 0 and codo.IsValid(): err, codo = AllplanGeo.MakeUnion(codo, anillo)
        if err != 0 or not codo.IsValid():
            return props, None

        eje_y = AllplanGeo.Axis3D(AllplanGeo.Point3D(0, 0, 0), AllplanGeo.Vector3D(0, 1, 0))
        codo_rot = AllplanGeo.Rotate(codo, eje_y, AllplanGeo.Angle(math.radians(270)))

        # Aplicar rotaciones hardcodeadas sobre el propio eje
        # Calcular centroide aproximado del codo para rotar sobre su centro
        cx = p['DIAMETRO'] / 2.0
        cy = p['DIAMETRO'] / 2.0 + p['LARGO_INCLINADA'] * math.sin(math.radians(p['ANGULO_INCLINADA'])) / 2.0
        cz = (p['LARGO_VERTICAL'] + p['LARGO_INCLINADA'] * math.cos(math.radians(p['ANGULO_INCLINADA'])) + p['LARGO_HORIZONTAL']) / 2.0

        # Aplicar rotaciones en orden X, Y, Z
        if abs(self.ROT_X_110MM_45) > 1e-6:
            eje_x = AllplanGeo.Axis3D(AllplanGeo.Point3D(cx, cy, cz), AllplanGeo.Vector3D(1, 0, 0))
            codo_rot = AllplanGeo.Rotate(codo_rot, eje_x, AllplanGeo.Angle(math.radians(self.ROT_X_110MM_45)))
        if abs(self.ROT_Y_110MM_45) > 1e-6:
            eje_y_rot = AllplanGeo.Axis3D(AllplanGeo.Point3D(cx, cy, cz), AllplanGeo.Vector3D(0, 1, 0))
            codo_rot = AllplanGeo.Rotate(codo_rot, eje_y_rot, AllplanGeo.Angle(math.radians(self.ROT_Y_110MM_45)))
        if abs(self.ROT_Z_110MM_45) > 1e-6:
            eje_z = AllplanGeo.Axis3D(AllplanGeo.Point3D(cx, cy, cz), AllplanGeo.Vector3D(0, 0, 1))
            codo_rot = AllplanGeo.Rotate(codo_rot, eje_z, AllplanGeo.Angle(math.radians(self.ROT_Z_110MM_45)))

        return props, codo_rot


# ===== Punto de entrada PythonPart =====
def create_element(build_ele, _doc) -> CreateElementResult:
    """Instancia la clase y delega la creación del elemento."""
    return CodoRigido(build_ele, _doc).create_result()
