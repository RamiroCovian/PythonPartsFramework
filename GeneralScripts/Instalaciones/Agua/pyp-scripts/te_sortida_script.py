from BaseScriptObject import BaseScriptObject, BaseScriptObjectData
from BuildingElement import BuildingElement
from CreateElementResult import CreateElementResult
import NemAll_Python_Utility as PythonUtility

from .te_sortida_004 import TeSortidaModel


def check_allplan_version(_build_ele, version) -> bool:
    return True


def create_script_object(build_ele, script_object_data):
    return TeSortidaScript(build_ele, script_object_data)


# --- Clase Principal del PythonPart ---
class TeSortidaScript(BaseScriptObject):
    """Clase principal del PythonPart que modela una te sortida."""

    def __init__(
        self, build_ele: BuildingElement, script_object_data: BaseScriptObjectData
    ):
        super().__init__(script_object_data)
        self.build_ele = build_ele
        self.doc = self.coord_input.GetInputViewDocument()

    def get_attributes(self, value: int = 0):

        attr_list = []
        return attr_list

    def execute(self, *args, **kwargs) -> CreateElementResult:
        """
        Ejecuta la creación de la te de salida.
        Acepta parámetros opcionales desde la polilínea:
        - diameter: diámetro elegido (20, 25, 32, ...)
        - dist_type: tipo de distribución ("IS" o "TD")
        - water_type: tipo de agua ("Fred", "Calent", etc.) – reservado para futura ampliación
        """
        # Mantener compatibilidad con llamadas antiguas que pasaban solo dist_type/diameter por nombre
        diameter = args[0] if args else kwargs.get("diameter")
        dist_type = kwargs.get("dist_type")
        water_type = kwargs.get("water_type")

        # TODO: usar diameter para ajustar realmente la geometría del modelo TeSortidaModel
        # cuando se defina el mapeo de diámetros a parámetros del modelo.

        model_ele_list = None
        if dist_type == "IS":
            PythonUtility.ShowMessageBox(
                "Este tipo de te sortida no existe o no está disponible para la distribución IS.",
                PythonUtility.MB_OK,
            )
            return CreateElementResult([])
        else:
            te_sortida = TeSortidaModel(self.build_ele, self.doc)
            model_ele_list = te_sortida.build()

        return CreateElementResult(model_ele_list)
