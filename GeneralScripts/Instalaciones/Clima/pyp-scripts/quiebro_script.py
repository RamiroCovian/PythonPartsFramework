from __future__ import annotations

import importlib
from types import SimpleNamespace

from BaseScriptObject import BaseScriptObject, BaseScriptObjectData
from BuildingElement import BuildingElement
from CreateElementResult import CreateElementResult

class _Param:
    def __init__(self, value):
        self.value = value


class QuiebroScript(BaseScriptObject):
    def __init__(self, build_ele: BuildingElement, script_object_data: BaseScriptObjectData):
        super().__init__(script_object_data)
        self.build_ele = build_ele
        self.doc = self.coord_input.GetInputViewDocument()

    def get_attributes(self, *args, **kwargs):
        return []

    def execute(self, *args, **kwargs) -> CreateElementResult:
        quiebro_mod = importlib.import_module(f"{__package__}.Quiebro")
        QuiebroModel = getattr(quiebro_mod, "QuiebroModel")

        installation_type = str(kwargs.get("installation_type", "Retorn"))
        diameter = str(kwargs.get("diameter", "150x150"))
        length_mm = kwargs.get("length_mm", None)

        # QuiebroModel lee parámetros de build_ele; aquí creamos un proxy mínimo.
        proxy = SimpleNamespace()
        proxy.TypeQuiebro = _Param(installation_type)
        proxy.TypeQuiebroRetorn = _Param(diameter)
        proxy.TypeQuiebroImpulsió = _Param(diameter)

        model = QuiebroModel(proxy, self.doc)
        if length_mm is not None:
            # Importante:
            # QuiebroModel.set_length() modifica también LEN_X/ARM_LEN_X (además del custom_length),
            # y LEN_X en este modelo afecta a la "anchura" (no solo a la longitud).
            # Para evitar deformaciones, solo dejamos variar la longitud a través de custom_length.
            try:
                model.custom_length = float(length_mm)
                # El atributo usado por el label/propiedades
                model.param["LONG. QUIEBRO"] = str(int(float(length_mm)))
            except Exception:
                pass

        model_ele_list = model.build()
        return CreateElementResult(model_ele_list)

