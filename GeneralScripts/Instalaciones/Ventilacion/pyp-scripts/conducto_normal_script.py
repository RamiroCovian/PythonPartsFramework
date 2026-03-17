import NemAll_Python_BaseElements as AllplanBaseElements

from BaseScriptObject import BaseScriptObject, BaseScriptObjectData
from BuildingElement import BuildingElement
from CreateElementResult import CreateElementResult
from NemAll_Python_BaseElements import AttributeService

from .conducto_3D import ConductoObject3D


# --- Funciones de PythonPart Requeridas ---
def check_allplan_version(build_ele, version):
    return True


def create_preview(build_ele, script_object_data):
    """Genera la vista previa del PythonPart (simplificada)."""
    conducto_3D = ConductoObject3D()
    model_ele_list = conducto_3D.create_conducto_geometry_3D(color=5)

    return model_ele_list, []


def create_script_object(build_ele, script_object_data):
    return ConductoNormalScript(build_ele, script_object_data)


# --- Clase Principal del PythonPart ---
class ConductoNormalScript(BaseScriptObject):
    """Clase principal del PythonPart que modela un difusor."""

    def __init__(self, build_ele: BuildingElement, script_object_data: BaseScriptObjectData):
        super().__init__(script_object_data)
        self.build_ele = build_ele
        self.doc = self.coord_input.GetInputViewDocument()

    def get_attributes_custom(self):
        custom_attributes = []

        try:
            # Value assignment for attributeID
            custom_attributes.append(AllplanBaseElements.AttributeString(1083, "TV"))
            custom_attributes.append(AllplanBaseElements.AttributeString(1084, ""))
            custom_attributes.append(AllplanBaseElements.AttributeString(1085, ""))
            custom_attributes.append(AllplanBaseElements.AttributeString(1086, ""))
            custom_attributes.append(AllplanBaseElements.AttributeString(1087, ""))
            custom_attributes.append(AllplanBaseElements.AttributeString(1895, ""))
            custom_attributes.append(AllplanBaseElements.AttributeString(1896, "75"))
            custom_attributes.append(AllplanBaseElements.AttributeString(1897, ""))
            custom_attributes.append(AllplanBaseElements.AttributeString(1898, "5625"))
            custom_attributes.append(AllplanBaseElements.AttributeString(1899, ""))
            custom_attributes.append(AllplanBaseElements.AttributeString(1900, ""))
            custom_attributes.append(AllplanBaseElements.AttributeString(1901, ""))
            custom_attributes.append(AllplanBaseElements.AttributeString(1902, ""))
            custom_attributes.append(AllplanBaseElements.AttributeString(1903, ""))
            custom_attributes.append(AllplanBaseElements.AttributeString(1904, ""))
            custom_attributes.append(AllplanBaseElements.AttributeString(1947, ""))
        except Exception:
            pass

        return custom_attributes

    def get_attributes_user(self, color = None):
        user_attributes = []

        try:
            # Inicialización de IDs
            self.attr_6_cc_is_id = AttributeService.GetAttributeID(self.doc, "6_CC_IS")
            self.attr_pmp_altura_id = AttributeService.GetAttributeID(self.doc, "pmp_altura")
            self.attr_pmp_amplada_id = AttributeService.GetAttributeID(self.doc, "pmp_amplada")
            self.attr_pmp_area_id = AttributeService.GetAttributeID(self.doc, "pmp_area")
            self.attr_pmp_armaflex_id = AttributeService.GetAttributeID(self.doc, "pmp_armaflex")
            self.attr_pmp_cargols_id = AttributeService.GetAttributeID(self.doc, "pmp_cargols")
            self.attr_pmp_carticul_id = AttributeService.GetAttributeID(self.doc, "pmp_CARTICULO")
            self.attr_pmp_color_id = AttributeService.GetAttributeID(self.doc, "pmp_color")
            self.attr_pmp_densitat_id = AttributeService.GetAttributeID(self.doc, "pmp_densitat")
            self.attr_pmp_densitat_lineal_id = AttributeService.GetAttributeID(self.doc, "pmp_densitat_lineal")
            self.attr_pmp_densitat_superfici_id = AttributeService.GetAttributeID(self.doc, "pmp_densitat_superficial")
            self.attr_pmp_diametre_id = AttributeService.GetAttributeID(self.doc, "pmp_diametre")
            self.attr_pmp_longitud_id = AttributeService.GetAttributeID(self.doc, "pmp_longitud")
            self.attr_pmp_longitud_extra_id = AttributeService.GetAttributeID(self.doc, "pmp_longitud_extra")
            self.attr_pmp_nom_id = AttributeService.GetAttributeID(self.doc, "pmp_nom")
            self.attr_pmp_pare_id = AttributeService.GetAttributeID(self.doc, "pmp_pare")
            self.attr_pmp_pes_unitari_id = AttributeService.GetAttributeID(self.doc, "pmp_pes_unitari")
            self.attr_pmp_seccio_id = AttributeService.GetAttributeID(self.doc, "pmp_seccio")
            self.attr_pmp_tipus_id = AttributeService.GetAttributeID(self.doc, "pmp_tipus")
            self.attr_pmp_tipus_cablejat_id = AttributeService.GetAttributeID(self.doc, "pmp_tipus_cablejat")
            self.attr_pmp_volteig_id = AttributeService.GetAttributeID(self.doc, "pmp_volteig")

            # Value assignment for attributeID
            user_attributes.append(AllplanBaseElements.AttributeString(self.attr_6_cc_is_id, "IS08"))
            user_attributes.append(AllplanBaseElements.AttributeString(self.attr_pmp_altura_id, ""))
            user_attributes.append(AllplanBaseElements.AttributeString(self.attr_pmp_amplada_id, ""))
            user_attributes.append(AllplanBaseElements.AttributeDouble(self.attr_pmp_area_id, 5625.0))
            user_attributes.append(AllplanBaseElements.AttributeString(self.attr_pmp_armaflex_id, ""))
            user_attributes.append(AllplanBaseElements.AttributeString(self.attr_pmp_cargols_id, ""))
            if color == 5:
                user_attributes.append(AllplanBaseElements.AttributeString(self.attr_pmp_carticul_id, "KN04_001-002"))
            elif color == 15:
                user_attributes.append(AllplanBaseElements.AttributeString(self.attr_pmp_carticul_id, "KN04_001-001"))
            user_attributes.append(AllplanBaseElements.AttributeString(self.attr_pmp_color_id, ""))
            user_attributes.append(AllplanBaseElements.AttributeDouble(self.attr_pmp_densitat_id, 0.0))
            user_attributes.append(AllplanBaseElements.AttributeDouble(self.attr_pmp_densitat_lineal_id, 0.2227))
            user_attributes.append(AllplanBaseElements.AttributeDouble(self.attr_pmp_densitat_superfici_id, 0.0))
            user_attributes.append(AllplanBaseElements.AttributeDouble(self.attr_pmp_diametre_id, 75.0))
            user_attributes.append(AllplanBaseElements.AttributeString(self.attr_pmp_longitud_id, ""))
            user_attributes.append(AllplanBaseElements.AttributeDouble(self.attr_pmp_longitud_extra_id, 0.0))
            user_attributes.append(AllplanBaseElements.AttributeString(self.attr_pmp_nom_id, ""))
            user_attributes.append(AllplanBaseElements.AttributeString(self.attr_pmp_pare_id, ""))
            user_attributes.append(AllplanBaseElements.AttributeDouble(self.attr_pmp_pes_unitari_id, 0.0))
            user_attributes.append(AllplanBaseElements.AttributeString(self.attr_pmp_seccio_id, ""))
            user_attributes.append(AllplanBaseElements.AttributeString(self.attr_pmp_tipus_id, ""))
            user_attributes.append(AllplanBaseElements.AttributeString(self.attr_pmp_tipus_cablejat_id, ""))
            user_attributes.append(AllplanBaseElements.AttributeString(self.attr_pmp_volteig_id, ""))
        except Exception:
            pass

        return user_attributes

    def get_attributes(self, *args, **kwargs):

        value = kwargs.get("value") or (args[0] if args else 0)

        attr_list = []
        custom_attributes = self.get_attributes_custom()
        user_attributes = self.get_attributes_user(color=value)

        attr_list.extend(custom_attributes)
        attr_list.extend(user_attributes)
        return attr_list

    def execute(self, *args, **kwargs) -> CreateElementResult:
        conducto_3D = ConductoObject3D()

        build_ele_color = getattr(self.build_ele, "Color", None)
        build_ele_length = getattr(self.build_ele, "Length", None)

        get_color = str(build_ele_color.value).split(",")[1] if build_ele_color else 5
        selec_color = int(get_color)

        length = build_ele_length.value if build_ele_length else 1000
        witdh = 75.0
        height = 75.0

        model_ele_list = conducto_3D.create_conducto_geometry_3D(
            length=length, witdh=witdh, height=height, color=selec_color
        )

        list_new = []
        attr_list = self.get_attributes(value=selec_color)
        if attr_list:
            for model_elem in model_ele_list:
                attr_set_list = []
                attr_set_list.append(AllplanBaseElements.AttributeSet(attr_list))
                attributes = AllplanBaseElements.Attributes(attr_set_list)
                model_elem.SetAttributes(attributes)
                list_new.append(model_elem)
        else:
            list_new.extend(model_ele_list)

        return CreateElementResult(list_new)
