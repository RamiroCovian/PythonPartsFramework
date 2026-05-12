# -*- coding: utf-8 -*-
"""Manguito """


import math
import NemAll_Python_Geometry as AllplanGeo
import NemAll_Python_AllplanSettings as AllplanSettings
import NemAll_Python_BasisElements as AllplanBasisElements
import NemAll_Python_BaseElements as AllplanBaseElements

from CreateElementResult import CreateElementResult


# ===== Requisito estándar =====
def check_allplan_version(_build_ele, _version) -> bool:
    """Check the current Allplan version (se soportan todas las versiones)."""
    return True
# ==============================




class Manguito:
    """Crea un manguito rectangular fijo (DIAMETRO × ANCHO × LARGO)."""

    DIAMETRO = 40.0   # mm (lado Z)
    ANCHO    = 32.5   # mm (lado Y, hardcodeado)
    LARGO    = 70.0   # mm (eje X)
    COLOR    = 65     # Verde claro (opcional)
    COLOR_COPIA = 5   # Color para las copias
    LAYER    = 40148  # IS_CON_SANE_FAB (is cone fab)

    def __init__(self, _build_ele=None, doc=None, rot_x=0.0, rot_y=0.0, rot_z=0.0):
        self.build_ele = _build_ele
        self.doc = doc
        self.rot_x = rot_x
        self.rot_y = rot_y
        self.rot_z = rot_z

    def create_result(self) -> CreateElementResult:
        """Construye tres copias del manguito y devuelve CreateElementResult."""
        elementos = []
        axis = AllplanGeo.AxisPlacement3D(AllplanGeo.Point3D(0, 0, 0))
        for i in range(3):
            props = AllplanSettings.AllplanGlobalSettings.GetCurrentCommonProperties()
            props.Color = self.COLOR if i == 0 else self.COLOR_COPIA
            props.ColorByLayer = False  # Permitir modificar el color independientemente de la layer
            props.Layer = self.LAYER  # IS_CON_SANE_FAB (is cone fab)
            diametro = self.DIAMETRO - 7.50 if i == 0 else self.DIAMETRO
            solido = AllplanGeo.BRep3D.CreateCuboid(axis, self.LARGO, self.ANCHO, diametro)
            # Rotación sobre sí mismo
            if self.rot_x != 0.0:
                rot_x_mat = AllplanGeo.Matrix3D()
                rot_x_mat.SetRotation(AllplanGeo.Line3D(0,0,0,1,0,0), AllplanGeo.Angle(math.radians(self.rot_x)))
                solido = AllplanGeo.Transform(solido, rot_x_mat)
            if self.rot_y != 0.0:
                rot_y_mat = AllplanGeo.Matrix3D()
                rot_y_mat.SetRotation(AllplanGeo.Line3D(0,0,0,0,1,0), AllplanGeo.Angle(math.radians(self.rot_y)))
                solido = AllplanGeo.Transform(solido, rot_y_mat)
            if self.rot_z != 0.0:
                rot_z_mat = AllplanGeo.Matrix3D()
                rot_z_mat.SetRotation(AllplanGeo.Line3D(0,0,0,0,0,1), AllplanGeo.Angle(math.radians(self.rot_z)))
                solido = AllplanGeo.Transform(solido, rot_z_mat)

            model_elem = AllplanBasisElements.ModelElement3D(props, solido)

            # Agregar atributos personalizados
            if i == 0:
                # Atributos del original según la foto
                attr_list = []
                attr_list.append(AllplanBaseElements.AttributeString(1083, "MØ25"))  # Custom attribute 01
                attr_list.append(AllplanBaseElements.AttributeString(1084, "Ø25"))   # Custom attribute 02
                attr_list.append(AllplanBaseElements.AttributeString(1085, ""))      # Custom attribute 03
                attr_list.append(AllplanBaseElements.AttributeString(1086, ""))      # Custom attribute 04
                attr_list.append(AllplanBaseElements.AttributeString(1087, ""))      # Custom attribute 05
                attr_list.append(AllplanBaseElements.AttributeString(1895, ""))      # Custom attribute 06
                attr_list.append(AllplanBaseElements.AttributeString(1896, "25"))    # Custom attribute 07
                attr_list.append(AllplanBaseElements.AttributeString(1897, ""))      # Custom attribute 08
                attr_list.append(AllplanBaseElements.AttributeString(1898, "625"))   # Custom attribute 09
                attr_list.append(AllplanBaseElements.AttributeString(1899, ""))      # Custom attribute 10
                attr_list.append(AllplanBaseElements.AttributeString(1900, ""))      # Custom attribute 11
                attr_list.append(AllplanBaseElements.AttributeString(1901, ""))      # Custom attribute 12
                attr_list.append(AllplanBaseElements.AttributeString(1902, ""))      # Custom attribute 13
                attr_list.append(AllplanBaseElements.AttributeString(1903, ""))      # Custom attribute 14
                attr_list.append(AllplanBaseElements.AttributeString(1904, ""))      # Custom attribute 15

                # Agregar atributos de usuario adicionales si hay documento disponible
                if self.doc:
                    self._add_user_attributes(attr_list)

                attr_set = AllplanBaseElements.AttributeSet(attr_list)
                attributes = AllplanBaseElements.Attributes([attr_set])
                model_elem.SetAttributes(attributes)
            else:
                # Agregar atributos a las copias (idx 1 y 2)
                if self.doc:
                    attr_list = []
                    self._add_copy_attributes(attr_list, i)
                    
                    if attr_list:
                        attr_set = AllplanBaseElements.AttributeSet(attr_list)
                        attributes = AllplanBaseElements.Attributes([attr_set])
                        model_elem.SetAttributes(attributes)

            elementos.append(model_elem)
        return CreateElementResult(elementos)

    def _add_user_attributes(self, attr_list):
        """Agrega atributos de usuario adicionales obteniendo sus IDs por nombre."""
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

            # pmp_CARTICULO: "KN07_003_001"
            if attr_pmp_carticulo_id and attr_pmp_carticulo_id > 0:
                attr_list.append(AllplanBaseElements.AttributeString(attr_pmp_carticulo_id, "KN07_003_001"))

            # pmp_nom: "MØ25"
            if attr_pmp_nom_id and attr_pmp_nom_id > 0:
                attr_list.append(AllplanBaseElements.AttributeString(attr_pmp_nom_id, "MØ25"))

            # pmp_pes_unitari: 0.0155 (AttributeDouble)
            if attr_pmp_pes_unitari_id and attr_pmp_pes_unitari_id > 0:
                attr_list.append(AllplanBaseElements.AttributeDouble(attr_pmp_pes_unitari_id, 0.0155))

            # pmp_seccio: 25 (AttributeInt o AttributeString según el tipo)
            if attr_pmp_seccio_id and attr_pmp_seccio_id > 0:
                try:
                    attr_list.append(AllplanBaseElements.AttributeInt(attr_pmp_seccio_id, 25))
                except:
                    attr_list.append(AllplanBaseElements.AttributeString(attr_pmp_seccio_id, "25"))

        except Exception as e:
            # No bloquear la creación si hay problemas con los atributos
            print(f"[ManguitoBasic_003] Advertencia al agregar atributos de usuario: {e}")

    def _add_copy_attributes(self, attr_list, idx):
        """Agrega atributos a las copias según el índice.
        
        Args:
            attr_list: Lista de atributos donde agregar
            idx: Índice de la copia (1 o 2)
        """
        if not self.doc:
            return

        try:
            # Obtener ID de 6_CC_IS (siempre necesario para copias)
            attr_6_cc_is_id = AllplanBaseElements.AttributeService.GetAttributeID(self.doc, "6_CC_IS")
            
            if attr_6_cc_is_id and attr_6_cc_is_id > 0:
                attr_list.append(AllplanBaseElements.AttributeString(attr_6_cc_is_id, ""))

            # Para la primera copia (idx == 1), agregar Material = CAVITAT
            if idx == 1:
                attr_material_id = AllplanBaseElements.AttributeService.GetAttributeID(self.doc, "Material")
                if attr_material_id and attr_material_id > 0:
                    attr_list.append(AllplanBaseElements.AttributeString(attr_material_id, "CAVITAT"))

        except Exception as e:
            # No bloquear la creación si hay problemas con los atributos
            print(f"[ManguitoBasic_003] Advertencia al agregar atributos a copia {idx}: {e}")


# ===== Punto de entrada PythonPart =====
def create_element(build_ele, _doc, rot_x=0.0, rot_y=180.0, rot_z=0.0) -> CreateElementResult:
    return Manguito(build_ele, _doc, rot_x, rot_y, rot_z).create_result()
