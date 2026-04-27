import NemAll_Python_BaseElements as AllplanBaseElements

from BaseScriptObject import BaseScriptObject, BaseScriptObjectData
from BuildingElement import BuildingElement
from CreateElementResult import CreateElementResult
from NemAll_Python_BaseElements import AttributeService

from .codo_90_3D import Codo90Object3D

# --- Funciones de PythonPart Requeridas ---
def check_allplan_version(build_ele, version):
    return True

def create_preview(build_ele, script_object_data):
    """Genera la vista previa del PythonPart (simplificada)."""
    codo_90_3d = Codo90Object3D()
    model_ele_list = codo_90_3d.create_codo_90_geometry_3D()

    return model_ele_list, []

def create_script_object(build_ele, script_object_data):
    return Codo90Script(build_ele, script_object_data)


# --- Clase Principal del PythonPart ---
class Codo90Script(BaseScriptObject):
    """Clase principal del PythonPart que modela un difusor."""

    def __init__(
        self, build_ele: BuildingElement, script_object_data: BaseScriptObjectData
    ):
        super().__init__(script_object_data)
        self.build_ele = build_ele
        self.doc = self.coord_input.GetInputViewDocument()

    def get_attributes_custom(self):
        custom_attributes = []
        try:
            # Value assignment for attributeID
            custom_attributes.append(AllplanBaseElements.AttributeString(1083, "COLZE Ø160/90º"))  # Custom attribute 01
            custom_attributes.append(AllplanBaseElements.AttributeString(1084, "Ø160/90º"))
            custom_attributes.append(AllplanBaseElements.AttributeString(1085, ""))
            custom_attributes.append(AllplanBaseElements.AttributeString(1086, ""))
            custom_attributes.append(AllplanBaseElements.AttributeString(1087, ""))
            custom_attributes.append(AllplanBaseElements.AttributeString(1895, ""))
            custom_attributes.append(AllplanBaseElements.AttributeString(1896, ""))
            custom_attributes.append(AllplanBaseElements.AttributeString(1897, ""))
            custom_attributes.append(AllplanBaseElements.AttributeString(1898, ""))
            custom_attributes.append(AllplanBaseElements.AttributeString(1899, ""))
            custom_attributes.append(AllplanBaseElements.AttributeString(1900, ""))
            custom_attributes.append(AllplanBaseElements.AttributeString(1901, ""))
            custom_attributes.append(AllplanBaseElements.AttributeString(1902, ""))
            custom_attributes.append(AllplanBaseElements.AttributeString(1903, ""))
            custom_attributes.append(AllplanBaseElements.AttributeString(1904, ""))
        except Exception:
            pass

        return custom_attributes

    def get_attributes_user(self):
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
            user_attributes.append(AllplanBaseElements.AttributeString(self.attr_6_cc_is_id, ""))
            user_attributes.append(AllplanBaseElements.AttributeString(self.attr_pmp_altura_id, ""))
            user_attributes.append(AllplanBaseElements.AttributeString(self.attr_pmp_amplada_id, ""))
            user_attributes.append(AllplanBaseElements.AttributeDouble(self.attr_pmp_area_id, 0.0))
            user_attributes.append(AllplanBaseElements.AttributeString(self.attr_pmp_armaflex_id, ""))
            user_attributes.append(AllplanBaseElements.AttributeString(self.attr_pmp_cargols_id, ""))
            user_attributes.append(AllplanBaseElements.AttributeString(self.attr_pmp_carticul_id, "KN04_007_004"))
            user_attributes.append(AllplanBaseElements.AttributeString(self.attr_pmp_color_id, ""))
            user_attributes.append(AllplanBaseElements.AttributeDouble(self.attr_pmp_densitat_id, 0.0))
            user_attributes.append(AllplanBaseElements.AttributeDouble(self.attr_pmp_densitat_lineal_id, 0.0))
            user_attributes.append(AllplanBaseElements.AttributeDouble(self.attr_pmp_densitat_superfici_id, 0.0))
            user_attributes.append(AllplanBaseElements.AttributeDouble(self.attr_pmp_diametre_id, 0.0))
            user_attributes.append(AllplanBaseElements.AttributeString(self.attr_pmp_longitud_id, ""))
            user_attributes.append(AllplanBaseElements.AttributeDouble(self.attr_pmp_longitud_extra_id, 0.0))
            user_attributes.append(AllplanBaseElements.AttributeString(self.attr_pmp_nom_id, "COLZE Ø160/90º"))
            user_attributes.append(AllplanBaseElements.AttributeString(self.attr_pmp_pare_id, ""))
            user_attributes.append(AllplanBaseElements.AttributeDouble(self.attr_pmp_pes_unitari_id, 0.0))
            user_attributes.append(AllplanBaseElements.AttributeString(self.attr_pmp_seccio_id, "Ø160/90º"))
            user_attributes.append(AllplanBaseElements.AttributeString(self.attr_pmp_tipus_id, ""))
            user_attributes.append(AllplanBaseElements.AttributeString(self.attr_pmp_tipus_cablejat_id, ""))
            user_attributes.append(AllplanBaseElements.AttributeString(self.attr_pmp_volteig_id, ""))
        except Exception:
            pass

        return user_attributes

    def get_attributes(self,  *args, **kwargs):
        attr_list = []
        custom_attributes = self.get_attributes_custom()
        user_attributes = self.get_attributes_user()

        attr_list.extend(custom_attributes)
        attr_list.extend(user_attributes)
        return attr_list

    def execute(self,  *args, **kwargs) -> CreateElementResult:
        codo_90_3d = Codo90Object3D()
        model_ele_list = codo_90_3d.create_codo_90_geometry_3D()

        list_new = []
        attr_list = self.get_attributes()
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

