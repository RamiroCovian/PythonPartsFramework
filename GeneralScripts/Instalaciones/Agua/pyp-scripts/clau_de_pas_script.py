from BaseScriptObject import BaseScriptObject, BaseScriptObjectData
from BuildingElement import BuildingElement
from CreateElementResult import CreateElementResult
import NemAll_Python_Utility as PythonUtility

from .clau_de_pas_006 import ClauDePasModel


def check_allplan_version(_build_ele, version) -> bool:
    return True


def create_preview(build_ele, script_object_data):
    """Vista previa simplificada para el file-based loader."""
    from .clau_de_pas_006 import create_preview as _model_preview

    return _model_preview(build_ele, None), []


# --- Clase Principal del PythonPart ---
class ClauDePasScript(BaseScriptObject):
    """Clase principal del PythonPart que modela un clau de pas."""

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
        Ejecuta la creación del clau de pas.
        Acepta parámetros opcionales desde la polilínea:
        - diameter: diámetro elegido (20, 25, 32, ...)
        - dist_type: tipo de distribución ("IS" o "TD")
        - water_type: tipo de agua ("Fred", "Calent", etc.) – reservado para futura ampliación
        """
        # Mantener compatibilidad con llamadas antiguas que pasaban solo dist_type/diameter por nombre
        diameter = args[0] if args else kwargs.get("diameter")
        dist_type = kwargs.get("dist_type")
        water_type = kwargs.get("water_type")

        # TODO: usar diameter para mapear a TipoClaudePas (CPØ20, CPØ25, ...)
        # cuando se defina el mapeo exacto desde la polilínea.

        if dist_type == "IS":
            PythonUtility.ShowMessageBox(
                "Este tipo de clau de pas no existe o no está disponible para la distribución IS.",
                PythonUtility.MB_OK,
            )
            return CreateElementResult([])
        clau = ClauDePasModel(self.build_ele, self.doc)
        model_ele_list = clau.build()

        return CreateElementResult(model_ele_list)
