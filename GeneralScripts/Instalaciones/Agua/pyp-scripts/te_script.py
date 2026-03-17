from BaseScriptObject import BaseScriptObject, BaseScriptObjectData
from BuildingElement import BuildingElement
from CreateElementResult import CreateElementResult
from .te_003_is import TeModel
from .te_003_td import TeTDModel


def check_allplan_version(_build_ele, version) -> bool:
    return True


def create_script_object(build_ele, script_object_data):
    return TeScript(build_ele, script_object_data)


class TeScript(BaseScriptObject):
    """Clase principal del PythonPart que modela una te."""

    def __init__(
        self, build_ele: BuildingElement, script_object_data: BaseScriptObjectData
    ):
        super().__init__(script_object_data)
        self.build_ele = build_ele
        self.doc = self.coord_input.GetInputViewDocument()

    def get_attributes(self, value: int = 0):
        attr_list = []
        return attr_list

    def execute(self, dist_type=None) -> CreateElementResult:
        if dist_type == "IS":
            te = TeModel(self.build_ele, self.doc)
            model_ele_list = te.build()
        else:
            te = TeTDModel(self.build_ele, self.doc)
            model_ele_list = te.build()

        return CreateElementResult(model_ele_list)
