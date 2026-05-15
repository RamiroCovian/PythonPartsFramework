# -*- coding: utf-8 -*-
# pylint: disable=import-error,broad-exception-caught
from BaseScriptObject import BaseScriptObject, BaseScriptObjectData
from BuildingElement import BuildingElement
from CreateElementResult import CreateElementResult
import NemAll_Python_BaseElements as AllplanBaseElements
from NemAll_Python_BaseElements import AttributeService

from .rejiband_u_3D import RejibandUObject3D


def check_allplan_version(build_ele, version):
    return True


def create_preview(build_ele, script_object_data):
    """Vista previa simplificada."""
    obj = RejibandUObject3D()
    model_ele_list = obj.create_rejiband_u_geometry_3d()
    return model_ele_list, []


def create_script_object(build_ele, script_object_data):
    return RejibandUScript(build_ele, script_object_data)


class RejibandUScript(BaseScriptObject):
    """
    Rejiband U (MVP2).

    Nota: el largo real lo ajusta el motor de la polilínea (GeometryHandler) según el tramo.
    Aquí devolvemos un "template" orientado en X.
    """
    def __init__(self, build_ele: BuildingElement, script_object_data: BaseScriptObjectData):
        super().__init__(script_object_data)
        self.build_ele = build_ele
        self.doc = self.coord_input.GetInputViewDocument()

    def _get_height(self) -> float:
        try:
            return float(
                getattr(getattr(self.build_ele, "RejibandHeight", None), "value", 50) or 50
            )
        except Exception:
            return 50.0

    def get_attributes_user(self, width: float = 100.0, height: float = 50.0) -> list:
        user_attributes = []
        try:
            attr_ids = {
                "6_CC_IS":                 AttributeService.GetAttributeID(self.doc, "6_CC_IS"),
                "pmp_altura":              AttributeService.GetAttributeID(self.doc, "pmp_altura"),
                "pmp_amplada":             AttributeService.GetAttributeID(self.doc, "pmp_amplada"),
                "pmp_area":                AttributeService.GetAttributeID(self.doc, "pmp_area"),
                "pmp_armaflex":            AttributeService.GetAttributeID(self.doc, "pmp_armaflex"),
                "pmp_cargols":             AttributeService.GetAttributeID(self.doc, "pmp_cargols"),
                "pmp_CARTICULO":           AttributeService.GetAttributeID(self.doc, "pmp_CARTICULO"),
                "pmp_color":               AttributeService.GetAttributeID(self.doc, "pmp_color"),
                "pmp_densitat":            AttributeService.GetAttributeID(self.doc, "pmp_densitat"),
                "pmp_densitat_lineal":     AttributeService.GetAttributeID(self.doc, "pmp_densitat_lineal"),
                "pmp_densitat_superficial": AttributeService.GetAttributeID(self.doc, "pmp_densitat_superficial"),
                "pmp_diametre":            AttributeService.GetAttributeID(self.doc, "pmp_diametre"),
                "pmp_longitud":            AttributeService.GetAttributeID(self.doc, "pmp_longitud"),
                "pmp_longitud_extra":      AttributeService.GetAttributeID(self.doc, "pmp_longitud_extra"),
                "pmp_nom":                 AttributeService.GetAttributeID(self.doc, "pmp_nom"),
                "pmp_pare":                AttributeService.GetAttributeID(self.doc, "pmp_pare"),
                "pmp_pes_unitari":         AttributeService.GetAttributeID(self.doc, "pmp_pes_unitari"),
                "pmp_seccio":              AttributeService.GetAttributeID(self.doc, "pmp_seccio"),
                "pmp_tipus":               AttributeService.GetAttributeID(self.doc, "pmp_tipus"),
                "pmp_tipus_cablejat":      AttributeService.GetAttributeID(self.doc, "pmp_tipus_cablejat"),
                "pmp_volteig":             AttributeService.GetAttributeID(self.doc, "pmp_volteig"),
            }

            area = width * height
            seccio = f"{int(width)}x{int(height)}"

            user_attributes.append(AllplanBaseElements.AttributeString(attr_ids["6_CC_IS"], ""))
            user_attributes.append(AllplanBaseElements.AttributeString(attr_ids["pmp_altura"], str(int(height))))
            user_attributes.append(AllplanBaseElements.AttributeString(attr_ids["pmp_amplada"], str(int(width))))
            user_attributes.append(AllplanBaseElements.AttributeString(attr_ids["pmp_area"], str(int(area))))
            user_attributes.append(AllplanBaseElements.AttributeString(attr_ids["pmp_armaflex"], ""))
            user_attributes.append(AllplanBaseElements.AttributeString(attr_ids["pmp_cargols"], ""))
            user_attributes.append(AllplanBaseElements.AttributeString(attr_ids["pmp_CARTICULO"], ""))
            user_attributes.append(AllplanBaseElements.AttributeString(attr_ids["pmp_color"], ""))
            user_attributes.append(AllplanBaseElements.AttributeDouble(attr_ids["pmp_densitat"], 0.0))
            user_attributes.append(AllplanBaseElements.AttributeDouble(attr_ids["pmp_densitat_lineal"], 0.0))
            user_attributes.append(AllplanBaseElements.AttributeDouble(attr_ids["pmp_densitat_superficial"], 0.0))
            user_attributes.append(AllplanBaseElements.AttributeDouble(attr_ids["pmp_diametre"], width))
            user_attributes.append(AllplanBaseElements.AttributeString(attr_ids["pmp_longitud"], ""))
            user_attributes.append(AllplanBaseElements.AttributeDouble(attr_ids["pmp_longitud_extra"], 0.0))
            user_attributes.append(AllplanBaseElements.AttributeString(attr_ids["pmp_nom"], ""))
            user_attributes.append(AllplanBaseElements.AttributeString(attr_ids["pmp_pare"], ""))
            user_attributes.append(AllplanBaseElements.AttributeDouble(attr_ids["pmp_pes_unitari"], 0.0))
            user_attributes.append(AllplanBaseElements.AttributeString(attr_ids["pmp_seccio"], seccio))
            user_attributes.append(AllplanBaseElements.AttributeString(attr_ids["pmp_tipus"], ""))
            user_attributes.append(AllplanBaseElements.AttributeString(attr_ids["pmp_tipus_cablejat"], ""))
            user_attributes.append(AllplanBaseElements.AttributeString(attr_ids["pmp_volteig"], ""))
        except Exception:
            pass
        return user_attributes

    def get_attributes(self, value=None, tipo=None, color=0, overlap_mm=0.0):
        width = float(value) if value else 100.0
        height = self._get_height()
        attr_list = []
        custom_attributes = self.get_attributes_custom(
            value=value,
            tipo=tipo,
            color=color,
            overlap_mm=overlap_mm,
        )
        user_attributes = self.get_attributes_user(width=width, height=height)
        attr_list.extend(custom_attributes)
        attr_list.extend(user_attributes)
        return attr_list

    def get_attributes_custom(self, value: float = 0, tipo: str | None = None,
                              color: int = 0, overlap_mm: float = 0.0) -> list:
        """
        Atributos técnicos del Rejiband U:
          02 → Dimensiones (p.ej. "100x50")
          09 → Área sección nominal (mm²) = ancho × alto
          11 → Ancho (mm)
        El attr01 (Nombre) lo construye el hook desde so.applied_attributes.
        """
        attr_list = []
        try:
            width = float(value) if value else 100.0
            height = self._get_height()
            area = width * height

            attr_list.append(AllplanBaseElements.AttributeString(1084, f"{int(width)}x{int(height)}"))
            attr_list.append(AllplanBaseElements.AttributeString(1898, str(int(area))))
            attr_list.append(AllplanBaseElements.AttributeDouble(1900, width))

        except Exception as e:
            print(f"[RejibandU] Error en get_attributes_custom: {e}")
        return attr_list

    def execute(self, diameter=None, length: float = 1000.0) -> CreateElementResult:
        obj = RejibandUObject3D()

        build_ele_diameter = getattr(self.build_ele, "Diameter", None)
        get_diameter = str(build_ele_diameter.value).split(" ")[0] if build_ele_diameter else 100.0
        selected_diameter = int(get_diameter)

        width = selected_diameter if not diameter else diameter

        try:
            thickness = float(getattr(getattr(self.build_ele, "RejibandThickness", None), "value", 4) or 4)
        except Exception:
            thickness = 4.0
        try:
            height = float(getattr(getattr(self.build_ele, "RejibandHeight", None), "value", 50) or 50)
        except Exception:
            height = 50.0

        color = 1

        model_ele_list = obj.create_rejiband_u_geometry_3d(
            length=float(length or 1000.0),
            width=width,
            height=height,
            thickness=thickness,
            color=color,
        )
        return CreateElementResult(model_ele_list)
