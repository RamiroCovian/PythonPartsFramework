from BaseScriptObject import BaseScriptObject, BaseScriptObjectData
from BuildingElement import BuildingElement
from CreateElementResult import CreateElementResult
import NemAll_Python_BaseElements as AllplanBaseElements
from NemAll_Python_BaseElements import AttributeService

from Instalaciones.GeometryTools.create_smart_geo import CreateSmartGeo

_COLOR_NAME_MAP: dict[int, str] = {
    13: "Marró",
}

# Dimensiones del tubo encapsulado TD
_COLOR_INNER = 13   # mismo que IS luz retorno / paralelas
_COLOR_OUTER = 4    # recubrimiento XPS
_OUTER_EXTRA = 5.0  # mm que sobresale el recubrimiento


# --- Funciones de PythonPart Requeridas ---
def check_allplan_version(build_ele, version):
    return True


def create_preview(build_ele, script_object_data):
    """Genera la vista previa del PythonPart (simplificada)."""
    geo_tools = CreateSmartGeo()
    desc = {
        "bases": [
            {"type": "cubo", "length": 1000.0, "width": 20.0, "height": 20.0,
             "base_point": (0, 0, 0), "color": _COLOR_INNER, "operations": []},
            {"type": "cubo", "length": 1000.0, "width": 20.0, "height": 20.0 + _OUTER_EXTRA,
             "base_point": (0, 0, 0), "color": _COLOR_OUTER, "operations": []},
        ]
    }
    model_ele_list = geo_tools.build_from_description(desc)
    return model_ele_list, []


def create_script_object(build_ele, script_object_data):
    return ConductoLuzRetornoParalelasTdScript(build_ele, script_object_data)


# --- Clase Principal del PythonPart ---
class ConductoLuzRetornoParalelasTdScript(BaseScriptObject):
    """PythonPart para conducto Luz Retorno / Paralelas TD (encapsulado XPS)."""

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
            user_attributes.append(AllplanBaseElements.AttributeString(attr_ids["pmp_CARTICULO"], "KN02_004_002"))
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
            user_attributes.append(AllplanBaseElements.AttributeString(attr_ids["pmp_tipus_cablejat"], "1,5M + 1,5B + 1,5TT"))
            user_attributes.append(AllplanBaseElements.AttributeString(attr_ids["pmp_volteig"], ""))
        except Exception:
            pass
        return user_attributes

    def get_attributes(self, value=None, tipo=None, color=0, overlap_mm=0.0):
        diameter = float(value) if value else 20.0
        attr_list = []
        custom_attributes = self.get_attributes_custom(value=value, tipo=tipo, color=color, overlap_mm=overlap_mm)
        user_attributes = self.get_attributes_user(diameter=diameter, color=color)
        attr_list.extend(custom_attributes)
        attr_list.extend(user_attributes)
        return attr_list

    def get_attributes_custom(self, value: float = 0, tipo: str | None = None,
                              color: int = 0, overlap_mm: float = 0.0) -> list:
        attr_list = []
        try:
            diameter = float(value) if value else 20.0
            area = diameter ** 2
            color_name = _COLOR_NAME_MAP.get(color, "")

            if tipo:
                attr_list.append(AllplanBaseElements.AttributeString(1086, tipo))

            attr_list.append(AllplanBaseElements.AttributeString(1895, color_name))
            attr_list.append(AllplanBaseElements.AttributeString(1896, str(int(diameter))))
            attr_list.append(AllplanBaseElements.AttributeString(1898, str(int(area))))
            attr_list.append(AllplanBaseElements.AttributeString(1899, "0"))

        except Exception as e:
            print(f"[LuzRetornoParalelasTD] Error en get_attributes_custom: {e}")
        return attr_list

    def execute(self, diameter=None) -> CreateElementResult:
        length = 1000.0
        width = float(diameter) if diameter else 20.0
        height = float(diameter) if diameter else 20.0
        geo_tools = CreateSmartGeo()
        desc = {
            "bases": [
                {"type": "cubo", "length": length, "width": width, "height": height,
                 "base_point": (0, 0, 0), "color": _COLOR_INNER, "operations": []},
                {"type": "cubo", "length": length, "width": width, "height": height + _OUTER_EXTRA,
                 "base_point": (0, 0, 0), "color": _COLOR_OUTER, "operations": []},
            ]
        }
        model_ele_list = geo_tools.build_from_description(desc)
        return CreateElementResult(model_ele_list)
