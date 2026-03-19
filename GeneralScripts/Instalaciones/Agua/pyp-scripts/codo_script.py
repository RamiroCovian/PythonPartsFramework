from BaseScriptObject import BaseScriptObject, BaseScriptObjectData
from BuildingElement import BuildingElement
from CreateElementResult import CreateElementResult

from .colze_001_is import ColzeModel
from .colze_001_td import ColzeTDModel


def check_allplan_version(_build_ele, version) -> bool:
    return True


def create_script_object(build_ele, script_object_data):
    return CodoScript(build_ele, script_object_data)


class CodoScript(BaseScriptObject):
    """Clase principal del PythonPart que modela un codo."""

    def __init__(
        self, build_ele: BuildingElement, script_object_data: BaseScriptObjectData
    ):
        super().__init__(script_object_data)
        self.build_ele = build_ele
        self.doc = self.coord_input.GetInputViewDocument()

    def get_attributes(self, *args, **kwargs):
        """
        Devuelve los atributos por defecto del modelo de codo (IS/TD).
        """
        dist_type = kwargs.get("dist_type")
        if dist_type not in ("IS", "TD"):
            dist_type = "IS"

        try:
            elbow = (
                ColzeModel(self.build_ele, self.doc)
                if dist_type == "IS"
                else ColzeTDModel(self.build_ele, self.doc)
            )
            create_attrs = getattr(elbow, "_create_attributes", None)
            if callable(create_attrs):
                attrs = create_attrs()
                if attrs:
                    return [attrs]
        except Exception:
            pass

        return []

    def execute(self, dist_type=None) -> CreateElementResult:
        if dist_type == "IS":
            elbow = ColzeModel(self.build_ele, self.doc)
            model_ele_list = elbow.build()
        else:
            elbow = ColzeTDModel(self.build_ele, self.doc)
            model_ele_list = elbow.build()

        return CreateElementResult(model_ele_list)
