# -*- coding: utf-8 -*-
"""Tubo PVC fecal Ø25 (básico, sección rectangular fija)."""


import math
import NemAll_Python_Geometry as AllplanGeo
import NemAll_Python_AllplanSettings as AllplanSettings
import NemAll_Python_BasisElements as AllplanBasisElements
import NemAll_Python_BaseElements as AllplanBaseElements

from CreateElementResult import CreateElementResult
from BuildingElement import BuildingElement
from BaseScriptObject import BaseScriptObject, BaseScriptObjectData

# ===== Requisito del usuario: función estándar =====
def check_allplan_version(_build_ele, _version) -> bool:
    """Check the current Allplan version

    Args:
        _build_ele: building element with the parameter properties
        _version:   the current Allplan version

    Returns:
        True
    """
    # Soporta todas las versiones
    return True
# ================================================


class TuboPVCBasico:
    """Crea un tubo PVC rectangular fijo (25 mm × 25 mm × 70 mm)."""

    # Parámetros por defecto (idénticos a tu script)
    DIAMETRO = 25.0   # mm (alto del cuboide)
    ANCHO    = 40.0   # mm (ancho del cuboide, hardcodeado)
    LARGO    = 70.0   # mm (eje X) - equivalente a 0.07000 m
    COLOR    = 66     # Verde claro (opcional)
    COLOR_COPIA = 5   # Color para las copias
    LAYER    = 40148  # IS_CON_SANE_FAB (is cone fab)

    def __init__(self, _build_ele=None, doc=None, rot_x=0.0, rot_y=0.0, rot_z=0.0):
        # Guardamos por si en el futuro leés valores desde la paleta.
        self.build_ele = _build_ele
        self.doc = doc
        self.rot_x = rot_x
        self.rot_y = rot_y
        self.rot_z = rot_z

    def create_result(self) -> CreateElementResult:
        """Construye tres copias del tubo y devuelve CreateElementResult."""
        elementos = []
        base_y = self.DIAMETRO
        axis = AllplanGeo.AxisPlacement3D(AllplanGeo.Point3D(0, 0, 0))
        print(
            f"[F25][SCRIPT] build start L={self.LARGO} base_y={base_y} ANCHO={self.ANCHO} "
            f"rot=({self.rot_x},{self.rot_y},{self.rot_z})"
        )
        for i in range(3):
            props = AllplanSettings.AllplanGlobalSettings.GetCurrentCommonProperties()
            props.Color = self.COLOR if i == 0 else self.COLOR_COPIA
            props.ColorByLayer = False  # Permitir modificar el color independientemente de la layer
            props.Layer = self.LAYER  # IS_CON_SANE_FAB (is cone fab)
            ancho_copia = self.ANCHO - 15.0 if i == 0 else self.ANCHO
            tag = "original" if i == 0 else f"copia_{i}"
            print(
                f"[F25][SCRIPT] {tag}: dims=({self.LARGO},{base_y},{ancho_copia}) "
                f"layer={props.Layer} color={props.Color}"
            )
            tubo = AllplanGeo.BRep3D.CreateCuboid(axis, self.LARGO, base_y, ancho_copia)
            # Rotación sobre sí mismo (igual que en Colze_basic_001.py)
            if self.rot_x != 0.0:
                rot_x_mat = AllplanGeo.Matrix3D()
                rot_x_mat.SetRotation(AllplanGeo.Line3D(0,0,0,1,0,0), AllplanGeo.Angle(math.radians(self.rot_x)))
                tubo = AllplanGeo.Transform(tubo, rot_x_mat)
            if self.rot_y != 0.0:
                rot_y_mat = AllplanGeo.Matrix3D()
                rot_y_mat.SetRotation(AllplanGeo.Line3D(0,0,0,0,1,0), AllplanGeo.Angle(math.radians(self.rot_y)))
                tubo = AllplanGeo.Transform(tubo, rot_y_mat)
            if self.rot_z != 0.0:
                rot_z_mat = AllplanGeo.Matrix3D()
                rot_z_mat.SetRotation(AllplanGeo.Line3D(0,0,0,0,0,1), AllplanGeo.Angle(math.radians(self.rot_z)))
                tubo = AllplanGeo.Transform(tubo, rot_z_mat)

            # Crear ModelElement3D
            tube_element = AllplanBasisElements.ModelElement3D(props, tubo)

            # Agregar atributos personalizados
            if i == 0:
                # Atributos del original según la foto
                attr_list = []
                attr_list.append(AllplanBaseElements.AttributeString(1083, "TS-25"))
                attr_list.append(AllplanBaseElements.AttributeString(1084, "Ø25"))
                attr_list.append(AllplanBaseElements.AttributeString(1085, ""))
                attr_list.append(AllplanBaseElements.AttributeString(1086, ""))
                attr_list.append(AllplanBaseElements.AttributeString(1087, ""))
                attr_list.append(AllplanBaseElements.AttributeString(1895, ""))
                attr_list.append(AllplanBaseElements.AttributeString(1896, "25"))
                attr_list.append(AllplanBaseElements.AttributeString(1897, "625"))
                attr_list.append(AllplanBaseElements.AttributeString(1898, ""))

                # Agregar atributos de usuario adicionales si hay documento disponible
                if self.doc:
                    self._add_user_attributes(attr_list)

                attr_set_list = []
                attr_set_list.append(AllplanBaseElements.AttributeSet(attr_list))
                attributes = AllplanBaseElements.Attributes(attr_set_list)
                tube_element.SetAttributes(attributes)
            else:
                # Agregar atributos a las copias (idx 1 y 2)
                if self.doc:
                    attr_list = []
                    self._add_copy_attributes(attr_list, i)

                    if attr_list:
                        attr_set_list = []
                        attr_set_list.append(AllplanBaseElements.AttributeSet(attr_list))
                        attributes = AllplanBaseElements.Attributes(attr_set_list)
                        tube_element.SetAttributes(attributes)

            elementos.append(tube_element)
        print(f"[F25][SCRIPT] build end -> elementos={len(elementos)}")
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
            attr_pmp_area_id = AllplanBaseElements.AttributeService.GetAttributeID(self.doc, "pmp_area")
            attr_pmp_densitat_lineal_id = AllplanBaseElements.AttributeService.GetAttributeID(self.doc, "pmp_densitat_lineal")
            attr_pmp_diametre_id = AllplanBaseElements.AttributeService.GetAttributeID(self.doc, "pmp_diametre")
            attr_pmp_seccio_id = AllplanBaseElements.AttributeService.GetAttributeID(self.doc, "pmp_seccio")

            # 6_CC_IS: "IS"
            if attr_6_cc_is_id and attr_6_cc_is_id > 0:
                attr_list.append(AllplanBaseElements.AttributeString(attr_6_cc_is_id, ""))

            # pmp_CARTICULO: "KN07_002_001"
            if attr_pmp_carticulo_id and attr_pmp_carticulo_id > 0:
                attr_list.append(AllplanBaseElements.AttributeString(attr_pmp_carticulo_id, "KN07_002_001"))

            # pmp_nom: "TS-25"
            if attr_pmp_nom_id and attr_pmp_nom_id > 0:
                attr_list.append(AllplanBaseElements.AttributeString(attr_pmp_nom_id, "TS-25"))

            # pmp_area: 625.000000 (AttributeDouble)
            if attr_pmp_area_id and attr_pmp_area_id > 0:
                attr_list.append(AllplanBaseElements.AttributeDouble(attr_pmp_area_id, 625.000000))

            # pmp_densitat_lineal: 0.2225 (AttributeDouble)
            if attr_pmp_densitat_lineal_id and attr_pmp_densitat_lineal_id > 0:
                attr_list.append(AllplanBaseElements.AttributeDouble(attr_pmp_densitat_lineal_id, 0.2225))

            # pmp_diametre: 25 (AttributeInt o AttributeString según el tipo)
            if attr_pmp_diametre_id and attr_pmp_diametre_id > 0:
                try:
                    attr_list.append(AllplanBaseElements.AttributeInteger(attr_pmp_diametre_id, 25))
                except:
                    attr_list.append(AllplanBaseElements.AttributeString(attr_pmp_diametre_id, "25"))

            # pmp_seccio: 25 (AttributeInt o AttributeString según el tipo)
            if attr_pmp_seccio_id and attr_pmp_seccio_id > 0:
                try:
                    attr_list.append(AllplanBaseElements.AttributeInteger(attr_pmp_seccio_id, 25))
                except:
                    attr_list.append(AllplanBaseElements.AttributeString(attr_pmp_seccio_id, "25"))

        except Exception as e:
            # No bloquear la creación si hay problemas con los atributos
            print(f"[TubPvcBasicF25] Advertencia al agregar atributos de usuario: {e}")

    def _add_copy_attributes(self, attr_list, idx):
        """Agrega atributos a las copias según el índice.

        Args:
            attr_list: Lista de atributos donde agregar
            idx: Índice de la copia (1 o 2)
        """
        if not self.doc:
            print(f"[F25][SCRIPT][ATTR] copia_{idx}: doc=None, no se pueden resolver IDs")
            return

        try:
            # Obtener ID de 6_CC_IS (siempre necesario para copias)
            attr_6_cc_is_id = AllplanBaseElements.AttributeService.GetAttributeID(self.doc, "6_CC_IS")

            if attr_6_cc_is_id and attr_6_cc_is_id > 0:
                attr_list.append(AllplanBaseElements.AttributeString(attr_6_cc_is_id, "IS"))
                print(
                    f"[F25][SCRIPT][ATTR] copia_{idx}: set 6_CC_IS(id={attr_6_cc_is_id})='IS'"
                )
            else:
                print(f"[F25][SCRIPT][ATTR] copia_{idx}: 6_CC_IS id no encontrado")

            # Para la segunda copia (idx == 2), agregar Material = CAVITAT
            if idx == 2:
                attr_material_id = AllplanBaseElements.AttributeService.GetAttributeID(self.doc, "Material")
                if attr_material_id and attr_material_id > 0:
                    attr_list.append(AllplanBaseElements.AttributeString(attr_material_id, "CAVITAT"))
                    print(
                        f"[F25][SCRIPT][ATTR] copia_{idx}: set Material(id={attr_material_id})='CAVITAT'"
                    )
                else:
                    print(f"[F25][SCRIPT][ATTR] copia_{idx}: Material id no encontrado")

        except Exception as e:
            # No bloquear la creación si hay problemas con los atributos
            print(f"[TubPvcBasicF25] Advertencia al agregar atributos a copia {idx}: {e}")


# ===== Punto de entrada estándar de PythonPart =====
def _create_element(rot_x=180.0, rot_y=0.0, rot_z=0.0, doc=None) -> CreateElementResult:
    """Instancia la clase y delega la creación del elemento. Permite rotar sobre eje x, y, z."""
    return TuboPVCBasico(None, doc, rot_x, rot_y, rot_z).create_result()


# --- Clase Principal del PythonPart ---
class TubPvcBasicF25Script(BaseScriptObject):
    """PythonPart: tubo PVC fecal Ø25 (modelo básico)."""

    def __init__(
        self, build_ele: BuildingElement, script_object_data: BaseScriptObjectData
    ):
        super().__init__(script_object_data)
        self.build_ele = build_ele
        self.doc = self.coord_input.GetInputViewDocument()

    def get_attributes(self, *args, **kwargs):
        return []

    def execute(self, *args, **kwargs) -> CreateElementResult:
        """Ejecuta la creación del tubo PVC básico Ø25."""
        rot_x = kwargs.get("rot_x", args[0] if len(args) > 0 else 180.0)
        rot_y = kwargs.get("rot_y", args[1] if len(args) > 1 else 0.0)
        rot_z = kwargs.get("rot_z", args[2] if len(args) > 2 else 0.0)
        # doc   = kwargs.get("doc",   args[3] if len(args) > 3 else None)
        return _create_element(rot_x, rot_y, rot_z, self.doc)
