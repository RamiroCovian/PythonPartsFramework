# -*- coding: utf-8 -*-
"""Codo Rígido """

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
    LAYER_KN_AIGUA = 40061  # KN_AIGUA (kn_aigua)
    LAYER_40055 = 40055
    LAYER_40054 = 40054
    LAYER_40057 = 40057  # Layer para elemento 4 (cilindro)
    
    # Rotaciones hardcodeadas para L3000_D87 (TipoColze==2), en grados
    ROT_X_L3000_D87 = 180.0
    ROT_Y_L3000_D87 = 0.0
    ROT_Z_L3000_D87 = 0.0
    # Rotaciones hardcodeadas para L1000_D110 (TipoColze==0), en grados
    ROT_X_L1000_D110 = 225.0
    ROT_Y_L1000_D110 = 0.0
    ROT_Z_L1000_D110 = 0.0
    # Rotaciones hardcodeadas para L3000_D45 (TipoColze==1), en grados
    ROT_X_L3000_D45 = 180.0
    ROT_Y_L3000_D45 = 0.0
    ROT_Z_L3000_D45 = 180.0
    
    # Rotaciones hardcodeadas para L1000_D87 (TipoColze==3, 110mm 87°), en grados
    ROT_X_110MM_87 = 0.0   # Rotación adicional en eje X
    ROT_Y_110MM_87 = 90.0    # Rotación adicional en eje Y
    ROT_Z_110MM_87 = 0.0     # Rotación adicional en eje Z

    # Desplazamientos hardcodeados para el cuboide cilíndrico en L3000_D87 (TipoColze==2)
    DESP_X_CUBO_CILINDRICO = -3.0
    DESP_Y_CUBO_CILINDRICO = -20.0
    DESP_Z_CUBO_CILINDRICO = -20.0

    # Dimensiones hardcodeadas para el cuboide cilíndrico en L3000_D87 (TipoColze==2)
    ANCHO_CUBO_CILINDRICO = 40.0   # Ancho (X)
    ALTO_CUBO_CILINDRICO = 40.0    # Alto (Y)
    LARGO_CUBO_CILINDRICO = 18.0   # Largo (Z)

    # Rotación adicional para el cuboide cilíndrico (para que "caiga" en sintonía)
    ROT_ADICIONAL_CUBO_CILINDRICO = -3.0  # grados, rotación alrededor del eje Y local

    """Implementa codos rígidos con variantes y un caso especial de 40 mm · 87°."""

    # Parametría base para las variantes "default"
    # PARAMS: cada dict representa una variante (ver .pyp: TipoColze)
    #
    # Cuboide vertical:
    #   - DIAMETRO
    #   - LARGO_VERTICAL
    # Tramo inclinado:
    #   - LARGO_INCLINADA
    #   - ANGULO_INCLINADA
    # Tramo horizontal:
    #   - LARGO_HORIZONTAL
    #   - ANGULO_HORIZONTAL
    # Anillo:
    #   - LARGO_ANILLO
    #   - SOBRESALE_ANILLO
    PARAMS = [
        dict(
            # Cuboide vertical
            DIAMETRO=110.0,
            LARGO_VERTICAL=3.0,
            # Tramo inclinado
            LARGO_INCLINADA=85.0,
            ANGULO_INCLINADA=22.5,
            # Tramo horizontal
            LARGO_HORIZONTAL=70.0,
            ANGULO_HORIZONTAL=45.0,
            # Anillo
            LARGO_ANILLO=75.0,
            SOBRESALE_ANILLO=9.0
        ),
        dict(
            # Cuboide vertical
            DIAMETRO=40.0,
            LARGO_VERTICAL=20.0,
            # Tramo inclinado
            LARGO_INCLINADA=5.0,
            ANGULO_INCLINADA=25.0,
            # Tramo horizontal
            LARGO_HORIZONTAL=58.0,
            ANGULO_HORIZONTAL=45.0,
            # Anillo
            LARGO_ANILLO=40.0,
            SOBRESALE_ANILLO=5.0
        )
    ]

    def __init__(self, build_ele, doc=None):
        self.build_ele = build_ele
        self.doc = doc

    # ---------- API pública ----------
    def create_result(self) -> CreateElementResult:
        """Evalúa TipoColze y crea los elementos 3D correspondientes."""
        tipo = self._get_tipo_colze(default=0)
        
        # Validar que el tipo esté en el rango válido (0-3)
        if tipo not in [0, 1, 2, 3]:
            print(f"Advertencia: TipoColze={tipo} no es válido. Usando tipo por defecto 0.")
            tipo = 0

        if tipo == 2:
            # Caso especial L3000_D87 (40 mm, 87°) → 3 elementos separados
            elems = self._build_40mm_87_especial()
        elif tipo == 3:
            # 110mm 87° (idéntico al tipo 6 de Colze_rigidSane_004.py)
            props, solid = self._build_110mm_87(variant=6)
            if solid is None or not solid.IsValid():
                print("Error al crear el codo 110mm 87°.")
                return CreateElementResult([])
            
            # Crear ModelElement3D
            model_elem = AllplanBasisElements.ModelElement3D(props, solid)
            
            # Agregar atributos personalizados
            attr_list = []
            # Custom attribute 01: CS87ºØ110
            attr_list.append(AllplanBaseElements.AttributeString(1083, "CS87ºØ110"))
            # Custom attribute 02: Ø110
            attr_list.append(AllplanBaseElements.AttributeString(1084, "Ø110"))
            # Custom attribute 03-06: undefined (vacíos)
            attr_list.append(AllplanBaseElements.AttributeString(1085, ""))
            attr_list.append(AllplanBaseElements.AttributeString(1086, ""))
            attr_list.append(AllplanBaseElements.AttributeString(1087, ""))
            attr_list.append(AllplanBaseElements.AttributeString(1895, ""))
            # Custom attribute 07: 110
            attr_list.append(AllplanBaseElements.AttributeString(1896, "110"))
            
            # Agregar atributos de usuario adicionales si hay documento disponible
            if self.doc:
                self._add_user_attributes_110mm_87(attr_list)
            
            # Crear AttributeSet con la lista de atributos
            attr_set_list = []
            attr_set_list.append(AllplanBaseElements.AttributeSet(attr_list))
            
            # Crear objeto Attributes
            attributes = AllplanBaseElements.Attributes(attr_set_list)
            
            # Asignar los atributos al elemento
            model_elem.SetAttributes(attributes)
            
            elems = [model_elem]
        else:
            # Variantes por tabla PARAMS (unión de polyhedra + rotación final)
            # tipo debe ser 0 o 1 en este punto
            elems = self._build_default_variant(tipo)
            
            # Asegurar que todos los elementos tengan atributos
            if elems:
                for elem in elems:
                    # Verificar si el elemento ya tiene atributos
                    try:
                        existing_attrs = elem.GetAttributes()
                        if existing_attrs is None or len(existing_attrs.GetAttributeSets()) == 0:
                            # Si no tiene atributos, asignar atributos por defecto según el tipo
                            attr_list = []
                            if tipo == 0:
                                # Custom attributes para 110mm 45°
                                attr_list.append(AllplanBaseElements.AttributeString(1083, "CS45ºØ110"))
                                attr_list.append(AllplanBaseElements.AttributeString(1084, "Ø110"))
                                attr_list.append(AllplanBaseElements.AttributeString(1085, ""))
                                attr_list.append(AllplanBaseElements.AttributeString(1086, ""))
                                attr_list.append(AllplanBaseElements.AttributeString(1087, ""))
                                attr_list.append(AllplanBaseElements.AttributeString(1895, ""))
                                attr_list.append(AllplanBaseElements.AttributeString(1896, "110"))
                                if self.doc:
                                    self._add_user_attributes_110mm_45(attr_list)
                            elif tipo == 1:
                                # Custom attributes para 40mm 45°
                                attr_list.append(AllplanBaseElements.AttributeString(1083, "CS45ºØ40"))
                                attr_list.append(AllplanBaseElements.AttributeString(1084, "40"))
                                attr_list.append(AllplanBaseElements.AttributeString(1085, ""))
                                attr_list.append(AllplanBaseElements.AttributeString(1086, ""))
                                attr_list.append(AllplanBaseElements.AttributeString(1087, ""))
                                attr_list.append(AllplanBaseElements.AttributeString(1895, ""))
                                attr_list.append(AllplanBaseElements.AttributeString(1896, "40"))
                            
                            if attr_list:
                                attr_set_list = []
                                attr_set_list.append(AllplanBaseElements.AttributeSet(attr_list))
                                attributes = AllplanBaseElements.Attributes(attr_set_list)
                                elem.SetAttributes(attributes)
                    except:
                        pass

        return CreateElementResult(elems)

    # ---------- Utilidades ----------
    def _props(self, color: int, pen: int = 1, stroke: int = 1, layer: int = None):
        if layer is None:
            layer = 1
        p = AllplanSettings.AllplanGlobalSettings.GetCurrentCommonProperties()
        p.Color = color
        p.ColorByLayer = False  # No afectar el color
        p.Pen = pen
        p.Stroke = stroke
        p.Layer = layer
        return p

    def _get_tipo_colze(self, default: int = 0) -> int:
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
            attr_pmp_carticulo_id = AllplanBaseElements.AttributeService.GetAttributeID(self.doc, "pmp_CARTICULO")
            attr_pmp_diametre_id = AllplanBaseElements.AttributeService.GetAttributeID(self.doc, "pmp_diametre")
            attr_pmp_nom_id = AllplanBaseElements.AttributeService.GetAttributeID(self.doc, "pmp_nom")
            attr_pmp_pes_unitari_id = AllplanBaseElements.AttributeService.GetAttributeID(self.doc, "pmp_pes_unitari")
            attr_pmp_seccio_id = AllplanBaseElements.AttributeService.GetAttributeID(self.doc, "pmp_seccio")

            # pmp_CARTICULO: "KN07_004_003"
            if attr_pmp_carticulo_id and attr_pmp_carticulo_id > 0:
                attr_list.append(AllplanBaseElements.AttributeString(attr_pmp_carticulo_id, "KN07_004_003"))

            # pmp_diametre: "110" (AttributeInt o AttributeString según el tipo)
            if attr_pmp_diametre_id and attr_pmp_diametre_id > 0:
                try:
                    attr_list.append(AllplanBaseElements.AttributeInt(attr_pmp_diametre_id, 110))
                except:
                    attr_list.append(AllplanBaseElements.AttributeString(attr_pmp_diametre_id, "110"))

            # pmp_nom: "CS45°Ø110"
            if attr_pmp_nom_id and attr_pmp_nom_id > 0:
                attr_list.append(AllplanBaseElements.AttributeString(attr_pmp_nom_id, "CS45°Ø110"))

            # pmp_pes_unitari: 0.2110 (AttributeDouble)
            if attr_pmp_pes_unitari_id and attr_pmp_pes_unitari_id > 0:
                attr_list.append(AllplanBaseElements.AttributeDouble(attr_pmp_pes_unitari_id, 0.2110))

            # pmp_seccio: "Ø110/45°" (AttributeString)
            if attr_pmp_seccio_id and attr_pmp_seccio_id > 0:
                attr_list.append(AllplanBaseElements.AttributeString(attr_pmp_seccio_id, "Ø110/45°"))

        except Exception as e:
            # No bloquear la creación si hay problemas con los atributos
            print(f"[Colze_rigid_004] Advertencia al agregar atributos de usuario 110mm 45°: {e}")

    def _add_user_attributes_40mm_87_elemento1(self, attr_list):
        """Agrega atributos de usuario para elemento 1 del codo 40mm 87°."""
        if not self.doc:
            return

        try:
            # Obtener IDs de atributos por nombre
            attr_pmp_carticulo_id = AllplanBaseElements.AttributeService.GetAttributeID(self.doc, "pmp_CARTICULO")
            attr_pmp_diametre_id = AllplanBaseElements.AttributeService.GetAttributeID(self.doc, "pmp_diametre")
            attr_pmp_nom_id = AllplanBaseElements.AttributeService.GetAttributeID(self.doc, "pmp_nom")
            attr_pmp_pes_unitari_id = AllplanBaseElements.AttributeService.GetAttributeID(self.doc, "pmp_pes_unitari")
            attr_pmp_seccio_id = AllplanBaseElements.AttributeService.GetAttributeID(self.doc, "pmp_seccio")

            # pmp_CARTICULO: "KN07_004_002"
            if attr_pmp_carticulo_id and attr_pmp_carticulo_id > 0:
                attr_list.append(AllplanBaseElements.AttributeString(attr_pmp_carticulo_id, "KN07_004_002"))

            # pmp_diametre: "40" (AttributeInt o AttributeString según el tipo)
            if attr_pmp_diametre_id and attr_pmp_diametre_id > 0:
                try:
                    attr_list.append(AllplanBaseElements.AttributeInt(attr_pmp_diametre_id, 40))
                except:
                    attr_list.append(AllplanBaseElements.AttributeString(attr_pmp_diametre_id, "40"))

            # pmp_nom: "CS87°Ø40"
            if attr_pmp_nom_id and attr_pmp_nom_id > 0:
                attr_list.append(AllplanBaseElements.AttributeString(attr_pmp_nom_id, "CS87°Ø40"))

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
            print(f"[Colze_rigid_004] Advertencia al agregar atributos de usuario elemento 1 (40mm 87°): {e}")

    def _add_user_attribute_pmp_tipus_hole(self, attr_list):
        """Agrega atributo de usuario pmp_tipus: Hole para elemento con layer 40057."""
        if not self.doc:
            return

        try:
            # Obtener ID de atributo por nombre
            attr_pmp_tipus_id = AllplanBaseElements.AttributeService.GetAttributeID(self.doc, "pmp_tipus")

            # pmp_tipus: "Hole"
            if attr_pmp_tipus_id and attr_pmp_tipus_id > 0:
                attr_list.append(AllplanBaseElements.AttributeString(attr_pmp_tipus_id, "Hole"))

        except Exception as e:
            # No bloquear la creación si hay problemas con los atributos
            print(f"[Colze_rigid_004] Advertencia al agregar atributo pmp_tipus: {e}")

    def _add_user_attributes_40mm_45_original(self, attr_list):
        """Agrega atributos de usuario para el objeto original del codo 40mm 45°."""
        if not self.doc:
            return

        try:
            # Obtener IDs de atributos por nombre
            attr_pmp_carticulo_id = AllplanBaseElements.AttributeService.GetAttributeID(self.doc, "pmp_CARTICULO")
            attr_pmp_diametre_id = AllplanBaseElements.AttributeService.GetAttributeID(self.doc, "pmp_diametre")
            attr_pmp_nom_id = AllplanBaseElements.AttributeService.GetAttributeID(self.doc, "pmp_nom")
            attr_pmp_pes_unitari_id = AllplanBaseElements.AttributeService.GetAttributeID(self.doc, "pmp_pes_unitari")
            attr_pmp_seccio_id = AllplanBaseElements.AttributeService.GetAttributeID(self.doc, "pmp_seccio")

            # pmp_CARTICULO: "KN07_004_001"
            if attr_pmp_carticulo_id and attr_pmp_carticulo_id > 0:
                attr_list.append(AllplanBaseElements.AttributeString(attr_pmp_carticulo_id, "KN07_004_001"))

            # pmp_diametre: "40" (AttributeInt o AttributeString según el tipo)
            if attr_pmp_diametre_id and attr_pmp_diametre_id > 0:
                try:
                    attr_list.append(AllplanBaseElements.AttributeInt(attr_pmp_diametre_id, 40))
                except:
                    attr_list.append(AllplanBaseElements.AttributeString(attr_pmp_diametre_id, "40"))

            # pmp_nom: "CS45°Ø40"
            if attr_pmp_nom_id and attr_pmp_nom_id > 0:
                attr_list.append(AllplanBaseElements.AttributeString(attr_pmp_nom_id, "CS45°Ø40"))

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
            print(f"[Colze_rigid_004] Advertencia al agregar atributos de usuario original 40mm 45°: {e}")

    def _add_user_attribute_material_cavitat(self, attr_list):
        """Agrega atributo de usuario MATERIAL: CAVITAT para elemento con layer 40054."""
        if not self.doc:
            return

        try:
            # Obtener ID de atributo por nombre
            attr_material_id = AllplanBaseElements.AttributeService.GetAttributeID(self.doc, "Material")

            # Material: "CAVITAT"
            if attr_material_id and attr_material_id > 0:
                attr_list.append(AllplanBaseElements.AttributeString(attr_material_id, "CAVITAT"))

        except Exception as e:
            # No bloquear la creación si hay problemas con los atributos
            print(f"[Colze_rigid_004] Advertencia al agregar atributo Material: {e}")

    @staticmethod
    def _crear_prisma_poly(diametro: float, largo: float):
        """Polyhedron: cuboide (para variantes default)."""
        return AllplanGeo.Polyhedron3D.CreateCuboid(
            AllplanGeo.Point3D(0, 0, 0),
            AllplanGeo.Point3D(diametro, diametro, largo)
        )

    @staticmethod
    def _crear_prisma(diametro: float, largo: float):
        """Polyhedron: cuboide (para 110mm 87°)."""
        return AllplanGeo.Polyhedron3D.CreateCuboid(
            AllplanGeo.Point3D(0, 0, 0),
            AllplanGeo.Point3D(diametro, diametro, largo)
        )

    # ---------- Variante especial: 40 mm · 87° (tres cuerpos) ----------
    def _build_40mm_87_especial(self):
        # --- Cuboide vertical ---
        DIAMETRO = 40.0
        LARGO_VERTICAL = 95.0

        # --- Cilindro inclinado ---
        LARGO_INCLINADA = 15.0
        ANGULO_INCLINADA = 87.0
        DESFASE_RAMAL = 30.0
        DIAMETRO_CILINDRO = 55.0

        # --- Anillo final ---
        LARGO_ANILLO = 30.0
        SOBRESALE_ANILLO = 10.0

        # Props diferenciadas con layers específicas
        # Elemento 1: conjunto unido (cubo0 + cubo_cilindrico + anillo) - layer 40061
        props_cubo_small = self._props(color=24, layer=40061)  # verde para el cuboide pequeño (40x40x95)
        # Elemento 2: cubo_adicional primera copia - layer 40055
        props_cubo_large_1 = self._props(color=7, layer=40055)   # azul para primera copia cuboide grande (50x50x95)
        # Elemento 3: cubo_adicional segunda copia - layer 40054
        props_cubo_large_2 = self._props(color=7, layer=40054)   # azul para segunda copia cuboide grande (50x50x95)
        # Elemento 4: cilindro - layer 40057
        props_cil  = self._props(color=28, layer=40057)        # naranja
        props_ring = self._props(color=24)        # verde (no se usa directamente, se une con cubo_small)

        # 1) Cuboide "vertical" (BRep con AxisPlacement)
        axis_cubo = AllplanGeo.AxisPlacement3D(
            AllplanGeo.Point3D(0, 0, 0),
            AllplanGeo.Vector3D(1, 0, 0),   # X
            AllplanGeo.Vector3D(0, 0, 1)    # Z
        )
        cubo0 = AllplanGeo.BRep3D.CreateCuboid(axis_cubo, DIAMETRO, DIAMETRO, LARGO_VERTICAL)

        # 1b) Cuboide adicional centrado sobre el original (50x50x95)
        offset_x = (DIAMETRO - 50.0) / 2.0
        offset_y = (DIAMETRO - 50.0) / 2.0
        axis_cubo2 = AllplanGeo.AxisPlacement3D(
            AllplanGeo.Point3D(offset_x, offset_y, 0),
            AllplanGeo.Vector3D(1, 0, 0),   # X
            AllplanGeo.Vector3D(0, 0, 1)    # Z
        )
        cubo_adicional = AllplanGeo.BRep3D.CreateCuboid(axis_cubo2, 50.0, 50.0, 95.0)

        # 2) Cilindro inclinado alrededor de eje paralelo a Y, pivotando desde el cuboide adicional
        # Posición ajustada para empezar desde el cuboide adicional (50x50) centrado
        base_pt = AllplanGeo.Point3D(offset_x + 50.0, offset_y + 25.0, LARGO_VERTICAL - DESFASE_RAMAL)
        eje_principal = AllplanGeo.Vector3D(0, 1, 0)  # Y
        eje_secundario = AllplanGeo.Vector3D(0, 0, 1) # Z
        eje_cil = AllplanGeo.AxisPlacement3D(base_pt, eje_principal, eje_secundario)
        cilindro = AllplanGeo.BRep3D.CreateCylinder(eje_cil, DIAMETRO_CILINDRO / 2.0, LARGO_INCLINADA)
        rot_axis = AllplanGeo.Line3D(
            base_pt.X, base_pt.Y, base_pt.Z,
            base_pt.X, base_pt.Y + 1.0, base_pt.Z
        )
        mrot = AllplanGeo.Matrix3D()
        mrot.SetRotation(rot_axis, AllplanGeo.Angle(math.radians(ANGULO_INCLINADA)))
        cilindro = AllplanGeo.Transform(cilindro, mrot)

        # 2b) Cuboide con tamaño del cilindro inclinado, centrado en la misma posición
        cubo_cilindrico = AllplanGeo.BRep3D.CreateCuboid(eje_cil, self.ANCHO_CUBO_CILINDRICO, self.ALTO_CUBO_CILINDRICO, self.LARGO_CUBO_CILINDRICO)
        cubo_cilindrico = AllplanGeo.Transform(cubo_cilindrico, mrot)

        # Aplicar rotación adicional al cuboide cilíndrico para que "caiga" en sintonía
        if abs(self.ROT_ADICIONAL_CUBO_CILINDRICO) > 1e-6:
            # Rotar alrededor del eje Y que pasa por el punto base
            rot_adicional_axis = AllplanGeo.Line3D(
                base_pt.X, base_pt.Y, base_pt.Z,
                base_pt.X, base_pt.Y + 1.0, base_pt.Z
            )
            mrot_adicional = AllplanGeo.Matrix3D()
            mrot_adicional.SetRotation(rot_adicional_axis, AllplanGeo.Angle(math.radians(self.ROT_ADICIONAL_CUBO_CILINDRICO)))
            cubo_cilindrico = AllplanGeo.Transform(cubo_cilindrico, mrot_adicional)

        # Aplicar desplazamiento hardcodeado al cuboide cilíndrico
        if abs(self.DESP_X_CUBO_CILINDRICO) > 1e-6 or abs(self.DESP_Y_CUBO_CILINDRICO) > 1e-6 or abs(self.DESP_Z_CUBO_CILINDRICO) > 1e-6:
            desp_matrix = AllplanGeo.Matrix3D()
            desp_matrix.SetTranslation(AllplanGeo.Vector3D(self.DESP_X_CUBO_CILINDRICO, self.DESP_Y_CUBO_CILINDRICO, self.DESP_Z_CUBO_CILINDRICO))
            cubo_cilindrico = AllplanGeo.Transform(cubo_cilindrico, desp_matrix)

        # 3) Anillo al final del ramal inclinado (como cuboide BRep)
        # Posicionado al final del cilindro que ahora comienza desde el cuboide adicional
        base_side = DIAMETRO + 2 * SOBRESALE_ANILLO
        z_inicio = LARGO_VERTICAL - DESFASE_RAMAL
        axis_ring = AllplanGeo.AxisPlacement3D(
            AllplanGeo.Point3D(
                offset_x + 50.0 + LARGO_INCLINADA,
                offset_y + 25.0 - base_side / 2.0,
                z_inicio - base_side / 2.0
            ),
            AllplanGeo.Vector3D(1, 0, 0),  # X
            AllplanGeo.Vector3D(0, 0, 1)   # Z
        )
        anillo = AllplanGeo.BRep3D.CreateCuboid(axis_ring, LARGO_ANILLO, base_side, base_side)

        # Centroide aproximado del conjunto (ajustable si lo necesitas)
        cx = DIAMETRO / 2.0 + LARGO_INCLINADA / 2.0
        cy = DIAMETRO / 2.0
        cz = LARGO_VERTICAL / 2.0

        # Rotar cada sólido si alguna rotación está activa
        angles = [self.ROT_X_L3000_D87, self.ROT_Y_L3000_D87, self.ROT_Z_L3000_D87]
        axes = ['x', 'y', 'z']
        def rotar_solido(solido):
            for angle, axis in zip(angles, axes):
                if abs(angle) > 1e-6:
                    mat = AllplanGeo.Matrix3D()
                    if axis == 'x':
                        axis_line = AllplanGeo.Line3D(cx, cy, cz, cx + 1.0, cy, cz)
                    elif axis == 'y':
                        axis_line = AllplanGeo.Line3D(cx, cy, cz, cx, cy + 1.0, cz)
                    else:
                        axis_line = AllplanGeo.Line3D(cx, cy, cz, cx, cy, cz + 1.0)
                    mat.SetRotation(axis_line, AllplanGeo.Angle(math.radians(angle)))
                    solido = AllplanGeo.Transform(solido, mat)
            return solido

        cubo0 = rotar_solido(cubo0)
        cubo_adicional = rotar_solido(cubo_adicional)
        cilindro = rotar_solido(cilindro)
        cubo_cilindrico = rotar_solido(cubo_cilindrico)
        anillo = rotar_solido(anillo)

        # Unir cubo0 + cubo_cilindrico + anillo en un solo elemento
        err, conjunto_unido = AllplanGeo.MakeUnion(cubo0, cubo_cilindrico)
        if err == 0 and conjunto_unido.IsValid():
            err, conjunto_unido = AllplanGeo.MakeUnion(conjunto_unido, anillo)

        # Si la unión falló, usar lista de geometrías
        if err != 0 or not conjunto_unido.IsValid():
            print("Advertencia: No se pudo unir los elementos, usando lista de geometrías")
            conjunto_unido = [cubo0, cubo_cilindrico, anillo]

        # Crear ModelElement3D para el conjunto unido con atributos personalizados
        model_elem_conjunto = AllplanBasisElements.ModelElement3D(props_cubo_small, conjunto_unido)

        # Añadir atributos personalizados al conjunto unido (Elemento 1)
        attr_list_conjunto = []
        # Custom attribute 01: CS87ºØ40
        attr_list_conjunto.append(AllplanBaseElements.AttributeString(1083, "CS87ºØ40"))
        # Custom attribute 02: Ø40
        attr_list_conjunto.append(AllplanBaseElements.AttributeString(1084, "Ø40"))
        # Custom attribute 03-06: undefined (vacíos)
        attr_list_conjunto.append(AllplanBaseElements.AttributeString(1085, ""))
        attr_list_conjunto.append(AllplanBaseElements.AttributeString(1086, ""))
        attr_list_conjunto.append(AllplanBaseElements.AttributeString(1087, ""))
        attr_list_conjunto.append(AllplanBaseElements.AttributeString(1895, ""))
        # Custom attribute 07: 40
        attr_list_conjunto.append(AllplanBaseElements.AttributeString(1896, "40"))
        
        # Agregar atributos de usuario adicionales si hay documento disponible
        if self.doc:
            self._add_user_attributes_40mm_87_elemento1(attr_list_conjunto)

        # Crear AttributeSet con la lista de atributos
        attr_set_list_conjunto = []
        attr_set_list_conjunto.append(AllplanBaseElements.AttributeSet(attr_list_conjunto))

        # Crear objeto Attributes
        attributes_conjunto = AllplanBaseElements.Attributes(attr_set_list_conjunto)

        # Asignar los atributos al elemento
        model_elem_conjunto.SetAttributes(attributes_conjunto)

        # Crear ModelElement3D para cilindro con atributos personalizados
        model_elem_cilindro = AllplanBasisElements.ModelElement3D(props_cil, cilindro)

        # Añadir atributos personalizados al cilindro (Elemento 4 - layer 40057)
        attr_list = []
        # Custom attribute 01-04: undefined (vacíos)
        attr_list.append(AllplanBaseElements.AttributeString(1083, ""))
        attr_list.append(AllplanBaseElements.AttributeString(1084, ""))
        attr_list.append(AllplanBaseElements.AttributeString(1085, ""))
        attr_list.append(AllplanBaseElements.AttributeString(1086, ""))
        # Custom attribute 05:""
        attr_list.append(AllplanBaseElements.AttributeString(1087, ""))
        
        # Agregar atributo de usuario pmp_tipus: "Hole" si hay documento disponible
        if self.doc:
            self._add_user_attribute_pmp_tipus_hole(attr_list)

        # Crear AttributeSet con la lista de atributos
        attr_set_list = []
        attr_set_list.append(AllplanBaseElements.AttributeSet(attr_list))

        # Crear objeto Attributes
        attributes = AllplanBaseElements.Attributes(attr_set_list)

        # Asignar los atributos al elemento
        model_elem_cilindro.SetAttributes(attributes)

        # Crear Elemento 3 (segunda copia del cubo_adicional) con atributo MATERIAL: CAVITAT
        elem3 = AllplanBasisElements.ModelElement3D(props_cubo_large_2, cubo_adicional)
        if self.doc:
            attr_list_elem3 = []
            self._add_user_attribute_material_cavitat(attr_list_elem3)
            if attr_list_elem3:
                attr_set_elem3 = AllplanBaseElements.AttributeSet(attr_list_elem3)
                attributes_elem3 = AllplanBaseElements.Attributes([attr_set_elem3])
                elem3.SetAttributes(attributes_elem3)

        return [
            model_elem_conjunto,  # Elemento 1: conjunto unido: cubo0 + cubo_cilindrico + anillo (color 24, layer 40061)
            AllplanBasisElements.ModelElement3D(props_cubo_large_1, cubo_adicional),  # Elemento 2: primera copia (layer 40055)
            elem3,  # Elemento 3: segunda copia (layer 40054) con MATERIAL: CAVITAT
            model_elem_cilindro,  # Elemento 4: cilindro (layer 40057) con pmp_tipus: Hole
        ]

    # ---------- Variante 110mm 87° (idéntico al tipo 6 de Colze_rigidSane_004.py) ----------
    def _build_110mm_87(self, variant: int):
        """110mm 87° (idéntico al tipo 6 de Colze_rigidSane_004.py)."""
        DIAMETRO = 110.0
        LARGO_VERTICAL = 110.0
        LARGO_INCLINADA = 110.0
        LARGO_HORIZONTAL = 110.0
        ANGULO_INCLINADA = 45.0
        ANGULO_HORIZONTAL = 90.0
        LARGO_ANILLO = 75.0
        SOBRESALE_ANILLO = 10.0

        props = self._props(color=24, layer=self.LAYER_KN_AIGUA)

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

        # Aplicar rotaciones hardcodeadas sobre el propio eje para variant==6 (TipoColze==3)
        if variant == 6:
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

    def _add_user_attributes_110mm_87(self, attr_list):
        """Agrega atributos de usuario para codo 110mm 87° (exactos de la imagen)."""
        if not self.doc:
            return

        try:
            # Obtener IDs de atributos por nombre
            attr_pmp_carticulo_id = AllplanBaseElements.AttributeService.GetAttributeID(self.doc, "pmp_CARTICULO")
            attr_pmp_diametre_id = AllplanBaseElements.AttributeService.GetAttributeID(self.doc, "pmp_diametre")
            attr_pmp_nom_id = AllplanBaseElements.AttributeService.GetAttributeID(self.doc, "pmp_nom")
            attr_pmp_pes_unitari_id = AllplanBaseElements.AttributeService.GetAttributeID(self.doc, "pmp_pes_unitari")
            attr_pmp_seccio_id = AllplanBaseElements.AttributeService.GetAttributeID(self.doc, "pmp_seccio")

            # pmp_CARTICULO: "KN07_004_004"
            if attr_pmp_carticulo_id and attr_pmp_carticulo_id > 0:
                attr_list.append(AllplanBaseElements.AttributeString(attr_pmp_carticulo_id, "KN07_004_004"))

            # pmp_diametre: "110"
            if attr_pmp_diametre_id and attr_pmp_diametre_id > 0:
                try:
                    attr_list.append(AllplanBaseElements.AttributeInt(attr_pmp_diametre_id, 110))
                except:
                    attr_list.append(AllplanBaseElements.AttributeString(attr_pmp_diametre_id, "110"))

            # pmp_nom: "CS87°Ø110" (exacto de la imagen)
            if attr_pmp_nom_id and attr_pmp_nom_id > 0:
                attr_list.append(AllplanBaseElements.AttributeString(attr_pmp_nom_id, "CS87°Ø110"))

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
            print(f"[Colze_rigid_004] Advertencia al agregar atributos de usuario 110mm 87°: {e}")

    # ---------- Variantes por tabla PARAMS ----------
    def _build_default_variant(self, tipo: int):
        """Construye la variante por PARAMS (un sólido unido) y rota Y=270° al final."""
        idx = tipo if 0 <= tipo < len(self.PARAMS) else 0
        p = self.PARAMS[idx]

        # Para Tipo 0 (L1000_D110 - 45° 110mm), usar layer kn_aigua
        if tipo == 0:
            props = self._props(color=24, layer=self.LAYER_KN_AIGUA)
        else:
            props = self._props(color=24)
        cubo0 = self._crear_prisma_poly(p['DIAMETRO'], p['LARGO_VERTICAL'])

        # Tramo inclinado
        rad_incl = math.radians(p['ANGULO_INCLINADA'])
        cubo1 = self._crear_prisma_poly(p['DIAMETRO'], p['LARGO_INCLINADA'])
        m1 = AllplanGeo.Matrix3D(); m1.SetRotation(AllplanGeo.Line3D(0, 0, 0, 1, 0, 0), AllplanGeo.Angle(-rad_incl))
        cubo1 = AllplanGeo.Transform(cubo1, m1)
        t1 = AllplanGeo.Matrix3D(); t1.SetTranslation(AllplanGeo.Vector3D(0, 0, p['LARGO_VERTICAL']))
        cubo1 = AllplanGeo.Transform(cubo1, t1)

        dz = p['LARGO_INCLINADA'] * math.cos(rad_incl)
        dy = p['LARGO_INCLINADA'] * math.sin(rad_incl)

        # Tramo horizontal
        rad_h = math.radians(p['ANGULO_HORIZONTAL'])
        cubo2 = self._crear_prisma_poly(p['DIAMETRO'], p['LARGO_HORIZONTAL'])
        m2 = AllplanGeo.Matrix3D(); m2.SetRotation(AllplanGeo.Line3D(0, 0, 0, 1, 0, 0), AllplanGeo.Angle(-rad_h))
        cubo2 = AllplanGeo.Transform(cubo2, m2)
        t2 = AllplanGeo.Matrix3D(); t2.SetTranslation(AllplanGeo.Vector3D(0, dy, p['LARGO_VERTICAL'] + dz))
        cubo2 = AllplanGeo.Transform(cubo2, t2)

        # Anillo en el origen (coordenadas negativas en Z)
        anillo = AllplanGeo.Polyhedron3D.CreateCuboid(
            AllplanGeo.Point3D(-p['SOBRESALE_ANILLO'], -p['SOBRESALE_ANILLO'], -p['LARGO_ANILLO']),
            AllplanGeo.Point3D(p['DIAMETRO'] + p['SOBRESALE_ANILLO'], p['DIAMETRO'] + p['SOBRESALE_ANILLO'], 0)
        )

        # Unión
        err, codo = AllplanGeo.MakeUnion(cubo0, cubo1)
        if err == 0 and codo.IsValid(): err, codo = AllplanGeo.MakeUnion(codo, cubo2)
        if err == 0 and codo.IsValid(): err, codo = AllplanGeo.MakeUnion(codo, anillo)
        if err != 0 or not codo.IsValid():
            print("Error al crear el codo Polyhedron")
            return []

        # Rotación hardcodeada para L1000_D110 (TipoColze==0)
        if tipo == 0:
            cx = p['DIAMETRO'] / 2.0
            cy = p['DIAMETRO'] / 2.0
            cz = (p['LARGO_VERTICAL'] + p['LARGO_INCLINADA'] + p['LARGO_HORIZONTAL']) / 2.0
            for angle, axis in zip([
                self.ROT_X_L1000_D110,
                self.ROT_Y_L1000_D110,
                self.ROT_Z_L1000_D110
            ], ['x', 'y', 'z']):
                if abs(angle) > 1e-6:
                    mat = AllplanGeo.Matrix3D()
                    if axis == 'x':
                        axis_line = AllplanGeo.Line3D(cx, cy, cz, cx + 1.0, cy, cz)
                    elif axis == 'y':
                        axis_line = AllplanGeo.Line3D(cx, cy, cz, cx, cy + 1.0, cz)
                    else:
                        axis_line = AllplanGeo.Line3D(cx, cy, cz, cx, cy, cz + 1.0)
                    mat.SetRotation(axis_line, AllplanGeo.Angle(math.radians(angle)))
                    codo = AllplanGeo.Transform(codo, mat)

        # Rotación hardcodeada para L3000_D45 (TipoColze==1)
        if tipo == 1:
            cx = p['DIAMETRO'] / 2.0
            cy = p['DIAMETRO'] / 2.0
            cz = (p['LARGO_VERTICAL'] + p['LARGO_INCLINADA'] + p['LARGO_HORIZONTAL']) / 2.0
            for angle, axis in zip([
                self.ROT_X_L3000_D45,
                self.ROT_Y_L3000_D45,
                self.ROT_Z_L3000_D45
            ], ['x', 'y', 'z']):
                if abs(angle) > 1e-6:
                    mat = AllplanGeo.Matrix3D()
                    if axis == 'x':
                        axis_line = AllplanGeo.Line3D(cx, cy, cz, cx + 1.0, cy, cz)
                    elif axis == 'y':
                        axis_line = AllplanGeo.Line3D(cx, cy, cz, cx, cy + 1.0, cz)
                    else:
                        axis_line = AllplanGeo.Line3D(cx, cy, cz, cx, cy, cz + 1.0)
                    mat.SetRotation(axis_line, AllplanGeo.Angle(math.radians(angle)))
                    codo = AllplanGeo.Transform(codo, mat)

        # Rotación final Y = 270°
        eje_y = AllplanGeo.Axis3D(AllplanGeo.Point3D(0, 0, 0), AllplanGeo.Vector3D(0, 1, 0))
        codo_rotado = AllplanGeo.Rotate(codo, eje_y, AllplanGeo.Angle(math.radians(270)))

        # Crear ModelElement3D
        model_elem = AllplanBasisElements.ModelElement3D(props, codo_rotado)

        # Añadir atributos personalizados para Tipo 0 (L1000_D110)
        if tipo == 0:
            attr_list = []
            # Custom attribute 01: CS45ºØ110
            attr_list.append(AllplanBaseElements.AttributeString(1083, "CS45ºØ110"))
            # Custom attribute 02: Ø110
            attr_list.append(AllplanBaseElements.AttributeString(1084, "Ø110"))
            # Custom attribute 03-06: undefined (vacíos)
            attr_list.append(AllplanBaseElements.AttributeString(1085, ""))
            attr_list.append(AllplanBaseElements.AttributeString(1086, ""))
            attr_list.append(AllplanBaseElements.AttributeString(1087, ""))
            attr_list.append(AllplanBaseElements.AttributeString(1895, ""))
            # Custom attribute 07: 110
            attr_list.append(AllplanBaseElements.AttributeString(1896, "110"))
            
            # Agregar atributos de usuario adicionales si hay documento disponible
            if self.doc:
                self._add_user_attributes_110mm_45(attr_list)

            # Crear AttributeSet con la lista de atributos
            attr_set_list = []
            attr_set_list.append(AllplanBaseElements.AttributeSet(attr_list))

            # Crear objeto Attributes
            attributes = AllplanBaseElements.Attributes(attr_set_list)

            # Asignar los atributos al elemento
            model_elem.SetAttributes(attributes)

        # Si es L3000_D45 (TipoColze==1), crear 3 copias idénticas
        if tipo == 1:
            # Crear 3 copias con atributos personalizados y layers específicas
            elementos = []
            for i in range(3):
                # Asignar layer y color según el índice
                if i == 0:
                    # Original: layer kn_aigua (40061), color 24
                    props_elem = self._props(color=24, layer=self.LAYER_KN_AIGUA)
                elif i == 1:
                    # Copia 1: layer 40055, color 7
                    props_elem = self._props(color=7, layer=self.LAYER_40055)
                else:  # i == 2
                    # Copia 2: layer 40054, color 7
                    props_elem = self._props(color=7, layer=self.LAYER_40054)
                
                elem = AllplanBasisElements.ModelElement3D(props_elem, codo_rotado)

                # Añadir atributos personalizados
                attr_list = []
                # Custom attribute 01: CS45ºØ40
                attr_list.append(AllplanBaseElements.AttributeString(1083, "CS45ºØ40"))
                # Custom attribute 02: 40
                attr_list.append(AllplanBaseElements.AttributeString(1084, "40"))
                # Custom attribute 03-06: undefined (vacíos)
                attr_list.append(AllplanBaseElements.AttributeString(1085, ""))
                attr_list.append(AllplanBaseElements.AttributeString(1086, ""))
                attr_list.append(AllplanBaseElements.AttributeString(1087, ""))
                attr_list.append(AllplanBaseElements.AttributeString(1895, ""))
                # Custom attribute 07: 40
                attr_list.append(AllplanBaseElements.AttributeString(1896, "40"))
                
                # Agregar atributos de usuario al original (i==0)
                if i == 0 and self.doc:
                    self._add_user_attributes_40mm_45_original(attr_list)
                
                # Agregar atributo MATERIAL: CAVITAT a la copia 2 (i==2)
                if i == 2 and self.doc:
                    self._add_user_attribute_material_cavitat(attr_list)

                # Crear AttributeSet con la lista de atributos
                attr_set_list = []
                attr_set_list.append(AllplanBaseElements.AttributeSet(attr_list))

                # Crear objeto Attributes
                attributes = AllplanBaseElements.Attributes(attr_set_list)

                # Asignar los atributos al elemento
                elem.SetAttributes(attributes)

                elementos.append(elem)

            return elementos
        else:
            return [model_elem]


# ===== Punto de entrada PythonPart =====
def create_element(build_ele, _doc) -> CreateElementResult:
    """Instancia la clase y delega la creación del elemento."""
    return CodoRigido(build_ele, _doc).create_result()
