from BaseScriptObject import BaseScriptObject, BaseScriptObjectData
from BuildingElement import BuildingElement
from CreateElementResult import CreateElementResult
import NemAll_Python_BaseElements as AllplanBaseElements
from NemAll_Python_BaseElements import AttributeService

from .conducto_3D import ConductoObject3D

_COLOR_NAME_MAP: dict[int, str] = {
    16: "Negre",
}


def check_allplan_version(build_ele, version):
    return True


def create_preview(build_ele, script_object_data):
    conducto_3D = ConductoObject3D()
    model_ele_list = conducto_3D.create_conducto_geometry_3D(color=16)
    return model_ele_list, []


def create_script_object(build_ele, script_object_data):
    return ConductoAlimentacionLucesCajetinesScript(build_ele, script_object_data)


class ConductoAlimentacionLucesCajetinesScript(BaseScriptObject):
    """PythonPart para conducto Alimentación luces / Cajetines (corrugados)."""

    def __init__(self, build_ele: BuildingElement, script_object_data: BaseScriptObjectData):
        super().__init__(script_object_data)
        self.build_ele = build_ele
        self.doc = self.coord_input.GetInputViewDocument()

    def get_attributes_user(self, diameter: float = 20.0, color: int = 0) -> list:
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

            area = float(diameter) ** 2
            color_name = _COLOR_NAME_MAP.get(color, "")

            user_attributes.append(AllplanBaseElements.AttributeString(attr_ids["6_CC_IS"], ""))
            user_attributes.append(AllplanBaseElements.AttributeString(attr_ids["pmp_altura"], ""))
            user_attributes.append(AllplanBaseElements.AttributeString(attr_ids["pmp_amplada"], ""))
            user_attributes.append(AllplanBaseElements.AttributeString(attr_ids["pmp_area"], str(int(area))))
            user_attributes.append(AllplanBaseElements.AttributeString(attr_ids["pmp_armaflex"], ""))
            user_attributes.append(AllplanBaseElements.AttributeString(attr_ids["pmp_cargols"], ""))
            user_attributes.append(AllplanBaseElements.AttributeString(attr_ids["pmp_CARTICULO"], "KN02_004_001"))
            user_attributes.append(AllplanBaseElements.AttributeString(attr_ids["pmp_color"], color_name))
            user_attributes.append(AllplanBaseElements.AttributeDouble(attr_ids["pmp_densitat"], 0.0))
            user_attributes.append(AllplanBaseElements.AttributeDouble(attr_ids["pmp_densitat_lineal"], 0.29))
            user_attributes.append(AllplanBaseElements.AttributeDouble(attr_ids["pmp_densitat_superficial"], 0.0))
            user_attributes.append(AllplanBaseElements.AttributeString(attr_ids["pmp_diametre"], str(int(diameter))))
            user_attributes.append(AllplanBaseElements.AttributeString(attr_ids["pmp_longitud"], ""))
            user_attributes.append(AllplanBaseElements.AttributeDouble(attr_ids["pmp_longitud_extra"], 0.0))
            user_attributes.append(AllplanBaseElements.AttributeString(attr_ids["pmp_nom"], ""))
            user_attributes.append(AllplanBaseElements.AttributeString(attr_ids["pmp_pare"], ""))
            user_attributes.append(AllplanBaseElements.AttributeDouble(attr_ids["pmp_pes_unitari"], 0.0))
            user_attributes.append(AllplanBaseElements.AttributeString(attr_ids["pmp_seccio"], ""))
            user_attributes.append(AllplanBaseElements.AttributeString(attr_ids["pmp_tipus"], ""))
            user_attributes.append(AllplanBaseElements.AttributeString(attr_ids["pmp_tipus_cablejat"], "1,5N + 1,5B + 1,5 TT"))
            user_attributes.append(AllplanBaseElements.AttributeString(attr_ids["pmp_volteig"], ""))
        except Exception:
            pass
        return user_attributes

    def get_attributes(self, value=None, tipo=None, color=0, overlap_mm=0.0):
        diameter = float(value) if value else 20.0
        attr_list = []
        custom_attributes = self.get_attributes_custom(
            value=value,
            tipo=tipo,
            color=color,
            overlap_mm=overlap_mm,
        )
        user_attributes = self.get_attributes_user(diameter=diameter, color=color)
        attr_list.extend(custom_attributes)
        attr_list.extend(user_attributes)
        return attr_list

    def get_attributes_custom(self, value: float = 0, tipo: str | None = None,
                              color: int = 0, overlap_mm: float = 0.0) -> list:
        """
        Atributos técnicos del conducto (Atributo personalizado):
          04 → Tipo derivado del layer: CORRUGATS SOBRE REJIBAND / D'ENTRADA / DE SORTIDA
          06 → Color del cable (nombre, p.ej. "Negre")
          07 → Diámetro nominal (mm)
          09 → Área sección (mm²) = diámetro²
          10 → Longitud extra / solape (mm)
        El attr01 (Nom;0) lo construye el hook desde so.applied_attributes.
        """
        attr_list = []
        try:
            diameter = float(value) if value else 20.0
            area = diameter ** 2
            color_name = _COLOR_NAME_MAP.get(color, "")

            if tipo:
                id_attr04 = AttributeService.GetAttributeID(
                    self.doc, "Atributo personalizado 04"
                )
                if id_attr04 and id_attr04 > 0:
                    attr_list.append(AllplanBaseElements.AttributeString(id_attr04, tipo))

            id_attr06 = AttributeService.GetAttributeID(
                self.doc, "Atributo personalizado 06"
            )
            if id_attr06 and id_attr06 > 0:
                attr_list.append(AllplanBaseElements.AttributeString(id_attr06, color_name))

            id_attr07 = AttributeService.GetAttributeID(
                self.doc, "Atributo personalizado 07"
            )
            if id_attr07 and id_attr07 > 0:
                attr_list.append(AllplanBaseElements.AttributeString(id_attr07, str(int(diameter))))

            id_attr09 = AttributeService.GetAttributeID(
                self.doc, "Atributo personalizado 09"
            )
            if id_attr09 and id_attr09 > 0:
                attr_list.append(AllplanBaseElements.AttributeString(id_attr09, str(int(area))))

            id_attr10 = AttributeService.GetAttributeID(
                self.doc, "Atributo personalizado 10"
            )
            if id_attr10 and id_attr10 > 0:
                attr_list.append(AllplanBaseElements.AttributeString(id_attr10, "0"))

        except Exception as e:
            print(f"[AlimentacionLucesCajetines] Error en get_attributes_custom: {e}")
        return attr_list

    def execute(self, diameter=None) -> CreateElementResult:
        conducto_3D = ConductoObject3D()
        selec_color = 16
        length = 1000.0
        width = diameter if diameter else 20.0
        height = diameter if diameter else 20.0
        model_ele_list = conducto_3D.create_conducto_geometry_3D(
            length=length, witdh=width, height=height, color=selec_color
        )
        return CreateElementResult(model_ele_list)

