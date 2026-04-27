import NemAll_Python_BaseElements as AllplanBaseElements

from BaseScriptObject import BaseScriptObject, BaseScriptObjectData
from BuildingElement import BuildingElement
from CreateElementResult import CreateElementResult
from NemAll_Python_BaseElements import AttributeService

from .manguito_3D import MenguitoObject3D


# --- Funciones de PythonPart Requeridas ---
def check_allplan_version(build_ele, version):
    return True

def create_preview(build_ele, script_object_data):
    """Genera la vista previa del PythonPart (simplificada)."""
    difusor_3d = MenguitoObject3D()
    model_ele_list = difusor_3d.create_manguito_geometry_3D()

    return model_ele_list, []

def create_script_object(build_ele, script_object_data):
    return ManguitoScript(build_ele, script_object_data)


# --- Clase Principal del PythonPart ---
class ManguitoScript(BaseScriptObject):
    """Clase principal del PythonPart que modela un difusor."""

    def __init__(
        self, build_ele: BuildingElement, script_object_data: BaseScriptObjectData
    ):
        super().__init__(script_object_data)
        self.build_ele = build_ele
        self.doc = self.coord_input.GetInputViewDocument()

    def get_attributes_user(self):
        user_attributes = []
        try:
            attr_6_cc_is = "6_CC_IS"
            attr_pmp_pare = "pmp_pare"

            attr_6_cc_is_id = AttributeService.GetAttributeID(self.doc, attr_6_cc_is)
            attr_pmp_pare_id = AttributeService.GetAttributeID(self.doc, attr_pmp_pare)

            user_attributes.append(AllplanBaseElements.AttributeString(attr_6_cc_is_id, ""))
            user_attributes.append(AllplanBaseElements.AttributeString(attr_pmp_pare_id, ""))
        except Exception:
            pass

        return user_attributes

    def get_attributes(self, *args, **kwargs):
        attr_list = []
        user_attributes = self.get_attributes_user()

        attr_list.extend(user_attributes)
        return attr_list

    def execute(self, *args, **kwargs) -> CreateElementResult:
        manguito_3d = MenguitoObject3D()
        model_ele_list = manguito_3d.create_manguito_geometry_3D()

        return CreateElementResult(model_ele_list)

