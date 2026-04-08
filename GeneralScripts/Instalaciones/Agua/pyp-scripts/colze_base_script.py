from BaseScriptObject import BaseScriptObject, BaseScriptObjectData
from BuildingElement import BuildingElement
from CreateElementResult import CreateElementResult
import NemAll_Python_Utility as PythonUtility

from .colze_base_002 import ColzeBaseModel


def check_allplan_version(_build_ele, version) -> bool:
    return True


def create_preview(build_ele, script_object_data):
    """Vista previa simplificada para el file-based loader."""
    from .colze_base_002 import create_preview as _model_preview

    return _model_preview(build_ele, None), []


def create_script_object(build_ele, script_object_data):
    return ColzeBaseScript(build_ele, script_object_data)


# --- Clase Principal del PythonPart ---
class ColzeBaseScript(BaseScriptObject):
    """Clase principal del PythonPart que modela un colze base."""

    def __init__(
        self, build_ele: BuildingElement, script_object_data: BaseScriptObjectData
    ):
        super().__init__(script_object_data)
        self.build_ele = build_ele
        self.doc = self.coord_input.GetInputViewDocument()

    def get_attributes(self, value: int = 0):

        attr_list = []
        return attr_list

    def execute(self, diameter=None, dist_type=None) -> CreateElementResult:
        # aqui tenes que usar el diametro que llega para generar el 3D en width y height
        # tenes que tratar de no usar self.param .. hacerlo mas dinamico
        model_ele_list = None
        if dist_type == "IS":
            PythonUtility.ShowMessageBox(
                "Este tipo de colze base no existe o no está disponible para la distribución IS.",
                PythonUtility.MB_OK,
            )
            return CreateElementResult([])
        else:
            colze_base = ColzeBaseModel(self.build_ele, self.doc)
            model_ele_list = colze_base.build()

        return CreateElementResult(model_ele_list)
