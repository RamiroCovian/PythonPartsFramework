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
    model_ele_list = conducto_3D.create_conducto_geometry_3D(color=19)

    return model_ele_list, []


def create_script_object(build_ele, script_object_data):
    return ConductoRecuperadorScript(build_ele, script_object_data)


# --- Clase Principal del PythonPart ---
class ConductoRecuperadorScript(BaseScriptObject):
    """Clase principal del PythonPart que modela un difusor."""

    def __init__(self, build_ele: BuildingElement, script_object_data: BaseScriptObjectData):
        super().__init__(script_object_data)
        self.build_ele = build_ele
        self.doc = self.coord_input.GetInputViewDocument()

    def get_attributes_custom(self):
        custom_attributes = []

        try:
            custom_attributes.append(AllplanBaseElements.AttributeString(1083, "TV"))
            custom_attributes.append(AllplanBaseElements.AttributeString(1947, ""))
        except Exception:
            pass

        return custom_attributes

    def get_attributes_user(self):
        user_attributes = []
        # Inicialización de IDs
        self.attr_6_cc_is_id = AttributeService.GetAttributeID(self.doc, "6_CC_IS")
        self.attr_pmp_pare_id = AttributeService.GetAttributeID(self.doc, "pmp_pare")

        # Value assignment for attributeID
        user_attributes.append(AllplanBaseElements.AttributeString(self.attr_6_cc_is_id, "IS"))
        user_attributes.append(AllplanBaseElements.AttributeString(self.attr_pmp_pare_id, ""))

        return user_attributes

    def get_attributes(self, value=None, *args, **kwargs):
        attr_list = []
        custom_attributes = self.get_attributes_custom()
        user_attributes = self.get_attributes_user()

        attr_list.extend(custom_attributes)
        attr_list.extend(user_attributes)
        return attr_list

    def execute(self, *args, **kwargs) -> CreateElementResult:
        conducto_3D = ConductoObject3D()

        build_ele_length = getattr(self.build_ele, "Length", None)
        length = build_ele_length.value if build_ele_length else 1000
        witdh = 160.0
        height = 160.0

        model_ele_list = conducto_3D.create_conducto_geometry_3D(
            length=length, witdh=witdh, height=height, color=19
        )

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
