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

    def execute(self, *args, **kwargs) -> CreateElementResult:
        """
        Ejecuta la creación de la te.
        Acepta parámetros opcionales desde la polilínea:
        - diameter: diámetro elegido (20, 25, 32, ...)
        - dist_type: tipo de distribución ("IS" o "TD")
        - water_type: tipo de agua ("Fred", "Calent", etc.) – reservado para futura ampliación
        """
        # Mantener compatibilidad con llamadas antiguas que pasaban solo dist_type por nombre
        dist_type = kwargs.get("dist_type")
        diameter = args[0] if args else kwargs.get("diameter")
        water_type = kwargs.get("water_type")

        # De momento los modelos TeModel / TeTDModel no usan aún diameter ni water_type,
        # pero dejamos la firma preparada.
        if dist_type == "IS":
            te = TeModel(self.build_ele, self.doc)
            model_ele_list = te.build()
        else:
            te = TeTDModel(self.build_ele, self.doc)
            model_ele_list = te.build()

        return CreateElementResult(model_ele_list)
