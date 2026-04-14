# -*- coding: utf-8 -*-
# pylint: disable=import-error,broad-exception-caught
from BaseScriptObject import BaseScriptObject, BaseScriptObjectData
from BuildingElement import BuildingElement
from CreateElementResult import CreateElementResult

from .caixa_connexions_200_3D import CaixaConnexions200Object3D


def check_allplan_version(build_ele, version):
    return True


def create_preview(build_ele, script_object_data):
    """Vista previa simplificada."""
    obj = CaixaConnexions200Object3D()
    model_ele_list = obj.create_geometry_3d()
    return model_ele_list, []


def create_script_object(build_ele, script_object_data):
    return CaixaConnexions200Script(build_ele, script_object_data)


class CaixaConnexions200Script(BaseScriptObject):
    """Caixa connexions 200 - Elemento estatico."""

    def __init__(
        self, build_ele: BuildingElement, script_object_data: BaseScriptObjectData
    ):
        super().__init__(script_object_data)
        self.build_ele = build_ele

    def execute(self) -> CreateElementResult:
        obj = CaixaConnexions200Object3D()

        try:
            length = float(getattr(getattr(self.build_ele, "Length", None), "value", 200) or 200)
        except Exception:
            length = 200.0
        try:
            width = float(getattr(getattr(self.build_ele, "Width", None), "value", 45) or 45)
        except Exception:
            width = 45.0
        try:
            height = float(getattr(getattr(self.build_ele, "Height", None), "value", 130) or 130)
        except Exception:
            height = 130.0
        try:
            hole_diameter = float(getattr(getattr(self.build_ele, "HoleDiameter", None), "value", 20) or 20)
        except Exception:
            hole_diameter = 20.0

        color = 1

        model_ele_list = obj.create_geometry_3d(
            length=length,
            width=width,
            height=height,
            hole_diameter=hole_diameter,
            color=color,
        )
        return CreateElementResult(model_ele_list)
