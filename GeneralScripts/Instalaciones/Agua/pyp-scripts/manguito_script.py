from BaseScriptObject import BaseScriptObject, BaseScriptObjectData
from BuildingElement import BuildingElement
from CreateElementResult import CreateElementResult

from .manguito_005_is import ManguitoModel
from .manguito_005_td import ManguitoTDModel


def check_allplan_version(_build_ele, version) -> bool:
    return True


def create_script_object(build_ele, script_object_data):
    return ManguitoScript(build_ele, script_object_data)


class ManguitoScript(BaseScriptObject):
    """Clase principal del PythonPart que modela un manguito."""

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
        Ejecuta la creación del manguito.
        Acepta parámetros opcionales desde la polilínea:
        - diameter: diámetro elegido (20, 25, 32, ...)
        - dist_type: tipo de distribución ("IS" o "TD")
        - water_type: tipo de agua ("Fred", "Calent", etc.) – reservado para futura ampliación
        """
        # Mantener compatibilidad con llamadas antiguas que pasaban solo dist_type por nombre
        dist_type = kwargs.get("dist_type")
        diameter = args[0] if args else kwargs.get("diameter")
        water_type = kwargs.get("water_type")

        # De momento los modelos ManguitoModel / ManguitoTDModel no usan aún
        # diameter ni water_type, pero dejamos la firma preparada.
        if dist_type == "IS":
            mangui = ManguitoModel(self.build_ele, self.doc)
            model_ele_list = mangui.build()
        else:
            mangui = ManguitoTDModel(self.build_ele, self.doc)
            model_ele_list = mangui.build()

        return CreateElementResult(model_ele_list)
